# Independent isolated re-check of existing Hermes candidates — 2026-10-18

**Verdict: candidate tests PASS in a separate Linux container. Owner Windows P0/P1: UNVERIFIED. Production: HOLD.**

## Environment / provenance

- Re-check date: **2026-10-18 13:55:24 UTC**.
- Environment: temporary isolated Linux directory; Python 3.13.5; Git 2.47.3; no host Windows access, secrets, customer data, Hermes app launch, network test, spending or deployment.
- Source of candidates: existing draft [PR #7](https://github.com/eltokhey1/hermes-agent/pull/7) and [PR #5](https://github.com/eltokhey1/hermes-agent/pull/5), accessed through the connected GitHub account.
- Source integrity: independently copied files' Git blob hashes matched the exact blobs retrieved from both PR branches, listed below.
- This re-check is **not** GitHub Actions CI and does not certify reproducibility on Windows.

## Executed commands and evidence

| Candidate | Reproduction in isolated copy | Observed exit/result | Tests |
|---|---|---|---|
| PR #7 P0 metadata-only inventory | `python -m unittest discover -s . -p test_read_only_inventory.py -v` | exit 0 / OK | 6/6 |
| PR #5 P1/FDE evidence validator | `python -m unittest discover -s tests/scripts -p test_fde_contract_validate.py -v` | exit 0 / OK | 21/21 |
| Both | `python -m py_compile` on four candidate Python files | exit 0 | syntax |

No live Hermes runtime or deployment commands were executed. Unit tests use fabricated temporary fixtures and deliberately generated fake filenames/URLs only.

## Source integrity references

| File | Git blob SHA (matches PR source) | SHA-256 of tested bytes |
|---|---|---|
| PR7 `ops/preflight/read_only_inventory.py` | `f5b8e1366f12dd45d127b5864e2b72f24843e983` | `b2e88a97aae363c24f2f985dfc7ddad697d62135d55a7edbc14f76d3e6fc82fe` |
| PR7 `ops/preflight/test_read_only_inventory.py` | `1d16868aef0cbb7736f8c2c7119cf6b1c865c4e4` | `103cf6232b6e238390b73bde495ac1aeac3aed6fbf0bc772361ad612d4824b76` |
| PR5 `scripts/fde_contract_validate.py` | `9d9901744694a62d4e897545a197d2b8e88b8acb` | `01e2b56449b58818a50652f22ba18c19d69d5ef8630f801cf53c484f9e930d01` |
| PR5 `tests/scripts/test_fde_contract_validate.py` | `1578ee0eb3548e49523082ba67b84dc6ccfe5744` | `631b3a98e0c5c07c3d9c34804a0692eccfdb33d17d06c6e5699b720aac564dfb` |

## Log artifact hashes (kept in this chat's isolated work area)

- `p0_preflight_6tests.log`: SHA-256 `eeda4d30adfd29655b45c8897222ef2b203065bac62ba77362dba1a523b65673`; 788 bytes.
- `p1_evidence_21tests.log`: SHA-256 `70cf98a862ad5a4421e7b3efeb997d37c9082ac5e3c6823bb9299b2f406eb58e`; 2648 bytes.
- Tests report **6** and **21** passing tests, respectively; neither logs nor their hashes prove absence of errors beyond these specified fixtures.

## Real-world gates not passed

- `P0-01`: actual Windows/host identity, working tree and install location **UNVERIFIED**.
- `P0-03/04`: restricted backup **not created or restored** from the owner's actual Hermes install.
- `P0-05/06/07`: actual fail-closed, canary secret leakage and hard spend cap **UNVERIFIED** on target host.
- `P1-01/02/03`: durable pre-effect intent, `UNKNOWN` reconciliation and human approval controls **UNVERIFIED** in target runtime.
- `P1-05/06/07/09`: real target evidence/quality/security and independent go/no-go **UNVERIFIED**.

**No status changes:** Master matrix P0/P1 rows stay `UNVERIFIED`. P2–P4 stay `DESIGN_ONLY`. `PRODUCTION_READY=NO` and `PRODUCTION_APPROVED=NO`. No draft merged or deployment conducted.

## Next admissible execution

After approved operator access to a known Windows checkout: use PR #7 only as a candidate non-executing inventory; preserve any local changes, obtain secure backup, **test real isolated restore**, and only then stage application security/reliability evaluation. Stop on unknown repository identity or any unsafe effect.
