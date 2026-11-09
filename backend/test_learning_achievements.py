import unittest
from datetime import datetime,timedelta
from sqlalchemy import create_engine,select,func
from sqlalchemy.orm import Session
from app.database import Base
from app.models import CourseLevel,Lesson,LessonMastery,QuizQuestion,QuizAnswerLog,StudyDay,UserBadge,BadgeDefinition,DEFAULT_USER_ID
from app.learning_achievements import progress
from app.seed_badges import seed_badges
from app.badge_service import evaluate_badges
from app.routers.badges import list_badges

class AchievementTests(unittest.TestCase):
 def setUp(self):
  self.engine=create_engine('sqlite://');Base.metadata.create_all(self.engine);self.db=Session(self.engine,autoflush=False);self.now=datetime(2026,11,9,4)
  for i in range(8):self.db.add(CourseLevel(title=f'L{i}',order_index=i))
  self.db.flush();level=self.db.scalar(select(CourseLevel))
  for i in range(5):self.db.add(Lesson(level_id=level.id,title=str(i),slug=f'lesson-{i}',order_index=i))
  self.db.flush();self.lesson=self.db.scalar(select(Lesson));self.q=QuizQuestion(lesson_id=self.lesson.id,prompt='x',options='["a","b"]',correct_index=0);self.db.add(self.q);self.db.commit()
 def tearDown(self):self.db.close();self.engine.dispose()
 def log(self,correct,at,source='quiz',user=DEFAULT_USER_ID):
  self.db.add(QuizAnswerLog(user_id=user,lesson_id=self.lesson.id,question_id=self.q.id,source=source,selected_index=0,correct_index=0,is_correct=correct,submitted_at=at));self.db.flush()
 def test_repair_24h_distinct_and_source(self):
  self.log(0,self.now-timedelta(days=1));self.log(1,self.now-timedelta(seconds=1));self.assertEqual(progress(self.db,DEFAULT_USER_ID,self.now)['OLD_PIT'],0)
  self.log(1,self.now,'practice');self.assertEqual(progress(self.db,DEFAULT_USER_ID,self.now)['OLD_PIT'],0)
  self.log(1,self.now,'review');self.log(1,self.now,'quiz');self.assertEqual(progress(self.db,DEFAULT_USER_ID,self.now)['REPAIR_CREW'],1)
 def test_other_user_and_future_excluded(self):
  self.log(0,self.now-timedelta(days=2),user='other');self.log(1,self.now);self.log(0,self.now);self.log(1,self.now+timedelta(days=2));self.assertEqual(progress(self.db,DEFAULT_USER_ID,self.now)['OLD_PIT'],0)
 def test_rolling_window_and_return(self):
  for i in [0,2,4,6,8,10,12]:self.db.add(StudyDay(study_date=(self.now.date()-timedelta(days=i)).isoformat(),activity_count=1))
  self.db.flush();p=progress(self.db,DEFAULT_USER_ID,self.now);self.assertEqual(p['STEADY_FIRE'],7);self.assertEqual(p['WELCOME_BACK'],1)
  self.db.add(StudyDay(study_date='2026-10-01',activity_count=1));self.db.flush();self.assertEqual(progress(self.db,DEFAULT_USER_ID,self.now)['WELCOME_BACK'],2)
 def test_natural_day_boundary(self):
  # UTC16:01 is the following local date; future days must not count early.
  self.db.add(StudyDay(study_date='2026-11-10',activity_count=1));self.db.flush()
  self.assertEqual(progress(self.db,DEFAULT_USER_ID,datetime(2026,11,9,15,59))['STEADY_FIRE'],0)
  self.assertEqual(progress(self.db,DEFAULT_USER_ID,datetime(2026,11,9,16,1))['STEADY_FIRE'],1)
 def test_mastery_and_distinct_review_progress(self):
  for l in self.db.scalars(select(Lesson)):
   self.db.add(LessonMastery(lesson_id=l.id,status='mastered',score=80,review_count=3))
  self.db.flush();p=progress(self.db,DEFAULT_USER_ID,self.now);self.assertEqual(p['FIVE_PAGES'],5);self.assertEqual(p['REVIEW_VISITOR'],5);self.assertEqual(p['REVIEW_ECHO'],15)
 def test_seed_preservation_idempotence_and_read_only_get(self):
  seed_badges(self.db);old={b.code:b.id for b in self.db.scalars(select(BadgeDefinition))};self.assertEqual(len(old),28)
  self.db.add(LessonMastery(lesson_id=self.lesson.id,status='mastered',score=80));self.db.flush()
  earned=evaluate_badges(self.db,now=self.now);self.db.commit();self.assertIn('FIRST_SPARK',{b['code'] for b in earned})
  stamps=[(b.badge_id,b.unlocked_at) for b in self.db.scalars(select(UserBadge))]
  self.assertEqual(evaluate_badges(self.db,now=self.now+timedelta(days=1)),[])
  seed_badges(self.db);self.assertEqual({b.code:b.id for b in self.db.scalars(select(BadgeDefinition))},old)
  self.assertEqual([(b.badge_id,b.unlocked_at) for b in self.db.scalars(select(UserBadge))],stamps)
  before=self.db.scalar(select(func.count()).select_from(UserBadge));items=list_badges(self.db)
  self.assertEqual(self.db.scalar(select(func.count()).select_from(UserBadge)),before)
  for b in items:
   self.assertNotEqual(b.action,'/review')
   if b.is_secret and not b.unlocked:self.assertEqual((b.name,b.image,b.goal,b.action),('','',None,''))
 def test_same_quiz_transaction_awards_repaired_question(self):
  from app.routers.quizzes import submit_quiz
  from app.schemas import QuizSubmitIn
  self.log(0,datetime.utcnow()-timedelta(days=2));seed_badges(self.db)
  for i in range(4):self.db.add(QuizQuestion(lesson_id=self.lesson.id,prompt=f'q{i}',options='["a","b"]',correct_index=0))
  self.db.commit()
  qs=self.db.scalars(select(QuizQuestion)).all()
  result=submit_quiz(self.lesson.id,QuizSubmitIn(answers=[dict(question_id=q.id,selected_index=0) for q in qs]),self.db)
  self.assertIn('OLD_PIT',{b.code for b in result.new_badges})

if __name__=='__main__':unittest.main()
