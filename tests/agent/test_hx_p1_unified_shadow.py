"""Research only: test one original AIAgent turn across MCP/Browser/Inline.

All providers and servers are synthetic; this is NOT production acceptance.
"""

import json
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


def _call(name, args, identity):
    return SimpleNamespace(id=identity, type="function", function=SimpleNamespace(
        name=name, arguments=json.dumps(args)))


def _response(calls=None):
    msg = SimpleNamespace(content="" if calls else "research complete", tool_calls=calls)
    return SimpleNamespace(choices=[SimpleNamespace(message=msg,
        finish_reason="tool_calls" if calls else "stop")], model="test/model", usage=None)


def test_original_agent_single_turn_mcp_browser_inline_denial(tmp_path, monkeypatch):
    from tools.mcp_tool_discovery import register_mcp_servers
    from tools.mcp_tool_lifecycle import shutdown_mcp_servers
    from tools import browser_tool
    from tools import browser_tool_eval_policy as eval_policy
    from tools import browser_tool_session as browser_session
    from run_agent import AIAgent

    child = tmp_path / "server.py"
    child.write_text('''import json,sys,pathlib
root=pathlib.Path(__file__).parent
for line in sys.stdin:
    req=json.loads(line)
    if "id" not in req: continue
    method=req["method"]
    if method=="initialize":
        body={"protocolVersion":req["params"]["protocolVersion"],"capabilities":{"tools":{}},"serverInfo":{"name":"hxshadow","version":"1"}}
    elif method=="tools/list":
        body={"tools":[{"name":"read_evidence","description":"Read synthetic evidence","inputSchema":{"type":"object","properties":{"key":{"type":"string"}},"required":["key"]},"annotations":{"readOnlyHint":True}},{"name":"write_evidence","description":"Write synthetic evidence","inputSchema":{"type":"object","properties":{"key":{"type":"string"}},"required":["key"]},"annotations":{"readOnlyHint":False}}]}
    elif method=="tools/call":
        name=req["params"]["name"]
        with (root/"calls.jsonl").open("a",encoding="utf8") as out: out.write(json.dumps(name)+"\\n")
        body={"content":[{"type":"text","text":"synthetic-evidence:"+name}]}
    else: body={}
    print(json.dumps({"jsonrpc":"2.0","id":req["id"],"result":body}),flush=True)
''', encoding="utf8")
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes-profile"))
    names = sorted(register_mcp_servers({"hxshadow": {
        "command": sys.executable, "args": [str(child)], "timeout": 10}}))
    try:
        assert len(names) == 2, names
        read_name = next(n for n in names if "read_evidence" in n)
        write_name = next(n for n in names if "write_evidence" in n)
        # Browser is intentionally offline: expose its real handler, not a real service.
        # In production this availability is governed by the configured browser backend.
        from tools.registry import invalidate_check_fn_cache
        invalidate_check_fn_cache()
        with (patch("agent.process_bootstrap.OpenAI"),
              patch("agent.model_metadata.fetch_model_metadata", return_value={}),
              patch.object(browser_tool, "check_browser_routed_requirements", return_value=True)):
            agent = AIAgent(model="test/model", api_key="SYNTHETIC_KEY_NO_SERVICE",
                base_url="http://127.0.0.1:1/v1", enabled_toolsets=["mcp-hxshadow", "browser", "todo"],
                max_iterations=3, quiet_mode=True, skip_context_files=True,
                skip_memory=True, save_trajectories=False)
        agent.client = MagicMock()
        agent._cached_system_prompt = "Use only synthetic test tools; never change files."
        agent._use_prompt_caching = False
        agent.compression_enabled = False
        agent.save_trajectories = False
        todo = {"id":"1","content":"Review synthetic-only evidence","status":"pending"}
        # Respect the *actual* Hermes tool surface: MCP is deferred and
        # must use tool_call; browser_click and todo_list are directly listed.
        calls = [
            _call("tool_call",{"calls":[{"name":read_name,"arguments":{"key":"public"}}]},"hx-mcp-read"),
            _call("browser_click",{"ref":"@e1"},"hx-browser-deny"),
            _call("tool_call",{"calls":[{"name":write_name,"arguments":{"key":"protected"}}]},"hx-mcp-write-deny"),
            _call("tool_call",{"calls":[{"name":"todo_list","arguments":{"todos":[todo]}}]},"hx-inline-todo"),
        ]
        agent.client.chat.completions.create.side_effect = [_response(calls),_response()]
        observed_hooks=[]
        def policy_hook(name, args, **kwargs):
            observed_hooks.append(name)
            if name == write_name:
                return "HX_OWNER_APPROVAL_REQUIRED: denied before MCP transport", None
            return None,None
        def forbid_browser_backend(*a, **kw):
            raise AssertionError("private page guard bypassed: browser backend invoked")
        with (patch("hermes_cli.plugins._dispatch_pre_tool_call_hooks",side_effect=policy_hook),
              patch.object(browser_tool,"_is_camofox_mode",return_value=False),
              patch.object(eval_policy,"_eval_ssrf_guard_active",return_value=True),
              patch.object(eval_policy,"_current_page_private_url",return_value="http://169.254.169.254/latest/meta-data/"),
              patch.object(browser_session,"_run_browser_command",side_effect=forbid_browser_backend)):
            result=agent.run_conversation("Read safe MCP evidence; reject private browser and unauthorized MCP write; list a todo.")
        assert result["final_response"] == "research complete", result.get("final_response")
        items=[m for m in result["messages"] if m.get("role")=="tool"]
        assistant = next(m for m in result["messages"] if m.get("tool_calls"))
        expanded_ids = [c["id"] for c in assistant["tool_calls"]]
        assert len(expanded_ids) == 4 and len(set(expanded_ids)) == 4, assistant
        assert {m["tool_call_id"] for m in items} == set(expanded_ids), items
        by_id = {m["tool_call_id"]: m for m in items}
        assert len(by_id) == 4, items
        assert "synthetic-evidence:read_evidence" in by_id["hx-mcp-read"]["content"], by_id["hx-mcp-read"]
        assert "private or internal address" in by_id["hx-browser-deny"]["content"], by_id["hx-browser-deny"]
        assert "HX_OWNER_APPROVAL_REQUIRED" in by_id["hx-mcp-write-deny"]["content"], by_id["hx-mcp-write-deny"]
        assert "Review synthetic-only evidence" in by_id["hx-inline-todo"]["content"], by_id["hx-inline-todo"]
        assert agent._todo_store.snapshot()["todos"]==[todo]
        logfile=tmp_path/"calls.jsonl"
        child_calls=[json.loads(x) for x in logfile.read_text().splitlines()] if logfile.exists() else []
        assert child_calls==["read_evidence"],child_calls
        assert write_name in observed_hooks
        assert "browser_click" in observed_hooks
        print("HX_UNIFIED_TURN=VERIFIED_PARTIAL real_AIAgent+local_stdio_MCP+browser_guard+inline_todo")
        print("HX_MCP_READ=ACTUAL_STDIO; HX_MCP_WRITE=DENIED_BEFORE_TRANSPORT")
        print("HX_BROWSER_PRIVATE_ACTION=DENIED; HX_INLINE_TODO=ACTUAL_IN_MEMORY")
        print("HX_FULL_E2E=NO-GO; HX_EXTERNAL_WITNESS=NOT_VERIFIED; PRODUCTION=HOLD")
    finally:
        shutdown_mcp_servers()
