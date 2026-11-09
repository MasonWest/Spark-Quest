"""Append the two authored lessons, preserving IDs, history and all old content.
Only old lesson.order_index may change. New lesson definitions are immutable.
"""
from contextlib import closing
from datetime import datetime
import json
from pathlib import Path
import sqlite3
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Lesson
from .reviewed_question_bank import seed_catalog_entries

ROOT=Path(__file__).parent


def apply_extensions(db):
    seed=json.loads((ROOT/'course_seed.json').read_text(encoding='utf-8'))
    specs=json.loads((ROOT/'course_extensions.json').read_text(encoding='utf-8'))['lessons']
    bank=json.loads((ROOT/'extension_reviewed_bank.json').read_text(encoding='utf-8'))['lessons']
    inserted=[];moved=[]
    for spec in specs:
        payload=spec['lesson'];slug=payload['slug']
        anchor=db.scalar(select(Lesson).where(Lesson.slug==spec['after']))
        if anchor is None:raise ValueError('Missing extension prerequisite: '+spec['after'])
        level=next(lv for lv in seed['levels'] if any(l['slug']==slug for l in lv['lessons']))
        canonical=level['lessons'];old=[l for l in canonical if l['slug']!=slug]
        rows={l.slug:l for l in db.scalars(select(Lesson).where(Lesson.level_id==anchor.level_id))}
        if set(rows)-{slug}!=set(l['slug'] for l in old):raise ValueError('Unexpected/missing lessons in extension level')
        # Accept exactly either old ordering or the completed canonical ordering.
        positions={l['slug']:i for i,l in enumerate(old)}
        for item in canonical:
            row=rows.get(item['slug'])
            if row is None:continue
            if row.order_index not in {positions.get(item['slug']),item['order_index']}:
                raise ValueError('Course order drift: '+item['slug'])
        expected=dict(payload,order_index=next(l['order_index'] for l in canonical if l['slug']==slug))
        expected['content']=json.dumps(expected['content'],ensure_ascii=False)
        row=rows.get(slug)
        if row is None:
            row=Lesson(level_id=anchor.level_id,**expected);db.add(row);db.flush();inserted.append(slug)
        else:
            for key,value in expected.items():
                actual=getattr(row,key)
                if key=='content':actual=json.loads(actual);value=json.loads(value)
                if actual!=value:raise ValueError('Extension lesson changed without migration: '+slug+'/'+key)
        for item in canonical:
            existing=rows.get(item['slug'])
            if existing is not None and existing.order_index!=item['order_index']:
                moved.append(existing.slug);existing.order_index=item['order_index']
    count=seed_catalog_entries(db,bank)
    db.flush()
    return dict(lessons_added=inserted,order_updated=moved,questions_added=count)


def install(engine,apply=False):
    with Session(engine) as db:
        result=apply_extensions(db);db.rollback()
    changed=bool(result['lessons_added'] or result['order_updated'] or result['questions_added'])
    backup=None
    if apply and changed:
        path=Path(engine.url.database).resolve()
        backup=path.with_name(path.name+'.bak_course_extensions_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
        with closing(sqlite3.connect(path.as_uri()+'?mode=ro',uri=True)) as source,closing(sqlite3.connect(backup)) as target:source.backup(target)
        with Session(engine) as db:
            result=apply_extensions(db);db.commit()
    return dict(mode='APPLY' if apply else 'DRY-RUN',**result,backup=str(backup) if backup else None)
