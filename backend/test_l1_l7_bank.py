"""Isolated tests for all 15 new purpose-separated lesson pools."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.database import Base
from app.models import CourseLevel, Lesson, QuizQuestion, QuizAnswerLog, LessonMastery, DEFAULT_USER_ID
from app.reviewed_question_bank import extra_catalog as all_extra_catalog, seed_reviewed_bank, questions_for_phase

def extra_catalog():
    return [entry for entry in all_extra_catalog() if entry["lesson_slug"].startswith(("l1-","l7-"))]
from app.routers import quizzes, review
from app.schemas import QuizSubmitIn, ReviewSubmitIn


class BankTests(unittest.TestCase):
    def setUp(self):
        self.engine=create_engine('sqlite://');Base.metadata.create_all(self.engine);self.db=Session(self.engine)
        level=CourseLevel(title='L1-L7 fixture',order_index=3);self.db.add(level);self.db.flush()
        for i,entry in enumerate(extra_catalog()):
            lesson=Lesson(level_id=level.id,title=entry['lesson_slug'],slug=entry['lesson_slug'],order_index=i)
            self.db.add(lesson);self.db.flush()
            self.db.add(QuizQuestion(lesson_id=lesson.id,prompt='Legacy '+lesson.slug,options='["a","b","c","d"]',correct_index=1,order_index=0))
        self.db.commit();self.first=self.db.scalar(select(Lesson).order_by(Lesson.order_index))
    def tearDown(self):
        self.db.close();self.engine.dispose()
    def test_additive_rollback_and_idempotence(self):
        old={q.id:q.prompt for q in self.db.scalars(select(QuizQuestion))}
        self.assertEqual(seed_reviewed_bank(self.db),150);self.db.rollback()
        self.assertEqual(self.db.scalar(select(func.count()).select_from(QuizQuestion)),15)
        self.assertEqual(seed_reviewed_bank(self.db),150);self.db.commit();self.assertEqual(seed_reviewed_bank(self.db),0)
        self.assertEqual({i:self.db.get(QuizQuestion,i).prompt for i in old},old)
    def test_all_15_pools_disjoint_and_no_answers_leak(self):
        seed_reviewed_bank(self.db);self.db.commit()
        for lesson in self.db.scalars(select(Lesson)):
            qs=self.db.scalars(select(QuizQuestion).where(QuizQuestion.lesson_id==lesson.id)).all()
            a=questions_for_phase(lesson.slug,qs,'assessment');r=questions_for_phase(lesson.slug,qs,'review')
            self.assertEqual(len(a),5);self.assertEqual(len(r),5)
            self.assertFalse({q.id for q in a}&{q.id for q in r})
            self.assertTrue(all(not q.prompt.startswith('Legacy') for q in a+r))
            with patch.object(quizzes,'compute_lesson_status',return_value='available'):
                actual=quizzes.get_quiz(lesson.id,self.db)
            self.assertEqual({q.id for q in actual.questions},{q.id for q in a})
            self.assertTrue(all('correct_index' not in q.model_dump() and 'explanation' not in q.model_dump() for q in actual.questions))
            self.db.add(LessonMastery(lesson_id=lesson.id,status='mastered',score=80));self.db.commit()
            actual_review=review.get_review(lesson.id,self.db)
            self.assertEqual({q.id for q in actual_review.questions},{q.id for q in r})
            self.assertTrue(all('correct_index' not in q.model_dump() for q in actual_review.questions))
    def test_thresholds_short_submit_and_legacy_compatibility(self):
        seed_reviewed_bank(self.db);self.db.commit()
        with patch.object(quizzes,'compute_lesson_status',return_value='available'):
            fetched=quizzes.get_quiz(self.first.id,self.db)
            answers=[dict(question_id=q.id,selected_index=self.db.get(QuizQuestion,q.id).correct_index) for q in fetched.questions]
            with self.assertRaises(HTTPException):quizzes.submit_quiz(self.first.id,QuizSubmitIn(answers=answers[:4]),self.db)
            self.assertEqual(self.db.scalar(select(func.count()).select_from(QuizAnswerLog)),0)
            answers[-1]['selected_index']=(answers[-1]['selected_index']+1)%4
            result=quizzes.submit_quiz(self.first.id,QuizSubmitIn(answers=answers),self.db)
            self.assertTrue(result.passed);self.assertEqual(result.score,80)
        fetched_review=review.get_review(self.first.id,self.db)
        r=[dict(question_id=q.id,selected_index=self.db.get(QuizQuestion,q.id).correct_index) for q in fetched_review.questions]
        r[-1]['selected_index']=(r[-1]['selected_index']+1)%4
        self.assertFalse(review.submit_review(self.first.id,ReviewSubmitIn(answers=r),self.db).passed)
        r[-1]['selected_index']=self.db.get(QuizQuestion,r[-1]['question_id']).correct_index
        self.assertTrue(review.submit_review(self.first.id,ReviewSubmitIn(answers=r),self.db).passed)
        old=[self.db.scalar(select(QuizQuestion).where(QuizQuestion.lesson_id==self.first.id,QuizQuestion.order_index==0))]
        for i in range(4):
            q=QuizQuestion(lesson_id=self.first.id,prompt=f'Old inflight {i}',options='["a","b","c","d"]',correct_index=1,order_index=i+1);self.db.add(q);old.append(q)
        self.db.commit()
        with patch.object(quizzes,'compute_lesson_status',return_value='available'):
            output=quizzes.submit_quiz(self.first.id,QuizSubmitIn(answers=[dict(question_id=q.id,selected_index=0) for q in old]),self.db)
            self.assertFalse(output.passed);self.assertEqual(output.status,'mastered')
    def test_incomplete_drift_and_other_levels(self):
        qs=self.db.scalars(select(QuizQuestion).where(QuizQuestion.lesson_id==self.first.id)).all()
        with self.assertRaises(ValueError):questions_for_phase(self.first.slug,qs,'assessment')
        self.assertEqual(questions_for_phase('l0-other',qs,'assessment'),qs)
        seed_reviewed_bank(self.db);self.db.commit()
        one=self.db.scalar(select(QuizQuestion).where(QuizQuestion.lesson_id==self.first.id,QuizQuestion.order_index>=200))
        one.explanation='unknown edit';self.db.flush()
        with self.assertRaises(ValueError):seed_reviewed_bank(self.db)
    def test_authored_structure_and_reproducibility(self):
        from author_reviewed_l1_l7 import build
        self.assertEqual(build(),json.loads((Path(__file__).parent/'app/l1_l7_reviewed_bank.json').read_text(encoding='utf-8')))
        keys=set();prompts=set();positions=[0]*4
        for entry in extra_catalog():
            self.assertEqual(len(entry['questions']),10)
            for q in entry['questions']:
                self.assertNotIn(q['key'],keys);keys.add(q['key']);self.assertNotIn(q['prompt'],prompts);prompts.add(q['prompt'])
                self.assertEqual(len(q['options']),4);self.assertEqual(len(set(q['options'])),4);positions[q['correct_index']]+=1
            self.assertEqual(sum(q['purpose']=='assessment' for q in entry['questions']),5)
        self.assertEqual(positions,[38,38,37,37])


if __name__=='__main__':unittest.main()
