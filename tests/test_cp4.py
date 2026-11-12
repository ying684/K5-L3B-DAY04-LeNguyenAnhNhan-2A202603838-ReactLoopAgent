"""Kiểm tra source validation qua nhiều provider, không gọi LLM thật."""
import json
import unittest

from agent import run_agent
from status_tools import StatusTools
from test_lab import FakeProvider, final, tool_call


class SourceValidationTests(unittest.TestCase):
    def test_revision_requires_all_successful_incident_sources(self):
        tools = StatusTools()
        github = tools.get_incident_details('github', 'xr3myzj7ms51')['url']
        cloudflare = tools.get_incident_details('cloudflare', 'wp49bp8bqo6c')['url']
        response = tool_call('a', 'get_incident_details', json.dumps({
            'provider': 'github', 'incident_id': 'xr3myzj7ms51'}))
        second = tool_call('b', 'get_incident_details', json.dumps({
            'provider': 'cloudflare', 'incident_id': 'wp49bp8bqo6c'}))
        response['calls'] += second['calls']
        response['message']['tool_calls'] += second['message']['tool_calls']
        provider = FakeProvider([response, final('Nguồn: ' + github),
                                 final('Nguồn: ' + github + ' ' + cloudflare)])
        result = run_agent('So sánh hai incident', provider, tools, max_steps=4)
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(len(provider.histories), 3)
        self.assertIn(github, result['answer'])
        self.assertIn(cloudflare, result['answer'])
        missing = [e for e in result['trace'] if e['event'] == 'validation_missing_source']
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0]['missing_urls'], [cloudflare])
        self.assertEqual(sum(e['event'] == 'tool' for e in result['trace']), 2)

    def test_repeated_missing_source_uses_budget_and_never_completes(self):
        provider = FakeProvider([
            tool_call('a', 'get_incident_details', '{"provider":"github","incident_id":"xr3myzj7ms51"}'),
            final('Thiếu URL'), final('Vẫn thiếu URL'),
        ])
        result = run_agent('check', provider, StatusTools(), max_steps=3)
        self.assertEqual(result['status'], 'max_steps')
        self.assertEqual(len(provider.histories), 3)
        self.assertEqual(sum(e['event'] == 'validation_missing_source' for e in result['trace']), 2)
