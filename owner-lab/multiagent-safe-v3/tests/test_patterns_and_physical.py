import math
import unittest
from patterns import Proposal, route, fanout_synthesize, evaluator_optimizer, bounded_handoff, WorkflowDenied
from physical_sim import SimulationSafetyGate, VirtualCommand, SafetyStop


class PatternTests(unittest.TestCase):
    def make_proposal(self, agent='research', confidence=.9):
        return Proposal(agent, 'Evidence-backed, nonexecuting plan', confidence, ('source-01',))

    def test_routing_deny_unknown(self):
        self.assertEqual(route('modify_code'), 'code')
        with self.assertRaises(WorkflowDenied): route('deploy_production')

    def test_missing_evidence_denied(self):
        with self.assertRaises(WorkflowDenied): Proposal('research', 'text', .9, ())

    def test_bad_confidence_denied(self):
        for confidence in (math.nan, 1.2, -0.1, True):
            with self.subTest(confidence=confidence), self.assertRaises(WorkflowDenied):
                self.make_proposal(confidence=confidence)

    def test_fanout_proposed_only(self):
        p = {'research': self.make_proposal(), 'code': self.make_proposal('code')}
        result = fanout_synthesize(p)
        self.assertEqual(result['status'], 'PROPOSED_ONLY')
        self.assertFalse(result['external_effects'])
        self.assertEqual(result['evidence_ids'], ['source-01'])

    def test_fanout_reject_confidence_and_mismatched_agent(self):
        with self.assertRaises(WorkflowDenied): fanout_synthesize({'research': self.make_proposal(confidence=.6)})
        with self.assertRaises(WorkflowDenied): fanout_synthesize({'code': self.make_proposal()})

    def test_evaluation_pass(self):
        p = self.make_proposal()
        self.assertIs(evaluator_optimizer(p, lambda _: True, lambda _: p), p)

    def test_evaluation_bound(self):
        p = self.make_proposal()
        attempts = []
        def improve(value):
            attempts.append(1)
            return value
        with self.assertRaises(WorkflowDenied):
            evaluator_optimizer(p, lambda _: False, improve, max_iterations=2)
        self.assertEqual(len(attempts), 2)

    def test_handoff_allow_and_cycle_block(self):
        self.assertEqual(bounded_handoff('research', {'research': 'qa'}), ('research', 'qa'))
        with self.assertRaises(WorkflowDenied):
            bounded_handoff('research', {'research': 'qa', 'qa': 'research'})

    def test_handoff_budget(self):
        with self.assertRaises(WorkflowDenied):
            bounded_handoff('research', {'research': 'code', 'code': 'qa'}, max_handoffs=1)


class PhysicalSimTests(unittest.TestCase):
    def test_virtual_move(self):
        gate = SimulationSafetyGate()
        self.assertEqual(gate.apply(VirtualCommand('virtual.move', 1.0, 1.0))['status'], 'MOVED')
        self.assertEqual(gate.position, (1.0, 1.0))

    def test_reject_ros_hardware(self):
        gate = SimulationSafetyGate()
        for capability in ('ros2.publish', 'motor.control', 'isaac.actuate', 'virtual.move;rm'):
            with self.subTest(capability=capability), self.assertRaises(SafetyStop):
                gate.apply(VirtualCommand(capability, 0.0, 0.0))

    def test_reject_bad_coordinates(self):
        gate = SimulationSafetyGate()
        for x in (-1, 11, math.nan, math.inf, True, '1'):
            with self.subTest(x=x), self.assertRaises(SafetyStop):
                gate.apply(VirtualCommand('virtual.move', x, 0.0))

    def test_reject_long_move(self):
        with self.assertRaises(SafetyStop):
            SimulationSafetyGate().apply(VirtualCommand('virtual.move', 3.0, 2.0))

    def test_reject_segment_collision(self):
        gate = SimulationSafetyGate(position=(2.3, 3.0), obstacles=((3.0, 3.0),))
        with self.assertRaises(SafetyStop):
            gate.apply(VirtualCommand('virtual.move', 3.7, 3.0))
        self.assertEqual(gate.position, (2.3, 3.0))

    def test_stop_latched_no_restart(self):
        gate = SimulationSafetyGate()
        self.assertEqual(gate.apply(VirtualCommand('virtual.stop', 0, 0))['status'], 'STOPPED')
        with self.assertRaises(SafetyStop):
            gate.apply(VirtualCommand('virtual.move', .1, .1))

    def test_episode_bounded(self):
        gate = SimulationSafetyGate()
        with self.assertRaises(SafetyStop):
            gate.run_episode([VirtualCommand('virtual.inspect', 0.0, 0.0)] * 11)
        self.assertEqual(gate.records, [])

    def test_inspect_no_motion(self):
        gate = SimulationSafetyGate()
        ret = gate.run_episode([VirtualCommand('virtual.inspect', 0, 0)])
        self.assertFalse(ret['hardware_execution'])
        self.assertEqual(ret['steps'], 1)
        self.assertEqual(gate.position, (0, 0))


if __name__ == '__main__': unittest.main()
