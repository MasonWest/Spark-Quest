# -*- coding: utf-8 -*-
"""Repair audit: lessons hidden from 待复习 by a FAILED review's 3-day defer.

Background (bug fixed 2026-09-14):
  `POST /api/review/{id}/submit` used to call `defer_review_schedule()` on a
  failed round, setting `next_review_at = now + 3 days`. Home's 待复习 list is
  `status='mastered' AND next_review_at <= now`, so a failed review dropped the
  lesson out of its only entry point until the deferral expired.

  Code is fixed (failures now keep the lesson due). This script finds the
  historical rows that are still wrongly hidden and, with --apply, makes them
  due again by setting `next_review_at = last_review_at`.

Detection (conservative -- else skip and report):
  * mastery.status == 'mastered'
  * next_review_at > now            (currently hidden)
  * the LATEST review round for that lesson in quiz_answer_log had >=1 wrong
    answer (a pass requires 5/5, so any wrong answer proves it failed)
  * that round contains exactly REVIEW_QUESTION_COUNT rows

Usage:
  python fix_deferred_failed_reviews_20260914.py           # dry run
  python fix_deferred_failed_reviews_20260914.py --apply   # write
"""
import shutil
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

DB = Path(__file__).resolve().parent / "spark_quest.db"
BACKUP = DB.with_name(DB.name + ".bak_before_reviewdeferfix_20260914")
ROUND_WINDOW_SECONDS = 10
REVIEW_QUESTION_COUNT = 5

APPLY = "--apply" in sys.argv
NOW = datetime.utcnow()
# Same "YYYY-MM-DD HH:MM:SS.ffffff" shape SQLAlchemy writes, so that raw string
# comparisons against `next_review_at` / `submitted_at` behave correctly.
NOW_SQL = NOW.strftime("%Y-%m-%d %H:%M:%S.%f")

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row


def parse(ts):
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


print(f"[now utc] {NOW.isoformat()}")
print(f"[mode]    {'APPLY' if APPLY else 'DRY RUN'}")
print()

rows = con.execute("""
    SELECT m.lesson_id, m.status, m.srs_stage, m.review_count,
           m.last_review_at, m.next_review_at,
           l.title, cl.title AS level_title
    FROM lesson_mastery m
    JOIN lessons l ON l.id = m.lesson_id
    JOIN course_levels cl ON cl.id = l.level_id
    WHERE m.status = 'mastered' AND m.next_review_at IS NOT NULL AND m.next_review_at > ?
    ORDER BY m.next_review_at
""", (NOW_SQL,)).fetchall()

print(f"mastered lessons with a FUTURE next_review_at: {len(rows)}")

candidates = []
skipped = []
for r in rows:
    lid = r["lesson_id"]
    agg = con.execute("""
        SELECT MAX(submitted_at) AS last_ts, COUNT(*) AS n
        FROM quiz_answer_log WHERE lesson_id=? AND source='review'
    """, (lid,)).fetchone()
    if not agg or not agg["last_ts"]:
        skipped.append((lid, r["title"], "no review log at all"))
        continue
    last_ts = parse(agg["last_ts"])
    if last_ts is None:
        skipped.append((lid, r["title"], f"unparseable log ts {agg['last_ts']!r}"))
        continue
    # NOTE: SQLAlchemy stores DateTime in SQLite as "YYYY-MM-DD HH:MM:SS.ffffff"
    # (space separator). Build the lower bound in that exact format -- an
    # isoformat() string uses "T" and makes every string comparison fail
    # silently (which reads as "0 rows in the round").
    lo = (last_ts - timedelta(seconds=ROUND_WINDOW_SECONDS)).strftime("%Y-%m-%d %H:%M:%S.%f")
    rnd = con.execute("""
        SELECT COUNT(*) AS n, COALESCE(SUM(is_correct), 0) AS ok
        FROM quiz_answer_log
        WHERE lesson_id=? AND source='review' AND submitted_at >= ?
    """, (lid, lo)).fetchone()
    n, ok = rnd["n"], rnd["ok"]
    if n != REVIEW_QUESTION_COUNT:
        skipped.append((lid, r["title"], f"last round has {n} rows (expected {REVIEW_QUESTION_COUNT})"))
        continue
    if ok == n:
        skipped.append((lid, r["title"], "last round PASSED (5/5) -> not a defer artifact"))
        continue
    candidates.append({
        "lesson_id": lid,
        "title": r["title"],
        "level": r["level_title"],
        "stage": r["srs_stage"],
        "review_count": r["review_count"],
        "last_review_at": r["last_review_at"],
        "next_review_at": r["next_review_at"],
        "round_wrong": n - ok,
    })

print()
print("=== CANDIDATES: hidden although the latest review FAILED ===")
if not candidates:
    print("  (none)")
for c in candidates:
    target = c["last_review_at"] or NOW_SQL
    gap = ""
    nra, lra = parse(c["next_review_at"]), parse(c["last_review_at"])
    if nra and lra:
        gap = f"  (next - last = {(nra - lra).total_seconds()/86400:.3f} days)"
    print(f"  lesson {c['lesson_id']:>3} | {c['level']} · {c['title']}")
    print(f"      stage={c['stage']} review_count={c['review_count']} last round wrong={c['round_wrong']}/5")
    print(f"      last_review_at={c['last_review_at']}")
    print(f"      next_review_at={c['next_review_at']}{gap}")
    print(f"      -> would set next_review_at = {target}  (due now)")

print()
print("=== SKIPPED (need a human look) ===")
if not skipped:
    print("  (none)")
for lid, title, why in skipped:
    print(f"  lesson {lid:>3} | {title} | {why}")

print()
if not APPLY:
    print("DRY RUN -- nothing written. Re-run with --apply to repair.")
else:
    if not candidates:
        print("Nothing to repair.")
    else:
        shutil.copy2(DB, BACKUP)
        print(f"backup -> {BACKUP.name}")
        for c in candidates:
            con.execute(
                "UPDATE lesson_mastery SET next_review_at = ? WHERE lesson_id = ?",
                (c["last_review_at"] or NOW_SQL, c["lesson_id"]),
            )
        con.commit()
        print(f"repaired {len(candidates)} lesson(s): {[c['lesson_id'] for c in candidates]}")

con.close()
