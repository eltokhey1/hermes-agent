# LC utilization — quantity and money

Use `lc_balance.calculate(lc, shipments)` with synthetic/local data. Currency and unit must match across records. Each shipment must have a unique shipment_id, ideally a stable B/L + voyage key. Amounts and quantities use Decimal; PLANNED and CANCELLED do not consume the provisional shipped allocation; SHIPPED, PRESENTED, HONOURED do. Status changes replace the same shipment record, **not** append it again.

Output distinguishes nominal remaining quantity and LC face-value headroom. A +10% quantity tolerance does not automatically increase the LC monetary amount. Never claim the balance equals the issuing bank's available drawing amount. Bank drawings, discrepancies, partial presentations, amendments, interest, charges, and settlement may affect real availability; obtain bank evidence before relying on it. Quantity remaining can be negative and is flagged, not silently clamped. No external integrations or automated writes. PRODUCTION=HOLD.

Example synthetic LC: 1,000 MT / USD 324,000. Shipment B1 300 MT / USD 97,200 and B2 200 MT / USD 64,800 -> shipped 500 MT / USD 162,000; remaining 500 MT / USD 162,000. Tests are synthetic; real bank acceptance not proven.
