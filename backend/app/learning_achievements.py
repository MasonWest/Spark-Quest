"""Shared, read-only progress for learning achievements; no new mastery state."""
from datetime import date,datetime,timedelta
from sqlalchemy import select
from .models import LessonMastery,StudyDay,QuizAnswerLog
from .services import local_now

# code, name, condition, group, goal, action, icon
DEFINITIONS=[
 ('FIRST_SPARK','第一簇火','首次正式掌握一课','起步',1,'/map','spark'),
 ('FIVE_PAGES','翻开新页','正式掌握5门不同课','起步',5,'/map','pages'),
 ('REVIEW_ECHO','记忆回声','首次通过正式复习','复习与修复',1,'/review','echo'),
 ('REVIEW_VISITOR','回访常客','5门不同课各通过至少一次正式复习','复习与修复',5,'/review','orbit'),
 ('OLD_PIT','跨过旧坑','同一道正式题答错后，至少24小时再在测验或复习中答对','复习与修复',1,'/review','bridge'),
 ('REPAIR_CREW','修理小队','5道不同题分别完成跨过旧坑','复习与修复',5,'/review','tools'),
 ('STEADY_FIRE','火种还在','任意14个本地自然日内，学习7个不同日期','坚持',7,'/map','flame'),
 ('WELCOME_BACK','欢迎回来','两次有效学习日期相隔至少7天，之后再次学习','坚持',2,'/map','return'),
]
CATALOG={d[0]:d for d in DEFINITIONS}


def progress(db,user_id,now=None):
    now=now or datetime.utcnow()
    masteries=db.scalars(select(LessonMastery)).all()
    mastered=sum(m.status=='mastered' for m in masteries)
    reviewed=sum((m.review_count or 0)>0 for m in masteries)
    passes=sum(m.review_count or 0 for m in masteries)
    today=local_now(now).date();days=[]
    for value in db.scalars(select(StudyDay.study_date).where(StudyDay.user_id==user_id,StudyDay.activity_count>0)):
        try:
            d=date.fromisoformat(value)
            if d<=today:days.append(d)
        except ValueError:continue
    days=sorted(set(days));best=0;left=0
    for right,d in enumerate(days):
        while (d-days[left]).days>=14:left+=1
        best=max(best,right-left+1)
    returned=any((b-a).days>=7 for a,b in zip(days,days[1:]))
    wrong={};repaired=set()
    logs=db.scalars(select(QuizAnswerLog).where(QuizAnswerLog.user_id==user_id,QuizAnswerLog.source.in_(['quiz','review']),QuizAnswerLog.submitted_at<=now).order_by(QuizAnswerLog.submitted_at,QuizAnswerLog.id))
    for log in logs:
        if not log.is_correct:wrong.setdefault(log.question_id,log.submitted_at)
        elif log.question_id in wrong and log.submitted_at-wrong[log.question_id]>=timedelta(hours=24):repaired.add(log.question_id)
    return dict(FIRST_SPARK=mastered,FIVE_PAGES=mastered,REVIEW_ECHO=passes,REVIEW_VISITOR=reviewed,
                OLD_PIT=len(repaired),REPAIR_CREW=len(repaired),STEADY_FIRE=best,WELCOME_BACK=2 if returned else int(bool(days)))
