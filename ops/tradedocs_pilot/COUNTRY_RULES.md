# Country / commodity requirements — conservative design

Each transaction must record origin country, export country, import country, commodity and shipment date. For real legal requirements also collect HS code (jurisdiction-specific tariff classification), transit countries, destination port, importer's licenses, product specifications and applicable current official sources.

`requirements_registry.assess(context, documents, rules)` flags missing **recommended** document data as NEEDS_REVIEW, not a legal or LC discrepancy. It only enforces missing documents when a caller supplies a sourced, dated, jurisdiction-and-commodity-specific rule. Current registry ships with **no legal rules**: no jurisdictional compliance claim is made.

Typical document types: invoice, packing list, B/L, origin, inspection, phytosanitary, veterinary/health, insurance, courier receipt. An LC reference is not universally mandatory on every document; enforce it only from operative credit or sourced regulation. A B/L number is not a unique shipment key across all carriers: combine issuer, B/L number, vessel/voyage, dates and container identifiers. MBL vs HBL is separate from payment mechanism.

Future country packs require official source URL, publication date, effective dates, jurisdiction, HS scope, issuer, original/copy rules, legalization requirements, exceptions and independent reviewer approval. The prototype performs no web research or legal certification. No real LC data is included. PRODUCTION=HOLD.
