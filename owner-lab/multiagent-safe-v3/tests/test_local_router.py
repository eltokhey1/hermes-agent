import unittest
from local_router import LocalInventory, Route, RoutingDenied, propose_local_route


class TestLocalRouting(unittest.TestCase):
    def i(self, tools=frozenset({'hermes', 'kilo', 'opencode'}), models=frozenset({'qwen3:4b'}), listening=True):
        return LocalInventory(tools, models, listening)

    def test_kilo_first(self):
        r = propose_local_route('code', self.i(), model='qwen3:4b')
        self.assertEqual(r.worker, 'kilo')
        self.assertEqual(r.estimated_cloud_usd, 0)
        self.assertEqual(r.execution, 'PROPOSAL_ONLY')
        self.assertEqual(r.base_url, 'http://127.0.0.1:11434')

    def test_opencode_fallback(self):
        r = propose_local_route('code', self.i(tools=frozenset({'opencode'})), model='qwen3:4b')
        self.assertEqual('opencode', r.worker)

    def test_hermes_general(self):
        self.assertEqual('hermes', propose_local_route('general', self.i(), model='qwen3:4b').worker)

    def test_reject_absent_model(self):
        with self.assertRaises(RoutingDenied):
            propose_local_route('code', self.i(models=frozenset()), model='qwen3:4b')

    def test_reject_absent_service(self):
        with self.assertRaises(RoutingDenied):
            propose_local_route('general', self.i(listening=False), model='qwen3:4b')

    def test_reject_absent_worker(self):
        with self.assertRaises(RoutingDenied):
            propose_local_route('code', self.i(tools=frozenset({'hermes'})), model='qwen3:4b')

    def test_no_fallback_to_untrusted_provider(self):
        with self.assertRaises(RoutingDenied):
            propose_local_route('code', self.i(), model='cloud-paid-model')

    def test_unknown_task_kind_rejected(self):
        with self.assertRaises(RoutingDenied):
            propose_local_route('web-browse', self.i(), model='qwen3:4b')

    def test_untrusted_inventory_rejected(self):
        with self.assertRaises(RoutingDenied):
            LocalInventory({'kilo'}, frozenset({'qwen3:4b'}), True)
        with self.assertRaises(RoutingDenied):
            LocalInventory(frozenset({'kilo'}), frozenset({'qwen3:4b'}), 1)


    def test_aider_only_local_route(self):
        r = propose_local_route('code', self.i(tools=frozenset({'aider'})), model='qwen3:4b')
        self.assertEqual(r.worker, 'aider')
        self.assertEqual(r.inference, 'ollama')
        self.assertEqual(r.execution, 'PROPOSAL_ONLY')
        self.assertEqual(r.estimated_cloud_usd, 0)

    def test_aider_before_opencode_with_no_kilo(self):
        tools = frozenset({'aider', 'opencode'})
        self.assertEqual('aider', propose_local_route('code', self.i(tools=tools), model='qwen3:4b').worker)

    def test_existing_kilo_priority_retained(self):
        tools = frozenset({'kilo', 'aider', 'opencode'})
        self.assertEqual('kilo', propose_local_route('code', self.i(tools=tools), model='qwen3:4b').worker)

    def test_explicit_preferred_aider_and_opencode(self):
        inventory = self.i(tools=frozenset({'kilo', 'aider', 'opencode'}))
        for preferred in ('aider', 'opencode'):
            with self.subTest(preferred=preferred):
                r = propose_local_route('code', inventory, model='qwen3:4b', preferred_worker=preferred)
                self.assertEqual(preferred, r.worker)
                self.assertEqual('PROPOSAL_ONLY', r.execution)

    def test_unavailable_preferred_worker_fails_closed(self):
        with self.assertRaises(RoutingDenied):
            propose_local_route('code', self.i(tools=frozenset({'kilo'})),
                                model='qwen3:4b', preferred_worker='aider')

    def test_disallowed_or_cloud_worker_fails_closed(self):
        for preferred in ('codex', 'minimax', 'cloud', '', 'Kilo', 1, True, [], {}):
            with self.subTest(preferred=preferred), self.assertRaises(RoutingDenied):
                propose_local_route('code', self.i(), model='qwen3:4b', preferred_worker=preferred)

    def test_preferred_worker_not_allowed_for_general_task(self):
        with self.assertRaises(RoutingDenied):
            propose_local_route('general', self.i(), model='qwen3:4b', preferred_worker='aider')

    def test_preferred_worker_never_overrides_ollama_or_model_checks(self):
        with self.assertRaises(RoutingDenied):
            propose_local_route('code', self.i(listening=False, tools=frozenset({'aider'})),
                                model='qwen3:4b', preferred_worker='aider')
        with self.assertRaises(RoutingDenied):
            propose_local_route('code', self.i(tools=frozenset({'aider'})),
                                model='paid-cloud-model', preferred_worker='aider')


if __name__ == '__main__': unittest.main()
