# TradeDocs Global — isolated offline pilot

## Run locally

From the repository root, with Python 3:

```sh
python ops/tradedocs_pilot/local_verify.py
cd ops/tradedocs_pilot
python local_api.py
```

Open `http://127.0.0.1:8765/` on the **same machine**. Stop with Ctrl+C. No account, cloud service, external email, banking API, or production deployment is needed.

The pilot is bound to `127.0.0.1`; its `/review` endpoint accepts JSON only, limits request bodies to 100 KB, and requires the local Host and same-origin browser requests. Do **not** bind it to `0.0.0.0`, reverse-proxy it, or expose it on the public Internet.

## Acceptance checks

1. `local_verify.py` exits with code 0.
2. `GET /health` returns `{"status":"LOCAL_REVIEW_ONLY"}`.
3. In the browser, select each language (English, Arabic, French, Spanish), enter a valid route (e.g. CN/CN/BR, HS 100199 and a valid shipment date), and click Review route.
4. With the synthetic defaults, remaining LC quantity is `700` and remaining face amount is `226800` USD. Status remains `NEEDS_HUMAN_REVIEW`.
5. Invalid country codes, HS codes, amounts, and dates are rejected; malicious Host, foreign Origin, null Origin and non-JSON POST are rejected.
6. Verify that no documents are sent to an external service. Never enter real customer or bank data into this prototype.

## Release gate

**Pilot only — NOT production ready.** CI must pass for the exact candidate commit. Browser manual acceptance, security review, license/dependency checks, and isolation evidence are still required before production. Country regulations and HS classification are **unverified**, and LC utilization is **not a bank-certified balance**. No automatic document approval, payment, external messaging, or shipping update is permitted.

Do not merge to `main` or deploy production until the full Hermes gates are met. An isolated pilot deployment needs a separate threat model and a service suitable for the Python backend; a static HTML host alone will not provide `POST /review`.
