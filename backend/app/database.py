"""Database engine setup for Spark Quest.

- engine / Base / SessionLocal
- init_db(): create tables and seed course data when empty
"""

import json
import logging
from pathlib import Path

from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

logger = logging.getLogger("spark_quest")

# SQLite file lives next to the backend/ directory (backend/spark_quest.db)
DB_PATH = Path(__file__).resolve().parent.parent / "spark_quest.db"

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # needed by SQLite + FastAPI
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for ORM models."""


SEED_FILE = Path(__file__).resolve().parent / "course_seed.json"
QUIZ_SEED_FILE = Path(__file__).resolve().parent / "quiz_seed.json"


def check_database_connection() -> bool:
    """Open a connection and run a trivial query.

    SQLite creates the file on first connect, so this both verifies
    connectivity and initializes the database file.
    """
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return DB_PATH.exists()


def init_db() -> None:
    """Create tables and seed course data if the database is empty."""
    # Import here so models are registered on Base before create_all.
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    # Phase 6.1: ensure the `dimension` column exists on existing databases.
    from . import migrate

    migrate.run_migrations()
    _seed_course_data()
    _seed_quizzes()

    # Phase 9.2: badge catalog must exist before the historical unlock, and
    # the LEVEL_* definitions are derived from course_levels -- so this runs
    # AFTER course/quiz seeding. backfill_badges then unlocks anything
    # derivable from the user's existing lesson_mastery rows.
    from .seed_badges import seed_badges
    from .migrate import backfill_badges

    with SessionLocal() as db:
        seed_badges(db)
    backfill_badges()


def _seed_course_data() -> None:
    """Insert seed levels/lessons only when course_levels is empty.

    When the course data already exists (e.g. DB created in Phase 1/2),
    lesson content is backfilled by slug instead — Phase 3 added structured
    content (explanation / examples / key_points / common_mistakes) to the
    seed file, and existing rows still have an empty `content` placeholder.
    """
    from .models import CourseLevel, Lesson

    data = json.loads(SEED_FILE.read_text(encoding="utf-8"))

    with Session(engine) as session:
        already_seeded = session.scalar(select(CourseLevel).limit(1)) is not None
        if not already_seeded:
            # Count before building: do NOT pop "lessons" off the shared dicts
            # in `data` (the backfill below reads them), and never re-read a
            # popped key (that raised KeyError on the fresh-seed path).
            n_levels = len(data["levels"])
            n_lessons = sum(len(lv.get("lessons", [])) for lv in data["levels"])
            for level_data in data["levels"]:
                level_fields = {k: v for k, v in level_data.items() if k != "lessons"}
                level = CourseLevel(**level_fields)
                for lesson_data in level_data.get("lessons", []):
                    # `content` is a nested object in the seed JSON but a Text
                    # column in the DB -> serialize it, mirroring the backfill
                    # path below. Without this, seeding an empty DB raises
                    # "type 'dict' is not supported".
                    row = dict(lesson_data)
                    if isinstance(row.get("content"), (dict, list)):
                        row["content"] = json.dumps(row["content"], ensure_ascii=False)
                    level.lessons.append(Lesson(**row))
                session.add(level)
            session.commit()
            logger.info("Seeded course data: %s levels, %s lessons.", n_levels, n_lessons)
        else:
            logger.info("Course data already present, skipping seed.")

        _backfill_lesson_content(session, data)


def _backfill_lesson_content(session: Session, data: dict) -> None:
    """Fill empty lessons.content from the seed file, matched by slug.

    Idempotent: rows that already carry content are left untouched, so
    hand-edited content in the DB is never overwritten on restart.
    """
    from .models import Lesson

    seed_content = {
        lesson["slug"]: json.dumps(lesson["content"], ensure_ascii=False)
        for level in data["levels"]
        for lesson in level["lessons"]
        if lesson.get("content")
    }
    if not seed_content:
        return

    updated = 0
    for lesson in session.scalars(select(Lesson)).all():
        if not (lesson.content or "").strip() and lesson.slug in seed_content:
            lesson.content = seed_content[lesson.slug]
            updated += 1
    if updated:
        session.commit()
        logger.info("Backfilled lesson content for %s lessons.", updated)


def _seed_quizzes() -> None:
    """Insert seed quiz questions from quiz_seed.json, once per lesson.

    Idempotent: a lesson that already has any quiz questions is skipped, so
    re-running init_db never duplicates questions and never overwrites edited
    ones.
    """
    from .models import Lesson, QuizQuestion

    if not QUIZ_SEED_FILE.exists():
        return

    data = json.loads(QUIZ_SEED_FILE.read_text(encoding="utf-8"))
    entries = data.get("quizzes", [])

    with Session(engine) as session:
        lessons_by_slug = {l.slug: l for l in session.scalars(select(Lesson)).all()}
        seeded = 0
        for entry in entries:
            lesson = lessons_by_slug.get(entry.get("lesson_slug"))
            if lesson is None:
                logger.warning("Quiz seed: no lesson for slug %s, skipping.", entry.get("lesson_slug"))
                continue
            existing = session.scalar(
                select(func.count())
                .select_from(QuizQuestion)
                .where(QuizQuestion.lesson_id == lesson.id)
            )
            if existing:
                continue
            for i, q in enumerate(entry.get("questions", [])):
                session.add(
                    QuizQuestion(
                        lesson_id=lesson.id,
                        type=q.get("type", "single_choice"),
                        prompt=q.get("prompt", ""),
                        options=json.dumps(q.get("options", []), ensure_ascii=False),
                        correct_index=q.get("correct_index", 0),
                        explanation=q.get("explanation", ""),
                        dimension=q.get("dimension"),
                        order_index=i,
                    )
                )
                seeded += 1
        if seeded:
            session.commit()
            logger.info("Seeded %s quiz questions.", seeded)
        else:
            logger.info("Quiz questions already present, skipping seed.")
