"""Isolated migration, cold-seed, real schema and unlock-chain regressions."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from sqlalchemy import create_engine,select,func
from sqlalchemy.orm import Session
from app import database
from app.database import Base
from app.models import CourseLevel,Lesson,QuizQuestion,LessonMastery,LessonNote
from app.course_extensions import apply_extensions
from app.reviewed_question_bank import seed_reviewed_bank,questions_for_phase
from app.services import compute_lesson_status
from app.routers.lessons import get_lesson

ROOT=Path(__file__).parent
NEW={'l3-window-topn','l7-cache-lifecycle'}
SEED=json.loads((ROOT/'app/course_seed.json').read_text(encoding='utf-8'))


class ExtensionTests(unittest.TestCase):
    def setUp(self):
        self.engine=create_engine('sqlite://');Base.metadata.create_all(self.engine);self.db=Session(self.engine)
    def tearDown(self):self.db.close();self.engine.dispose()
    def seed_old(self):
        for lv in SEED['levels']:
            level=CourseLevel(**{k:v for k,v in lv.items() if k!='lessons'});self.db.add(level);self.db.flush()
            for i,item in enumerate(l for l in lv['lessons'] if l['slug'] not in NEW):
                fields=dict(item,order_index=i,content=json.dumps(item['content'],ensure_ascii=False))
                lesson=Lesson(level_id=level.id,**fields);self.db.add(lesson);self.db.flush()
                self.db.add(QuizQuestion(lesson_id=lesson.id,prompt='Unchanged old '+lesson.slug,options='["a","b","c","d"]',correct_index=2,order_index=0))
        anchor=self.db.scalar(select(Lesson).where(Lesson.slug=='l3-groupby-having'))
        self.db.add(LessonMastery(lesson_id=anchor.id,status='mastered',score=80))
        self.db.add(LessonNote(lesson_id=anchor.id,content='Keep my note'));self.db.commit()
    def test_upgrade_rollback_ids_and_idempotence(self):
        self.seed_old()
        old={l.id:{c.name:getattr(l,c.name) for c in Lesson.__table__.columns if c.name!='order_index'} for l in self.db.scalars(select(Lesson))}
        qs={q.id:q.prompt for q in self.db.scalars(select(QuizQuestion))}
        result=apply_extensions(self.db);self.assertEqual(len(result['lessons_added']),2);self.assertEqual(result['questions_added'],20)
        self.db.rollback();self.assertEqual(self.db.scalar(select(func.count()).select_from(Lesson)),66)
        apply_extensions(self.db);self.db.commit()
        for ident,fields in old.items():self.assertEqual({k:getattr(self.db.get(Lesson,ident),k) for k in fields},fields)
        self.assertEqual({i:self.db.get(QuizQuestion,i).prompt for i in qs},qs)
        self.assertEqual(self.db.scalar(select(LessonNote)).content,'Keep my note')
        again=apply_extensions(self.db);self.assertEqual(again,dict(lessons_added=[],order_updated=[],questions_added=0))
    def test_order_unlock_and_old_mastery(self):
        self.seed_old();apply_extensions(self.db);self.db.commit()
        new=self.db.scalar(select(Lesson).where(Lesson.slug=='l3-window-topn'))
        following=self.db.scalar(select(Lesson).where(Lesson.slug=='l3-joins-intro'))
        self.assertEqual(compute_lesson_status(new,self.db),'available')
        self.assertEqual(compute_lesson_status(following,self.db),'locked')
        self.db.add(LessonMastery(lesson_id=following.id,status='mastered',score=100));self.db.commit()
        self.assertEqual(compute_lesson_status(following,self.db),'mastered')
        self.assertEqual(get_lesson(new.id,self.db).next_lesson.id,following.id)
        for slug in NEW:
            lesson=self.db.scalar(select(Lesson).where(Lesson.slug==slug));detail=get_lesson(lesson.id,self.db)
            self.assertEqual(len(detail.content.examples),8)
            self.assertIn('【先用人话理解】',detail.content.explanation)
    def test_purpose_pools_and_schema(self):
        self.seed_old();apply_extensions(self.db);self.db.commit()
        for slug in NEW:
            lesson=self.db.scalar(select(Lesson).where(Lesson.slug==slug))
            qs=self.db.scalars(select(QuizQuestion).where(QuizQuestion.lesson_id==lesson.id)).all()
            a=questions_for_phase(slug,qs,'assessment');r=questions_for_phase(slug,qs,'review')
            self.assertEqual(len(a),5);self.assertEqual(len(r),5);self.assertFalse({q.id for q in a}&{q.id for q in r})
            self.assertEqual({q.correct_index for q in a},set(range(4)))
            self.assertEqual({q.correct_index for q in r},set(range(4)))
    def test_order_and_new_content_drift_rejected(self):
        self.seed_old();anchor=self.db.scalar(select(Lesson).where(Lesson.slug=='l3-groupby-having'));anchor.order_index=999;self.db.flush()
        with self.assertRaises(ValueError):apply_extensions(self.db)
        self.db.rollback();apply_extensions(self.db);self.db.commit()
        lesson=self.db.scalar(select(Lesson).where(Lesson.slug=='l7-cache-lifecycle'));lesson.content='{}';self.db.flush()
        with self.assertRaises(ValueError):apply_extensions(self.db)
    def test_cold_seed_keeps_legacy_661_questions(self):
        with patch.object(database,'engine',self.engine):
            database._seed_course_data()
            apply_extensions(self.db);self.db.commit()
            database._seed_quizzes()
        self.assertEqual(self.db.scalar(select(func.count()).select_from(Lesson)),68)
        self.assertEqual(self.db.scalar(select(func.count()).select_from(QuizQuestion)),681)
        seed_reviewed_bank(self.db);self.db.commit()
        self.assertEqual(self.db.scalar(select(func.count()).select_from(QuizQuestion)),1291)
        self.assertEqual(seed_reviewed_bank(self.db),0)


if __name__=='__main__':unittest.main()
