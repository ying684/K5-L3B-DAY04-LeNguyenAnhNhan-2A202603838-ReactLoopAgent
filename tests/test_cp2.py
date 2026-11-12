"""Kiểm tra phục hồi sau lỗi và điều kiện dừng CP2, không gọi API."""
import json
import unittest
from unittest.mock import Mock

from agent import run_agent
from status_tools import StatusTools
from test_lab import FakeProvider, final, tool_call


class RobustnessTests(unittest.TestCase):
    def test_provider_failure_preserves_previous_trace_and_usage(self):
        first = tool_call('a', 'get_status', '{"provider":"github"}')
        first['usage'] = {'total_tokens': 12}
        provider = Mock()
        provider.complete.side_effect = [first, RuntimeError('SECRET request data')]
        result = run_agent('check', provider, StatusTools())
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['answer'], '')
        self.assertEqual(result['usage'], [{'total_tokens': 12}])
        self.assertEqual(result['trace'][-1]['stage'], 'provider')
        self.assertEqual(result['trace'][-1]['step'], 2)
        self.assertTrue(any(e['event'] == 'tool' for e in result['trace']))
        self.assertNotIn('SECRET', json.dumps(result))

    def test_unknown_tool_invalid_provider_and_timeout_reach_model(self):
        cases = [
            ('missing', '{}', StatusTools(), 'UNKNOWN_TOOL'),
            ('get_status', '{"provider":"invalid"}', StatusTools(), 'ValueError'),
            ('get_status', '{"provider":"github"}', StatusTools(fail=True), 'TimeoutError'),
            ('get_status', '{"provider":"github"}', Mock(execute=Mock(side_effect=TimeoutError('SECRET'))), 'TimeoutError'),
        ]
        for name, args, tools, expected in cases:
            with self.subTest(expected=expected, name=name):
                provider = FakeProvider([tool_call('a', name, args), final('Not enough data')])
                result = run_agent('check', provider, tools)
                self.assertEqual(result['status'], 'completed')
                observation = provider.histories[1][-1]
                self.assertEqual(observation['tool_call_id'], 'a')
                self.assertEqual(json.loads(observation['content'])['error'], expected)
                event = next(e for e in result['trace'] if e['event'] == 'tool')
                self.assertEqual(event['result']['error'], expected)
                self.assertNotIn('SECRET', json.dumps(result))

    def test_invalid_arguments_do_not_skip_other_calls(self):
        for invalid in ['{', '[]', 'null', '42']:
            with self.subTest(arguments=invalid):
                response = tool_call('bad', 'get_status', invalid)
                valid = tool_call('good', 'get_status', '{"provider":"github"}')
                response['calls'] += valid['calls']
                response['message']['tool_calls'] += valid['message']['tool_calls']
                provider = FakeProvider([response, final()])
                result = run_agent('check', provider, StatusTools())
                self.assertEqual(result['status'], 'completed')
                observations = provider.histories[1][-2:]
                self.assertEqual([m['tool_call_id'] for m in observations], ['bad', 'good'])
                self.assertEqual(json.loads(observations[0]['content'])['error'], 'INVALID_ARGUMENTS')
                self.assertEqual(json.loads(observations[1]['content'])['provider'], 'github')

    def test_truncated_tool_call_is_never_executed(self):
        response = tool_call('a', 'get_status', '{"provider":"github"}')
        response['finish'] = 'length'
        tools = Mock()
        result = run_agent('check', FakeProvider([response]), tools)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['trace'][-1]['event'], 'error')
        tools.execute.assert_not_called()

    def test_budget_exhaustion_is_traced(self):
        provider = FakeProvider([tool_call('a', 'get_status', '{"provider":"github"}')])
        result = run_agent('check', provider, StatusTools(), max_steps=1)
        self.assertEqual(result['status'], 'max_steps')
        self.assertEqual(len(provider.histories), 1)
        self.assertEqual(result['trace'][-1], {'event': 'max_steps', 'step': 1})

    def test_invalid_budget_does_not_call_model(self):
        for budget in [0, -1, True, 1.5]:
            with self.subTest(budget=budget):
                provider = Mock()
                result = run_agent('check', provider, StatusTools(), max_steps=budget)
                self.assertEqual(result['status'], 'error')
                self.assertEqual(result['trace'][-1]['stage'], 'input')
                provider.complete.assert_not_called()
