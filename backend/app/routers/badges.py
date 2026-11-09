"""Badge catalog API (Phase 9.2).

Endpoints:
    GET /api/badges  -> full catalog for the (single) local user, with live
                        unlock state. Secret badges that are NOT yet unlocked
                        expose only their code + is_secret flag; name /
                        description / image are blanked so the catalog can't
                        leak what a hidden badge is.

The catalog is the badge_definitions table (seeded by seed_badges). Unlock
state comes from user_badges. No badge is ever "computed" here -- the engine
in badge_service decides unlocks; this router only projects existing facts.
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import DEFAULT_USER_ID, BadgeDefinition, UserBadge, LessonMastery, QuizAnswerLog
from ..schemas import BadgeOut

router = APIRouter(prefix="/api")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def build_badge_out(
    badge: BadgeDefinition,
    unlocked_ids: set,
    unlocked_at_map: dict,
) -> BadgeOut:
    """Project one catalog row, blanking secret badges that are still locked."""
    unlocked = badge.id in unlocked_ids
    # A secret badge only reveals itself once earned.
    secret_locked = badge.is_secret and not unlocked
    return BadgeOut(
        code=badge.code,
        name="" if secret_locked else badge.name,
        description="" if secret_locked else badge.description,
        image="" if secret_locked else badge.image,
        tier=badge.tier,
        sort_order=badge.sort_order,
        is_secret=badge.is_secret,
        unlocked=unlocked,
        unlocked_at=unlocked_at_map.get(badge.id),
    )


@router.get("/badges", response_model=List[BadgeOut])
def list_badges(db: Session = Depends(get_db)) -> List[BadgeOut]:
    """Full badge catalog with per-user unlock state.

    Order mirrors the seed (journey badges by level, then special badges), so
    the frontend can group by `tier` without re-sorting.
    """
    definitions = db.scalars(
        select(BadgeDefinition).order_by(BadgeDefinition.sort_order, BadgeDefinition.id)
    ).all()

    rows = db.execute(
        select(UserBadge.badge_id, UserBadge.unlocked_at).where(
            UserBadge.user_id == DEFAULT_USER_ID
        )
    ).all()
    unlocked_ids = {row[0] for row in rows}
    unlocked_at_map = {
        row[0]: (row[1].isoformat() if row[1] is not None else None) for row in rows
    }

    from ..learning_achievements import CATALOG
    from ..badge_service import build_context
    ctx = build_context(db, DEFAULT_USER_ID)
    values = ctx.learning
    legacy = {**{f'QUIZ_{n}':(ctx.total_quiz_correct,n) for n in (100,500,1000)},
              **{f'STREAK_{n}':(ctx.longest_streak,n) for n in (7,30,100)},
              'REVIEW_50':(ctx.total_reviews_passed,50),'QUANJING':(ctx.mastered_count,ctx.total_lessons)}
    mastered = db.scalars(select(LessonMastery).where(LessonMastery.status=='mastered').order_by(LessonMastery.next_review_at)).first()
    review_action = f'/review/{mastered.lesson_id}' if mastered else '/map'
    wrong = db.scalars(select(QuizAnswerLog).where(QuizAnswerLog.user_id==DEFAULT_USER_ID,QuizAnswerLog.source.in_(['quiz','review']),QuizAnswerLog.is_correct==0).order_by(QuizAnswerLog.submitted_at.desc())).first()
    repair_action = (f'/review/{wrong.lesson_id}' if wrong.source=='review' else f'/lesson/{wrong.lesson_id}/quiz') if wrong else review_action
    result = []
    for b in definitions:
        item = build_badge_out(b, unlocked_ids, unlocked_at_map)
        if b.code in CATALOG and not (b.is_secret and not item.unlocked):
            _, _, _, group, goal, action, _ = CATALOG[b.code]
            item.progress = goal if item.unlocked else min(goal, values[b.code])
            item.goal = goal
            item.group = group
            item.action = repair_action if b.code in ('OLD_PIT','REPAIR_CREW') else review_action if action=='/review' else action
        elif not (b.is_secret and not item.unlocked):
            pair = legacy.get(b.code)
            if b.code.startswith('LEVEL_'):
                pair = ctx.levels.get(int(b.code.split('_')[1]))
            if pair and pair[1]>0:
                item.progress = min(pair[0],pair[1]);item.goal=pair[1];item.action='/map'
        result.append(item)
    return result
