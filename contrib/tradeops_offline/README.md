# TradeOps acceptance contract (isolated proposal)

**Not wired into Hermes, not production ready.** This is a pure Python,
side-effect-free report contract gate. It **does not grant authorization**,
validate the authenticity of documents, retrieve shipping events, or execute
money movement, email, deployment or file operations.

```bash
python -m unittest discover -s contrib/tradeops_offline/tests -v
```

Data classification: synthetic fixtures only. A case report that passes
`inspect_report()` still **requires authenticated human review** and
independent validation of source documents. The only possible value for
`release_authorized` is `False`.

The full offline TradeOps v3 prototype is **not** included in this repository;
this narrow module is provided for safe interface review ahead of P0/P1.
