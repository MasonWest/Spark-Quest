"""Read-only source audit. Run from any cwd; does not read or modify learner data.

Length is Python Unicode code-point length, not rendered width. Longest-choice
accuracy breaks ties uniformly, so it is an estimate of a guessing strategy,
not observed learner accuracy. Metadata overlap is not semantic coverage.
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANKS = (
    "l2_reviewed_bank.json", "l3_l6_reviewed_bank.json",
    "l1_l7_reviewed_bank.json", "extension_reviewed_bank.json", "l0_reviewed_bank.json",
)


def metrics(rows):
    unique = any_longest = 0
    longest_accuracy = shortest_accuracy = chance = 0.0
    for options, correct in rows:
        lengths = list(map(len, options))
        winners = [i for i, length in enumerate(lengths) if length == max(lengths)]
        hit = correct in winners
        unique += hit and len(winners) == 1
        any_longest += hit
        longest_accuracy += (1 / len(winners)) if hit else 0
        shortest = [i for i, length in enumerate(lengths) if length == min(lengths)]
        shortest_accuracy += (1 / len(shortest)) if correct in shortest else 0
        chance += 1 / len(options)
    n = len(rows)
    return {
        "n": n, "correct_uniquely_longest": unique,
        "correct_among_longest": any_longest,
        "longest_choice_accuracy_pct": round(100 * longest_accuracy / n, 1) if n else None,
        "shortest_choice_accuracy_pct": round(100 * shortest_accuracy / n, 1) if n else None,
        "uniform_choice_accuracy_pct": round(100 * chance / n, 1) if n else None,
    }


def audit():
    formal = []
    for name in BANKS:
        bank = json.loads((ROOT / "backend/app" / name).read_text(encoding="utf-8"))
        questions = [q for entry in bank["lessons"] for q in entry["questions"]]
        pairs = defaultdict(list)
        for entry in bank["lessons"]:
            for q in entry["questions"]:
                pairs[entry["lesson_slug"], q["knowledge_id"]].append(q)
        repeated = sum(
            any(sorted(a["options"]) == sorted(b["options"])
                for a in qs if a["purpose"] == "assessment"
                for b in qs if b["purpose"] != "assessment")
            for qs in pairs.values()
        )
        formal.append({
            "source": name, "lessons": len(bank["lessons"]),
            **metrics([(q["options"], q["correct_index"]) for q in questions]),
            "types": dict(Counter(q["type"] for q in questions)),
            "correct_positions": dict(Counter(q["correct_index"] for q in questions)),
            "knowledge_groups": len(pairs),
            "groups_with_identical_option_sets_across_phases": repeated,
        })
    chapters = defaultdict(list)
    free_responses = Counter()
    formal_by_level = defaultdict(list)
    for name in BANKS:
        for entry in json.loads((ROOT/'backend/app'/name).read_text(encoding='utf-8'))['lessons']:
            for q in entry['questions']:
                formal_by_level[entry['lesson_slug'].split('-')[0]].append((q['options'],q['correct_index']))
    task_shapes = Counter()
    for path in sorted((ROOT / "frontend/src/content/lessons").glob("*.json")):
        lesson = json.loads(path.read_text(encoding="utf-8"))
        for task in lesson["tasks"]:
            task_shapes["single_field" if len(task["fields"]) == 1 else "multi_field"] += 1
            for field in task["fields"]:
                if field.get('input'):
                    task_shapes['free_response_fields'] += 1
                    free_responses[lesson['slug'].split('-')[0]] += 1
                    continue
                options = field["options"]
                correct = next(i for i, o in enumerate(options) if o["id"] == field["correctOptionId"])
                chapters[lesson["slug"].split("-")[0]].append(([o["text"] for o in options], correct))
    return {
        "scope": "Current L0-L7 authored formal banks and primary journey fields; excludes legacy questions, remedies, delayed checks, and downloadable labs.",
        "length_unit": "Unicode code points; ties broken uniformly; source-only, not learner analytics",
        "formal": formal,
        "formal_by_level": {chapter:metrics(rows) for chapter,rows in sorted(formal_by_level.items())},
        "journey_task_shapes": dict(task_shapes),
        "free_response_by_level": dict(free_responses),
        "journey_by_level": {chapter: metrics(rows) for chapter, rows in sorted(chapters.items())},
    }


if __name__ == "__main__":
    print(json.dumps(audit(), ensure_ascii=False, indent=2))
