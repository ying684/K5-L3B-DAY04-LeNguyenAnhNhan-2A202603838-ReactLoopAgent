"""Chạy tiếp report lỗi mà không gọi lại case đã có điểm hay sửa điểm cũ."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import urllib.error
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'evals'))
import run_evals
from agent import run_agent
from status_tools import StatusTools


class RetryTests(unittest.TestCase):
    def report(self):
        cases = json.loads((Path(run_evals.__file__).parent / 'cases.json').read_text(encoding='utf-8'))
        return {'config': {'provider': 'groq', 'model': 'test', 'judge_provider': 'groq',
                           'judge_model': 'test', 'max_steps': 8, 'dataset': 'core',
                           'groq_max_completion_tokens': 8192},
                'cases': [dict(c, grade={'score': None if c['id'] == 'E6' else 0 if c['id'] == 'A1' else 100,
                                        'status': 'unscored' if c['id'] == 'E6' else 'scored'}) for c in cases]}

    def invoke(self, path, fake):
        argv = ['run_evals.py', '--provider', 'groq', '--model', 'test',
                '--output', str(path), '--retry-unscored']
        with patch.object(sys, 'argv', argv), patch.object(run_evals, 'run_case', side_effect=fake) as run:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                code = run_evals.main()
        return code, run

    def test_only_unscored_retried_zero_preserved_and_original_backed_up(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'report.json'
            original = self.report()
            path.write_text(json.dumps(original), encoding='utf-8')
            original_bytes = path.read_bytes()
            def fake(case, args):
                self.assertEqual(case['id'], 'E6')
                return dict(case, grade={'score': 80, 'status': 'scored'})
            code, run = self.invoke(path, fake)
            self.assertEqual(code, 0)
            self.assertEqual(run.call_count, 1)
            report = json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(report['summary']['scored_cases'], 22)
            for before, after in zip(original['cases'], report['cases']):
                if before['id'] != 'E6':
                    self.assertEqual(before, after)
            self.assertEqual(report['retry_history'][0]['previous_unscored'][0]['id'], 'E6')
            self.assertEqual(next(Path(td).glob('*.before_retry_*.json')).read_bytes(), original_bytes)

    def test_configuration_mismatch_rejected_before_api(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'report.json'
            report = self.report()
            report['config']['max_steps'] = 9
            path.write_text(json.dumps(report), encoding='utf-8')
            with self.assertRaises(SystemExit) as raised:
                self.invoke(path, lambda *args: self.fail('Must not call API'))
            self.assertEqual(raised.exception.code, 2)
            self.assertEqual(json.loads(path.read_text(encoding='utf-8')), report)

    def test_failure_stays_unscored_without_repeating_scored_cases(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'report.json'
            path.write_text(json.dumps(self.report()), encoding='utf-8')
            code, run = self.invoke(path, lambda c, a: dict(c, grade={'score': None, 'status': 'unscored'}))
            self.assertEqual(code, 1)
            self.assertEqual(run.call_count, 1)
            self.assertIsNone(json.loads(path.read_text(encoding='utf-8'))['summary']['score_0_100'])

    def test_http_status_is_traced_without_error_body(self):
        http_error = urllib.error.HTTPError('https://example.invalid', 429, 'SECRET', {}, io.BytesIO())
        error = RuntimeError('SECRET')
        error.__cause__ = http_error
        provider = Mock(complete=Mock(side_effect=error))
        result = run_agent('check', provider, StatusTools())
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['trace'][-1]['http_status'], 429)
        self.assertNotIn('SECRET', json.dumps(result))
        http_error.close()
