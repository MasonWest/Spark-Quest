"""Purpose routing and scoring checks against isolated in-memory databases."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.database import Base
from app.models import CourseLevel, Lesson, QuizQuestion, QuizAnswerLog, LessonMastery
from app.l2_question_bank import catalog, seed_reviewed_bank, questions_for_phase
from app.routers import quizzes, review
from app.schemas import QuizSubmitIn, ReviewSubmitIn


class ReviewedBankTests(unittest.TestCase):
    def setUp(self):
        self.engine=create_engine('sqlite://')
        Base.metadata.create_all(self.engine)
        self.db=Session(self.engine)
        level=CourseLevel(title='L2 fixture',order_index=2)
        self.db.add(level);self.db.flush()
        for i,entry in enumerate(catalog()):
            self.db.add(Lesson(level_id=level.id,title=entry['lesson_slug'],slug=entry['lesson_slug'],order_index=i))
        self.db.flush()
        self.first=self.db.scalar(select(Lesson).order_by(Lesson.order_index))
        self.legacy=QuizQuestion(lesson_id=self.first.id,prompt='Legacy question, retained',options='["a","b","c","d"]',correct_index=1,order_index=0)
        self.db.add(self.legacy);self.db.commit()

    def tearDown(self):
        self.db.close();self.engine.dispose()

    def test_additive_idempotent_seed_and_rollback(self):
        old_id=self.legacy.id
        self.assertEqual(seed_reviewed_bank(self.db),100)
        self.db.rollback()
        self.assertEqual(self.db.scalar(select(func.count()).select_from(QuizQuestion)),1)
        self.assertEqual(seed_reviewed_bank(self.db),100);self.db.commit()
        self.assertEqual(seed_reviewed_bank(self.db),0)
        self.assertEqual(self.db.get(QuizQuestion,old_id).prompt,'Legacy question, retained')

    def test_all_lessons_have_disjoint_five_question_pools(self):
        seed_reviewed_bank(self.db);self.db.commit()
        for lesson in self.db.scalars(select(Lesson)).all():
            qs=self.db.scalars(select(QuizQuestion).where(QuizQuestion.lesson_id==lesson.id)).all()
            a=questions_for_phase(lesson.slug,qs,'assessment');r=questions_for_phase(lesson.slug,qs,'review')
            self.assertEqual(len(a),5);self.assertEqual(len(r),5)
            self.assertFalse({q.id for q in a}&{q.id for q in r})
            with patch.object(quizzes,'compute_lesson_status',return_value='available'):
                output=quizzes.get_quiz(lesson.id,self.db)
            self.assertEqual({q.id for q in output.questions},{q.id for q in a})
            self.assertTrue(all('correct_index' not in q.model_dump() for q in output.questions))

    def test_thresholds_history_and_invalid_short_submit(self):
        seed_reviewed_bank(self.db);self.db.commit()
        with patch.object(quizzes,'compute_lesson_status',return_value='available'):
            fetch=quizzes.get_quiz(self.first.id,self.db)
            answers=[dict(question_id=q.id,selected_index=self.db.get(QuizQuestion,q.id).correct_index) for q in fetch.questions]
            with self.assertRaises(HTTPException):
                quizzes.submit_quiz(self.first.id,QuizSubmitIn(answers=answers[:4]),self.db)
            self.assertEqual(self.db.scalar(select(func.count()).select_from(QuizAnswerLog)),0)
            answers[-1]['selected_index']=(answers[-1]['selected_index']+1)%4
            result=quizzes.submit_quiz(self.first.id,QuizSubmitIn(answers=answers),self.db)
            self.assertEqual(result.score,80);self.assertTrue(result.passed)
            self.assertEqual(result.status,'mastered')
        fetched=review.get_review(self.first.id,self.db)
        self.assertFalse({q.id for q in fetched.questions}&{q.id for q in fetch.questions})
        review_answers=[dict(question_id=q.id,selected_index=self.db.get(QuizQuestion,q.id).correct_index) for q in fetched.questions]
        review_answers[-1]['selected_index']=(review_answers[-1]['selected_index']+1)%4
        failed=review.submit_review(self.first.id,ReviewSubmitIn(answers=review_answers),self.db)
        self.assertFalse(failed.passed)
        self.assertEqual(self.db.scalar(select(LessonMastery)).status,'mastered')
        review_answers[-1]['selected_index']=self.db.get(QuizQuestion,review_answers[-1]['question_id']).correct_index
        passed=review.submit_review(self.first.id,ReviewSubmitIn(answers=review_answers),self.db)
        self.assertTrue(passed.passed)
        self.assertEqual(self.db.get(QuizQuestion,self.legacy.id).prompt,'Legacy question, retained')

    def test_missing_bank_fails_closed_other_levels_unchanged(self):
        with self.assertRaises(ValueError):questions_for_phase(self.first.slug,[self.legacy],'assessment')
        self.assertEqual(questions_for_phase('l3-any',[self.legacy],'assessment'),[self.legacy])

    def test_inflight_legacy_five_questions_remain_gradable_and_mastery_sticky(self):
        seed_reviewed_bank(self.db)
        old=[self.legacy]
        for i in range(4):
            q=QuizQuestion(lesson_id=self.first.id,prompt=f'Legacy inflight {i}',options='["a","b","c","d"]',correct_index=1,order_index=i+1)
            self.db.add(q);old.append(q)
        self.db.commit()
        with patch.object(quizzes,'compute_lesson_status',return_value='available'):
            result=quizzes.submit_quiz(self.first.id,QuizSubmitIn(answers=[dict(question_id=q.id,selected_index=1) for q in old]),self.db)
            self.assertTrue(result.passed)
            failed=quizzes.submit_quiz(self.first.id,QuizSubmitIn(answers=[dict(question_id=q.id,selected_index=0) for q in old]),self.db)
            self.assertFalse(failed.passed);self.assertEqual(failed.status,'mastered')

    def test_authoring_is_reproducible(self):
        from author_l2_assessment import build
        authored=json.loads((Path(__file__).parent/'app/l2_reviewed_bank.json').read_text(encoding='utf-8'))
        self.assertEqual(build(),authored)

    def test_authored_content_structure_and_nonidentical_variants(self):
        keys=set();prompts=set()
        for entry in catalog():
            content=[]
            for q in entry['questions']:
                self.assertNotIn(q['key'],keys);keys.add(q['key'])
                self.assertNotIn(q['prompt'],prompts);prompts.add(q['prompt'])
                self.assertEqual(len(q['options']),4);self.assertEqual(len(set(q['options'])),4)
                self.assertIn(q['correct_index'],range(4))
                content.append(q['prompt'].split('：',1)[1])
            self.assertEqual(len(set(content)),10)


if __name__=='__main__':unittest.main()
