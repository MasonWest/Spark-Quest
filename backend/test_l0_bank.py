"""L0 upgrade regressions, isolated from real learner state."""
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from fastapi import HTTPException
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from app.database import Base
from app.models import CourseLevel, Lesson, LessonMastery, QuizQuestion, QuizAnswerLog, LessonNote
from app.reviewed_question_bank import extra_catalog, seed_reviewed_bank, questions_for_phase
from app.routers import quizzes, review
from app.schemas import QuizSubmitIn, ReviewSubmitIn
from app.services import compute_lesson_status
from audit_question_design import audit

ROOT=Path(__file__).resolve().parent.parent


def catalog():
    return [e for e in extra_catalog() if e['lesson_slug'].startswith('l0-')]


class L0BankTests(unittest.TestCase):
    def setUp(self):
        self.engine=create_engine('sqlite://');Base.metadata.create_all(self.engine)
        self.db=Session(self.engine)
        level=CourseLevel(title='L0',order_index=0);self.db.add(level);self.db.flush()
        for i,entry in enumerate(catalog()):
            lesson=Lesson(level_id=level.id,title=entry['lesson_slug'],slug=entry['lesson_slug'],order_index=i)
            self.db.add(lesson);self.db.flush()
            for j in range(5):
                self.db.add(QuizQuestion(lesson_id=lesson.id,prompt=f'Legacy {i}/{j}',type='single_choice',options='["a","b","c","d"]',correct_index=1,order_index=j))
        self.db.flush()
        self.first=self.db.scalar(select(Lesson).order_by(Lesson.order_index))
        self.db.add(LessonNote(lesson_id=self.first.id,content='Keep this original note'))
        self.db.commit()

    def tearDown(self):
        self.db.close();self.engine.dispose()

    def test_additive_transaction_and_idempotence(self):
        before={q.id:(q.prompt,q.options,q.correct_index,q.order_index) for q in self.db.scalars(select(QuizQuestion))}
        self.assertEqual(seed_reviewed_bank(self.db),50)
        self.db.rollback()
        self.assertEqual(self.db.scalar(select(func.count()).select_from(QuizQuestion)),25)
        self.assertEqual(seed_reviewed_bank(self.db),50);self.db.commit()
        self.assertEqual(seed_reviewed_bank(self.db),0)
        for ident,values in before.items():
            q=self.db.get(QuizQuestion,ident)
            self.assertEqual((q.prompt,q.options,q.correct_index,q.order_index),values)
        self.assertEqual(self.db.scalar(select(LessonNote)).content,'Keep this original note')

    def test_pools_cover_each_lesson_and_hide_answers(self):
        seed_reviewed_bank(self.db);self.db.commit()
        for lesson in self.db.scalars(select(Lesson)):
            qs=self.db.scalars(select(QuizQuestion).where(QuizQuestion.lesson_id==lesson.id)).all()
            a=questions_for_phase(lesson.slug,qs,'assessment');r=questions_for_phase(lesson.slug,qs,'review')
            self.assertEqual(len(a),5);self.assertEqual(len(r),5)
            self.assertFalse({q.id for q in a}&{q.id for q in r})
            with patch.object(quizzes,'compute_lesson_status',return_value='available'):
                response=quizzes.get_quiz(lesson.id,self.db)
            self.assertEqual({q.id for q in response.questions},{q.id for q in a})
            self.assertTrue(all('correct_index' not in q.model_dump() and 'explanation' not in q.model_dump() for q in response.questions))
            self.db.add(LessonMastery(lesson_id=lesson.id,status='mastered',score=80));self.db.commit()
            response=review.get_review(lesson.id,self.db)
            self.assertEqual({q.id for q in response.questions},{q.id for q in r})

    def test_mastery_review_and_legacy_inflight_contract(self):
        seed_reviewed_bank(self.db);self.db.commit()
        response=quizzes.get_quiz(self.first.id,self.db)
        answers=[dict(question_id=q.id,selected_index=self.db.get(QuizQuestion,q.id).correct_index) for q in response.questions]
        with self.assertRaises(HTTPException):quizzes.submit_quiz(self.first.id,QuizSubmitIn(answers=answers[:4]),self.db)
        self.assertEqual(self.db.scalar(select(func.count()).select_from(QuizAnswerLog)),0)
        answers[-1]['selected_index']=(answers[-1]['selected_index']+1)%4
        passed=quizzes.submit_quiz(self.first.id,QuizSubmitIn(answers=answers),self.db)
        self.assertTrue(passed.passed);self.assertEqual(passed.score,80)
        second=self.db.scalar(select(Lesson).where(Lesson.order_index==1))
        self.assertEqual(compute_lesson_status(second,self.db),'available')
        r=review.get_review(self.first.id,self.db)
        answers=[dict(question_id=q.id,selected_index=self.db.get(QuizQuestion,q.id).correct_index) for q in r.questions]
        answers[-1]['selected_index']=(answers[-1]['selected_index']+1)%4
        self.assertFalse(review.submit_review(self.first.id,ReviewSubmitIn(answers=answers),self.db).passed)
        answers[-1]['selected_index']=self.db.get(QuizQuestion,answers[-1]['question_id']).correct_index
        self.assertTrue(review.submit_review(self.first.id,ReviewSubmitIn(answers=answers),self.db).passed)
        legacy=self.db.scalars(select(QuizQuestion).where(QuizQuestion.lesson_id==self.first.id,QuizQuestion.order_index<5)).all()
        result=quizzes.submit_quiz(self.first.id,QuizSubmitIn(answers=[dict(question_id=q.id,selected_index=0) for q in legacy]),self.db)
        self.assertFalse(result.passed);self.assertEqual(result.status,'mastered')

    def test_l0_completion_unlocks_l1(self):
        seed_reviewed_bank(self.db);self.db.commit()
        l0=list(self.db.scalars(select(Lesson).order_by(Lesson.order_index)))
        for lesson in l0[:-1]:
            self.db.add(LessonMastery(lesson_id=lesson.id,status='mastered',score=80))
        level=CourseLevel(title='L1',order_index=1);self.db.add(level);self.db.flush()
        following=Lesson(level_id=level.id,title='RDD',slug='l1-what-is-rdd',order_index=0)
        self.db.add(following);self.db.commit()
        self.assertEqual(compute_lesson_status(following,self.db),'locked')
        fetched=quizzes.get_quiz(l0[-1].id,self.db)
        answers=[dict(question_id=q.id,selected_index=self.db.get(QuizQuestion,q.id).correct_index) for q in fetched.questions]
        result=quizzes.submit_quiz(l0[-1].id,QuizSubmitIn(answers=answers),self.db)
        self.assertTrue(result.passed);self.assertTrue(result.unlocked_next)
        self.assertEqual(result.next_lesson_id,following.id)
        self.assertEqual(compute_lesson_status(following,self.db),'available')

    def test_missing_pool_and_silent_content_edits_rejected(self):
        old=self.db.scalars(select(QuizQuestion).where(QuizQuestion.lesson_id==self.first.id)).all()
        with self.assertRaises(ValueError):questions_for_phase(self.first.slug,old,'assessment')
        seed_reviewed_bank(self.db);self.db.commit()
        one=self.db.scalar(select(QuizQuestion).where(QuizQuestion.lesson_id==self.first.id,QuizQuestion.order_index>=200))
        one.options='["changed","b","c","d"]';self.db.flush()
        with self.assertRaises(ValueError):seed_reviewed_bank(self.db)

    def test_content_coverage_variants_and_reproducibility(self):
        path=ROOT/'frontend/scripts/author-l0-content.py'
        spec=importlib.util.spec_from_file_location('l0_author',path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        lessons,guides,delayed,bank=module.build()
        self.assertEqual(bank,json.loads((ROOT/'backend/app/l0_reviewed_bank.json').read_text(encoding='utf-8')))
        self.assertEqual(len(lessons),5);self.assertEqual(sum(len(l['tasks']) for l in lessons.values()),25)
        self.assertEqual(len(delayed),5);self.assertEqual(len(guides),5)
        prompts=set();keys=set()
        for entry in catalog():
            tasks={t['id'] for t in lessons[entry['lesson_slug']]['tasks']}
            self.assertEqual({q['task_id'] for q in entry['questions']},tasks)
            for q in entry['questions']:
                self.assertNotIn(q['key'],keys);keys.add(q['key'])
                self.assertNotIn(q['prompt'],prompts);prompts.add(q['prompt'])
                self.assertEqual(len(set(q['options'])),4)
            for i in range(0,10,2):
                a,b=entry['questions'][i:i+2]
                self.assertEqual(a['knowledge_id'],b['knowledge_id'])
                self.assertNotEqual(a['prompt'],b['prompt'])
                self.assertNotEqual(sorted(a['options']),sorted(b['options']))
        report=audit()
        for scope in ['formal_by_level','journey_by_level']:
            self.assertLess(report[scope]['l0']['longest_choice_accuracy_pct'],40)
            self.assertLess(report[scope]['l0']['shortest_choice_accuracy_pct'],40)
        self.assertEqual(report['free_response_by_level']['l0'],9)


if __name__=='__main__':unittest.main()
