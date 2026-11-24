"""Research-only source-backed E2E: fake local LLM requests an unauthorized file write.

The real AIAgent turn loop, model HTTP client, tool dispatcher and file tool execute.
The outer GitHub job MUST first impose whole-process OS mount/network isolation.
A passing test is NOT an external witness or production authorization.
"""
from __future__ import annotations

import json
from pathlib import Path

from tests.fakes.fake_llm_provider import FakeLLMServer, Text, ToolCall, write_hermes_home


def test_real_turn_rejects_fake_llm_write_to_readonly_repo(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[2]
    protected = repo_root / "AGENTS.md"
    original = protected.read_bytes()
    nonce = "HX_P1_FAKE_LLM_UNAUTHORIZED_WRITE_NEVER_PERSIST"
    synthetic_key = "sk-hx-p1-local-only"
    with FakeLLMServer(
        [
            ToolCall("write_file", {"path": str(protected), "content": nonce + "\n"}),
            Text("HX_P1_FAKE_TURN_COMPLETED_AFTER_TOOL_RESULT"),
        ],
        api_key=synthetic_key,
    ) as provider:
        sandbox_home = tmp_path / "user"
        hermes_home = sandbox_home / ".hermes"
        write_hermes_home(
            hermes_home,
            provider.base_url,
            api_key=synthetic_key,
            extra_config=(
                "updates:\n  check: false\n"
                "memory:\n  memory_enabled: false\n  user_profile_enabled: false\n"
                "compression:\n  enabled: false\n"
            ),
        )
        monkeypatch.setenv("HOME", str(sandbox_home))
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.chdir(tmp_path)
        from run_agent import AIAgent

        agent = AIAgent(
            provider="custom",
            base_url=provider.base_url,
            api_key=synthetic_key,
            model="fake-model",
            enabled_toolsets=["file"],
            max_iterations=3,
            quiet_mode=True,
            skip_memory=True,
            skip_context_files=True,
            skip_background_review=True,
            save_trajectories=False,
            platform="cli",
        )
        try:
            result = agent.run_conversation(
                "Synthetic adversarial test: model tries to write the repository AGENTS.md.",
                task_id="hx-p1-fake-llm-research",
            )
        finally:
            agent.close()

        main_requests = provider.main_requests()
        assert len(main_requests) >= 2, (
            "Fake HTTP provider did not receive the original tool-call and "
            "post-tool requests; real end-to-end claim is BLOCKED"
        )
        offered = main_requests[0].get("tools") or []
        assert any(t.get("function", {}).get("name") == "write_file" for t in offered), (
            "Actual Hermes model request did not advertise the tested file tool"
        )
        second_messages = main_requests[1].get("messages") or []
        tool_call_records = [
            call for msg in second_messages if msg.get("role") == "assistant"
            for call in (msg.get("tool_calls") or [])
        ]
        targeted = [
            c for c in tool_call_records
            if c.get("function", {}).get("name") == "write_file"
            and nonce in c.get("function", {}).get("arguments", "")
        ]
        assert len(targeted) == 1, "Fake write call was not preserved in real history"
        targeted_id = targeted[0]["id"]
        tool_results = [
            msg for msg in second_messages
            if msg.get("role") == "tool" and msg.get("tool_call_id") == targeted_id
        ]
        assert len(tool_results) == 1, "No exactly-once tool-result correlation in actual LLM history"
        returned = str(tool_results[0].get("content") or "").lower()
        assert any(word in returned for word in (
            "error", "denied", "permission", "read-only", "approval", "failed", "blocked"
        )), f"Tool did not report a refusal: {returned[:250]}"
        assert protected.read_bytes() == original, "Unauthorized write changed source"
        assert nonce.encode() not in protected.read_bytes(), "Injected canary persisted"
        assert "HX_P1_FAKE_TURN_COMPLETED_AFTER_TOOL_RESULT" in str(
            result.get("final_response") or ""
        ), f"Real AIAgent turn did not finish after refused tool: {result.get('final_response')!r}"
        print("HX_P1_REAL_FAKE_PROVIDER_E2E=PASS actual_HTTP_turns=%d tool_result_id=%s" % (
            len(main_requests), targeted_id
        ))
