"""Hermes offline autonomy planning safety negative tests; no actual tools or agents."""
import copy
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_workflow_planner import plan_tasks, InvalidPlan, main


def task(ident='P0-01', *, action='READ_ONLY', deps=None, role='Observer', cost=0):
    return dict(id=ident, role=role, action=action, dependencies=deps or [], impact=10,
                confidence=.9, urgency=8, effort=2, estimated_cost_usd=cost)


def request(tasks=None):
    return dict(tasks=tasks if tasks is not None else [task()], completed={},
                limits={'max_usd': 0, 'max_steps': 45, 'max_tool_calls': 45},
                estop_engaged=False, gates={'G0':'NO-GO','G_CODE':'NO-GO','G1':'NO-GO','production':'HOLD'})


class PlannerTests(unittest.TestCase):
    def test_readonly_candidate_is_never_authorized(self):
        r=plan_tasks(request()); self.assertEqual(r['decisions'][0]['decision'],'CANDIDATE_READ_ONLY_NOT_AUTHORIZED')
        self.assertEqual(r['production'],'HOLD');self.assertFalse(r['execution_performed'])
    def test_estop_blocks_readonly(self):
        v=request();v['estop_engaged']=True
        self.assertEqual(plan_tasks(v)['decisions'][0]['decision'],'ESTOP_HOLD')
    def test_estop_not_boolean_refused(self):
        v=request();v['estop_engaged']='false'
        self.assertRaises(InvalidPlan,plan_tasks,v)
    def test_side_effects_cannot_be_approved_by_boolean(self):
        for kind in ('CODE_WRITE','NETWORK','DELETE','FINANCIAL','PRODUCTION'):
            with self.subTest(kind=kind):
                v=request([task(action=kind)])
                self.assertEqual(plan_tasks(v)['decisions'][0]['decision'],'HUMAN_APPROVAL_AND_GATE_REQUIRED')
    def test_unknown_action_fails_closed(self):
        v=request([task(action='RUN_SHELL')]);self.assertRaises(InvalidPlan,plan_tasks,v)
    def test_unknown_role_fails_closed(self):
        v=request([task(role='ROOT')]);self.assertRaises(InvalidPlan,plan_tasks,v)
    def test_non_string_role_and_action_fails_closed(self):
        for key in ('role', 'action'):
            with self.subTest(key=key):
                v=request();v['tasks'][0][key]=['unexpected']
                self.assertRaises(InvalidPlan,plan_tasks,v)
    def test_no_task_fails(self):
        self.assertRaises(InvalidPlan,plan_tasks,request([]))
    def test_more_than_canonical_budget_fails(self):
        self.assertRaises(InvalidPlan,plan_tasks,request([task('T%d'%i) for i in range(46)]))
    def test_duplicate_ids_fails(self):
        self.assertRaises(InvalidPlan,plan_tasks,request([task(),task()]))
    def test_unknown_dependency_fails(self):
        self.assertRaises(InvalidPlan,plan_tasks,request([task(deps=['UNDEFINED'])]))
    def test_cycle_fails(self):
        self.assertRaises(InvalidPlan,plan_tasks,request([task('a',deps=['b']),task('b',deps=['a'])]))
    def test_self_dependency_fails(self):
        self.assertRaises(InvalidPlan,plan_tasks,request([task(deps=['P0-01'])]))
    def test_missing_dependency_fenced(self):
        v=request([task('a'),task('b',deps=['a'])])
        decisions={x['id']:x['decision'] for x in plan_tasks(v)['decisions']}
        self.assertEqual(decisions['b'],'DEPENDENCY_PENDING')
    def test_completion_requires_64_hex_evidence(self):
        v=request([task('a'),task('b',deps=['a'])]);v['completed']={'a':'done'}
        self.assertRaises(InvalidPlan,plan_tasks,v)
    def test_completion_releases_dependents_proposal_only(self):
        v=request([task('a'),task('b',deps=['a'])]);v['completed']={'a':'f'*64}
        decisions={x['id']:x['decision'] for x in plan_tasks(v)['decisions']}
        self.assertEqual(decisions['a'],'COMPLETED_EVIDENCE_ONLY')
        self.assertEqual(decisions['b'],'CANDIDATE_READ_ONLY_NOT_AUTHORIZED')
    def test_budget_zero_blocks_positive_cost(self):
        self.assertEqual(plan_tasks(request([task(cost=.01)]))['decisions'][0]['decision'],'BUDGET_LIMIT')
    def test_budget_can_propose_but_not_execute(self):
        v=request([task(cost=.25)]);v['limits']['max_usd']=.25
        r=plan_tasks(v);self.assertEqual(r['projected_cost_usd'],.25);self.assertFalse(r['execution_performed'])
    def test_tool_calls_zero_blocks_even_readonly(self):
        v=request();v['limits']['max_tool_calls']=0
        self.assertEqual(plan_tasks(v)['decisions'][0]['decision'],'STEP_OR_TOOL_LIMIT')
    def test_step_limit_one(self):
        v=request([task('x'),task('y')]);v['limits']['max_steps']=1
        self.assertEqual([x['decision'] for x in plan_tasks(v)['decisions']].count('CANDIDATE_READ_ONLY_NOT_AUTHORIZED'),1)
    def test_boolean_budget_fails(self):
        v=request();v['limits']['max_usd']=True
        self.assertRaises(InvalidPlan,plan_tasks,v)
    def test_nan_fails(self):
        v=request();v['tasks'][0]['confidence']=float('nan')
        self.assertRaises(InvalidPlan,plan_tasks,v)
    def test_inf_fails(self):
        v=request();v['tasks'][0]['effort']=float('inf')
        self.assertRaises(InvalidPlan,plan_tasks,v)
    def test_negative_cost_fails(self):
        v=request([task(cost=-1)])
        self.assertRaises(InvalidPlan,plan_tasks,v)
    def test_unknown_gate_raises(self):
        v=request();v['gates']['G0']='GO'
        self.assertRaises(InvalidPlan,plan_tasks,v)
    def test_forged_production_gate_raises(self):
        v=request();v['gates']['production']='ACTIVE'
        self.assertRaises(InvalidPlan,plan_tasks,v)
    def test_unexpected_task_field_raises(self):
        v=request();v['tasks'][0]['command']='rm -rf .'
        self.assertRaises(InvalidPlan,plan_tasks,v)
    def test_unexpected_request_field_raises(self):
        v=request();v['authorized']=True
        self.assertRaises(InvalidPlan,plan_tasks,v)
    def test_deterministic_order_and_digest(self):
        v=request([task('z'),task('a')]);a=plan_tasks(v);b=plan_tasks(v)
        self.assertEqual(a,b);self.assertEqual([d['id'] for d in a['decisions']],['a','z'])
    def test_never_echoes_user_task_data(self):
        v=request([task('safe')]);text=json.dumps(plan_tasks(v))
        self.assertNotIn('command',text);self.assertNotIn('secrets',text)
    def test_expected_eight_roles(self):
        from agent_workflow_planner import ALLOWED_ROLES
        self.assertEqual(len(ALLOWED_ROLES),8)
    def test_unknown_completed_fails(self):
        v=request();v['completed']={'OTHER':'a'*64}
        self.assertRaises(InvalidPlan,plan_tasks,v)
    def test_request_non_dict_fails(self):
        self.assertRaises(InvalidPlan,plan_tasks,[])
    def test_cost_cap_prioritization(self):
        v=request([task('a',cost=.5),task('b',cost=.5)]);v['limits']['max_usd']=.5
        r=plan_tasks(v);self.assertEqual([d['decision'] for d in r['decisions']],['CANDIDATE_READ_ONLY_NOT_AUTHORIZED','BUDGET_LIMIT'])
    def test_zero_budget_rejects_tiny_positive_cost(self):
        v=request([task(cost=1e-10)])
        self.assertEqual(plan_tasks(v)['decisions'][0]['decision'],'BUDGET_LIMIT')
    def test_tiny_cost_not_hidden_by_reporting_roundoff(self):
        v=request([task(cost=1e-10)]);v['limits']['max_usd']=1e-10
        r=plan_tasks(v)
        self.assertEqual(r['decisions'][0]['decision'],'CANDIDATE_READ_ONLY_NOT_AUTHORIZED')
        self.assertEqual(r['projected_cost_usd'],1e-10)
    def test_decimal_budget_sum_does_not_false_reject(self):
        v=request([task('a',cost=.1),task('b',cost=.2)])
        v['limits']['max_usd']=.3
        r=plan_tasks(v)
        self.assertEqual([x['decision'] for x in r['decisions']], ['CANDIDATE_READ_ONLY_NOT_AUTHORIZED']*2)
        self.assertEqual(r['projected_cost_usd'],.3)
    def test_extremely_tiny_effort_does_not_generate_infinity(self):
        v=request();v['tasks'][0]['effort']=1e-320
        self.assertRaises(InvalidPlan,plan_tasks,v)
    def test_huge_integer_fails_closed_not_overflow_exception(self):
        v=request();v['tasks'][0]['impact']=10**1000
        self.assertRaises(InvalidPlan,plan_tasks,v)
    def test_cli_error_no_secrets_leaked(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'input.json';p.write_text('{"secret":"TOP_SECRET"')
            output=io.StringIO()
            with contextlib.redirect_stdout(output):rc=main(['--request',str(p)])
            self.assertEqual(rc,2);self.assertIn('SAFE_STOP',output.getvalue());self.assertNotIn('TOP_SECRET',output.getvalue())
    def test_cli_good_nonacceptance(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'input.json';p.write_text(json.dumps(request()))
            out=io.StringIO()
            with contextlib.redirect_stdout(out): rc=main(['--request',str(p)])
            self.assertEqual(rc,0);self.assertEqual(json.loads(out.getvalue())['production'],'HOLD')

if __name__ == '__main__': unittest.main()
