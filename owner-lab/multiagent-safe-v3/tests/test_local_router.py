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

if __name__ == '__main__': unittest.main()
