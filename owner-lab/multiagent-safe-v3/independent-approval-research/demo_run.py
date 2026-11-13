"""End-to-end inert demo, 2 child processes. Run only in disposable sandbox.

No real human login, production tool, payment, secret provisioning, install,
external destination, or uncontrolled background process. Standard library.
"""
from __future__ import annotations

import hashlib
import multiprocessing as mp
from pathlib import Path
import secrets
import tempfile

from authority import action_hash
from ipc_service import authority_process, request, root_process
from test_identity_research import SyntheticIssuer


def main():
    keys = [secrets.token_bytes(32) for _ in range(6)]
    ctx = mp.get_context("spawn")
    with tempfile.TemporaryDirectory(prefix="hermes-approval-synthetic-") as tmp:
        root_queue, authority_queue = ctx.Queue(), ctx.Queue()
        root = ctx.Process(target=root_process,
                           args=(str(Path(tmp) / "root.sqlite"), keys[0], keys[1], root_queue))
        auth = None
        try:
            root.start()
            root_address = root_queue.get(timeout=15)["root_address"]
            auth = ctx.Process(target=authority_process, args=(
                str(Path(tmp) / "authority.sqlite"), root_address, keys[1],
                keys[2], keys[3], keys[4], keys[5], authority_queue, True))
            auth.start()
            info = authority_queue.get(timeout=15)
            action = {"task_id": secrets.token_hex(16), "effect": "demo.review",
                      "target": "synthetic-only", "input_sha256": hashlib.sha256(b"demo only").hexdigest(),
                      "cost_usd": 0, "environment": "sandbox"}
            def agent(data):
                return request(info["agent_address"], keys[2], data)
            def owner(data):
                return request(info["owner_address"], keys[3], data)
            submitted = agent({"op": "submit", "action": action})
            assert submitted["ok"], submitted
            no_approval = agent({"op": "decide", "task_id": action["task_id"]})
            assert not no_approval["ok"]
            proof = SyntheticIssuer(keys[4]).mint()
            ch_response = owner({"op": "begin_review", "task_id": action["task_id"],
                                 "identity_proof": proof})
            assert ch_response["ok"], ch_response
            challenge = ch_response["data"]["review_challenge"]
            approved = owner({"op": "decide", "task_id": action["task_id"],
                              "expected_hash": action_hash(action), "decision": "approve",
                              "identity_proof": proof, "challenge": challenge,
                              "csrf_echo": challenge})
            assert approved["ok"], approved
            executed = agent({"op": "preview", "task_id": action["task_id"],
                              "expected_hash": action_hash(action)})
            assert executed["ok"] and executed["data"]["external_effects"] is False
            repeated = agent({"op": "preview", "task_id": action["task_id"],
                              "expected_hash": action_hash(action)})
            assert not repeated["ok"]
            print("DEMO_PROCESSES=2")
            print("OWNER_CHANNEL_ISOLATION=PASS")
            print("EXACT_ACTION_HASH=PASS")
            print("SINGLE_USE=PASS")
            print("SYNTHETIC_OWNER_PROOF_ONLY=true")
            print("EXTERNAL_EFFECTS=false")
            print("PRODUCTION=HOLD")
        finally:
            for p in (auth, root):
                if p is not None:
                    if p.is_alive():
                        p.terminate()
                    p.join(timeout=5)
                    if p.is_alive():
                        p.kill(); p.join(timeout=5)

if __name__ == "__main__":
    main()
