"""Kiểm tra retry, pagination và context bonus qua agent; không gọi API."""
import json
import unittest
from unittest.mock import Mock, patch

from agent import run_agent
from bonus.tools import BonusTools
from test_lab import FakeProvider, final, tool_call


class BonusControlTests(unittest.TestCase):
    def test_persistent_rate_limit_stops_backend_retry(self):
        tools = BonusTools(scenario='rate_limit_always')
        provider = FakeProvider([
            tool_call(str(i), 'get_vercel_status', '{}') for i in range(3)
        ] + [final('Không xác nhận được Vercel vì rate limit.')])
        result = run_agent('check', provider, tools, max_steps=6)
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(tools.calls[('get_vercel_status', 'vercel')], 2)
        last = json.loads(provider.histories[-1][-1]['content'])
        self.assertEqual(last['error'], 'RATE_LIMITED')
        self.assertFalse(last['retry_allowed'])

    def test_retry_after_seconds_and_http_date_are_respected(self):
        for retry_after in ('2', 'Thu, 01 Jan 1970 00:01:42 GMT'):
            with self.subTest(retry_after=retry_after):
                tools = BonusTools()
                tools.execute = Mock(side_effect=[
                    {'ok': False, 'error': 'RATE_LIMITED', 'retry_after': retry_after},
                    {'provider': 'npm', 'overall': {'indicator': 'none'}},
                ])
                provider = FakeProvider([
                    tool_call('a', 'get_npm_status', '{}'),
                    tool_call('b', 'get_npm_status', '{}'), final(),
                ])
                with patch('agent.time.time', return_value=100), patch('agent.time.sleep') as sleep:
                    result = run_agent('check', provider, tools)
                self.assertEqual(result['status'], 'completed')
                sleep.assert_called_once_with(2.0)
                self.assertEqual(tools.execute.call_count, 2)
                self.assertTrue(any(e['event'] == 'retry_wait' for e in result['trace']))

    def test_long_retry_after_stops_without_waiting_or_new_request(self):
        tools = BonusTools()
        tools.execute = Mock(return_value={'ok': False, 'error': 'RATE_LIMITED', 'retry_after': '120'})
        provider = FakeProvider([
            tool_call('a', 'get_npm_status', '{}'),
            tool_call('b', 'get_npm_status', '{}'), final('Chưa biết trạng thái npm.'),
        ])
        with patch('agent.time.time', return_value=100), patch('agent.time.sleep') as sleep:
            result = run_agent('check', provider, tools)
        self.assertEqual(result['status'], 'completed')
        sleep.assert_not_called()
        tools.execute.assert_called_once()
        self.assertFalse(json.loads(provider.histories[1][-1]['content'])['retry_allowed'])

    def test_context_compaction_keeps_original_trace(self):
        provider = FakeProvider([tool_call('a', 'get_vercel_status', '{}'), final()])
        result = run_agent('check', provider, BonusTools(scenario='noisy'))
        observation = json.loads(provider.histories[1][-1]['content'])
        self.assertNotIn('distractors', observation)
        self.assertEqual(observation['omitted_distractor_count'], 160)
        event = next(e for e in result['trace'] if e['event'] == 'tool')
        self.assertEqual(len(event['result']['distractors']), 160)
        self.assertEqual(event['result']['incidents'], observation['incidents'])

    def test_read_next_page_and_keep_source(self):
        tools = BonusTools()
        first = tools.get_incident_details('vercel', 'sps6n39gm4sg')
        provider = FakeProvider([
            tool_call('a', 'get_incident_details', json.dumps({'provider': 'vercel', 'incident_id': first['id']})),
            tool_call('b', 'get_incident_details', json.dumps({'provider': 'vercel', 'incident_id': first['id'], 'offset': first['next_offset']})),
            final('Incident lịch sử, vẫn còn trang chưa đọc. Nguồn: ' + first['url']),
        ])
        result = run_agent('Tìm thông báo upstream', provider, tools)
        self.assertEqual(result['status'], 'completed')
        events = [e for e in result['trace'] if e['event'] == 'tool']
        self.assertEqual([e['step'] for e in events], [1, 2])
        self.assertTrue(any('GitHub' in u['body'] for u in events[1]['result']['updates']))
        self.assertIsNotNone(events[1]['result']['next_offset'])
        self.assertIn(first['url'], result['answer'])
