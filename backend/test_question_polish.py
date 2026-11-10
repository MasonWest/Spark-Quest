"""Editorial regressions: source coverage, source determinism and both length cues."""
import json
from pathlib import Path
import unittest
from audit_question_design import audit, metrics

ROOT=Path(__file__).resolve().parent.parent


class QuestionPolishTests(unittest.TestCase):
    def test_length_audit_ties_and_shortest(self):
        report=metrics([(['aa','bb','cc','dd'],0),(['a','bbbb','cc','dd'],1)])
        self.assertEqual(report['longest_choice_accuracy_pct'],62.5)
        self.assertEqual(report['shortest_choice_accuracy_pct'],12.5)

    def test_both_length_shortcuts_are_bounded_per_target_level(self):
        report=audit()
        for scope in ['journey_by_level','formal_by_level']:
            for chapter in ['l1','l6','l7']:
                with self.subTest(scope=scope,chapter=chapter):
                    row=report[scope][chapter]
                    self.assertLess(row['longest_choice_accuracy_pct'],40)
                    self.assertLess(row['shortest_choice_accuracy_pct'],40)
        self.assertEqual(report['free_response_by_level']['l1'],5)

    def test_l1_and_memory_questions_trace_to_current_teaching(self):
        bank=json.loads((ROOT/'backend/app/l1_l7_reviewed_bank.json').read_text(encoding='utf-8'))
        for entry in bank['lessons']:
            slug=entry['lesson_slug']
            if not slug.startswith('l1-') and slug!='l7-executor-memory':continue
            lesson=json.loads((ROOT/'frontend/src/content/lessons'/f'{slug}.json').read_text(encoding='utf-8'))
            tasks={t['id'] for t in lesson['tasks']}
            for q in entry['questions']:
                self.assertIn(q['task_id'],tasks)
                self.assertTrue(q['key'].endswith('-v2'))
            if slug.startswith('l1-'):
                pairs=[entry['questions'][i:i+2] for i in range(0,10,2)]
                # A new context or a different response representation must be
                # present. Numeric cases may legitimately share some options.
                self.assertTrue(all(a['prompt']!=b['prompt'] for a,b in pairs))
                self.assertLess(sum(sorted(a['options'])==sorted(b['options']) for a,b in pairs),3)


if __name__=='__main__':unittest.main()
