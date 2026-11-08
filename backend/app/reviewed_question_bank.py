"""L2-L6 purpose routing; legacy question IDs remain gradable and in history."""
import json
from pathlib import Path
from sqlalchemy import select
from .models import Lesson, QuizQuestion
from . import l2_question_bank

BANK_PATH = Path(__file__).with_name('l3_l6_reviewed_bank.json')


def extra_catalog():
    return json.loads(BANK_PATH.read_text(encoding='utf-8'))['lessons']


def catalog():
    return l2_question_bank.catalog() + extra_catalog()


def has_reviewed_bank(slug):
    return any(entry['lesson_slug'] == slug for entry in catalog())


def seed_reviewed_bank(db):
    inserted = l2_question_bank.seed_reviewed_bank(db)
    for entry in extra_catalog():
        lesson = db.scalar(select(Lesson).where(Lesson.slug == entry['lesson_slug']))
        if lesson is None:
            continue
        existing = {q.prompt:q for q in db.scalars(select(QuizQuestion).where(QuizQuestion.lesson_id==lesson.id)).all()}
        for i,q in enumerate(entry['questions']):
            old = existing.get(q['prompt'])
            if old:
                if json.loads(old.options)!=q['options'] or old.correct_index!=q['correct_index'] or old.explanation!=q['explanation'] or old.dimension!=q['dimension'] or old.type!=q['type']:
                    raise ValueError('Reviewed question changed without migration: '+q['key'])
                continue
            row = QuizQuestion(lesson_id=lesson.id,type=q['type'],prompt=q['prompt'],options=json.dumps(q['options'],ensure_ascii=False),correct_index=q['correct_index'],explanation=q['explanation'],dimension=q['dimension'],order_index=200+i)
            db.add(row);existing[q['prompt']]=row;inserted+=1
    db.flush()
    return inserted


def questions_for_phase(slug,questions,phase):
    entry = next((e for e in extra_catalog() if e['lesson_slug']==slug),None)
    if entry is None:
        return l2_question_bank.questions_for_phase(slug,questions,phase)
    if phase not in ('assessment','review'):
        raise ValueError('Unknown question phase')
    purposes={'assessment'} if phase=='assessment' else {'review','remediation'}
    expected={q['prompt'] for q in entry['questions'] if q['purpose'] in purposes}
    selected=[q for q in questions if q.prompt in expected]
    if len(expected)!=5 or len(selected)!=5:
        raise ValueError('Reviewed bank incomplete; run the backed-up bank installer before serving quizzes')
    return selected
