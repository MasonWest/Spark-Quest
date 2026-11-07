"""Purpose-separated questions. Legacy rows remain available to history/practice."""
import json
from pathlib import Path
from sqlalchemy import select
from .models import Lesson, QuizQuestion

BANK_PATH = Path(__file__).with_name("l2_reviewed_bank.json")


def catalog():
    return json.loads(BANK_PATH.read_text(encoding="utf-8"))["lessons"]


def seed_reviewed_bank(db):
    inserted = 0
    for entry in catalog():
        lesson = db.scalar(select(Lesson).where(Lesson.slug == entry["lesson_slug"]))
        if lesson is None:
            continue
        existing = {q.prompt: q for q in db.scalars(select(QuizQuestion).where(QuizQuestion.lesson_id == lesson.id)).all()}
        for i, question in enumerate(entry["questions"]):
            previous = existing.get(question["prompt"])
            if previous:
                if json.loads(previous.options) != question["options"] or previous.correct_index != question["correct_index"] or previous.explanation != question["explanation"]:
                    raise ValueError("Reviewed question changed without explicit migration: " + question["key"])
                continue
            row = QuizQuestion(lesson_id=lesson.id, type=question["type"], prompt=question["prompt"], options=json.dumps(question["options"], ensure_ascii=False), correct_index=question["correct_index"], explanation=question["explanation"], dimension=question["dimension"], order_index=100+i)
            db.add(row)
            inserted += 1
    db.flush()
    return inserted


def questions_for_phase(slug, questions, phase):
    entry = next((e for e in catalog() if e["lesson_slug"] == slug), None)
    if entry is None:
        return list(questions)
    purposes = {"assessment"} if phase == "assessment" else {"review", "remediation"}
    expected = {q["prompt"] for q in entry["questions"] if q["purpose"] in purposes}
    selected = [q for q in questions if q.prompt in expected]
    if len(selected) != len(expected) or len(selected) < 5:
        raise ValueError("L2 reviewed bank is incomplete; initialize the database before serving quizzes")
    return selected
