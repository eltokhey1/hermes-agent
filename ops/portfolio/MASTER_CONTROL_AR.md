# Hermes | الخطة المرجعية الموحدة — 2026-10-18

> وثيقة مراجعة فقط: لا تنشر ولا تثبّت أدوات أو مفاتيح أو تتعامل مع بيانات عملاء. الحالة الفعلية لـHermes على Windows غير متحققة؛ P0/P1 ما زالا OPEN، والإنتاج HOLD.

## سجل واحد بلا تكرار
- المرجع التاريخي: `Hermes_Unified_Portfolio_2026-10-18.xlsx`، 16 مسارًا، **45 حزمة عمل موحدة**، مرتبطة بـ **120 معرّف مهمة قديمًا** (61 Master + 59 Portfolio). أبقِ كل معرّف قابلًا للتتبع.
- محفظة أبحاث منفصلة: **20 دراسة منافس** بحالة UNDER_RESEARCH، و **3 أفكار منتجات أصلية** بحالة VALIDATION_BACKLOG. ليست 23 خدمة قيد البرمجة.
- الأنشطة الجديدة NEXT-001..026 نقاط عمل *فرعية* مرتبطة بالحزم الـ45، لا 26 حزمة إضافية.
- لا تُحذف الأدلة السابقة أو تُجمع مراحل P0-P4 مع مراحل التحقق التجاري.

## تقسيم العمل
1. **Hermes Core:** حوكمة وأمن (GOV, P0, P1, SEC)، البوابة MCP/Router والمهارات (ARC)، النشر والسحابة (CLD).
2. **عمليات منفصلة:** TradeOps (TRD)، Maersk وشحنات (SHP)، استخبارات السفن (VES)، Hermes Bridge (BRG)، Viral Kit (VIR)، CRM/Homi (CRM)، Universal Analyzer (ANA)، المحتوى (CNT).
3. **الدخل والاكتشاف:** الرادار (RAD)، التحقق التجاري في السعودية والإمارات (MKT)، TradeDocs ثم ExportLead ثم Shipment Intelligence بوصفها أفكارًا تحتاج إثبات استعداد الدفع.

## تبعيات وإثباتات
| ترتيب | الأولوية | ما يلزم | لا يمكن ادعاؤه |
|---|---|---|---|
| S0 | تنظيم السجل وPRs والمصادر | ربط قديم/جديد وقرارات محدثة | تجهيز docs لا يعني جاهزية |
| S1 | P0 | جرد Windows قراءة فقط؛ backup وrestore فعلي معزول؛ deny timeout/empty/malformed/network؛ synthetic-secret leakage=0؛ سقف $0 وعزل | لا اجتياز بلا نتائج بيئة الهدف |
| S2 | P1 | durable intent قبل كل أثر؛ UNKNOWN لا يعاد تلقائيًا؛ independent evidence؛ bounded watchdog؛ Golden Set وShadow | اختبار mock لا يثبت الاستعادة بعد restart |
| S3 | P2 | SDK رسمي، MCP scopes، بيانات مرخصة، اختبار فعلي لكل client/model | دعم OpenAI/Claude/Gemini/Ollama لم يثبت |
| S4 | P3 | 10 مقابلات + عروض تجربة مدفوعة + تكلفة وحدة فعلية؛ منتج واحد في كل مرة | الإيرادات المدرجة ليست صافي أرباح |
| S5 | P4 | تحسين ذاتي مقاس بعد البوابات | التوسع بلا قياسات محظور |

## حدود تنفيذ
- Use a shared, least-privilege MCP gateway and versioned per-project profiles. iFixAi is a candidate assessor, not an installed security control.
- TrustMRR official MCP: https://trustmrr.com/mcp ; Startups.RIP CLI: https://startups.rip/cli requires explicit licensing/payment approval.
- Do not infer container release from AIS vessel position or ETA.
- Do not use a model-generated yes/no or advisory MCP result as the sole production authorization.
- No autonomous outbound outreach, payment, deletion, repository merge, or customer file processing without a separate trusted approval.
- Keep the user-owned applications in distinct repositories/databases, share specifications/capability contracts only after acceptance tests.

## Review outcome
This PR remains draft and docs-only; merge and deployment are not authorized. Evidence index must distinguish documented/offline/verified remote/verified host/UNKNOWN.

## تحديث التوفيق مع سجل الاعتماد الهندسي (لقطة 2026-10-18)
- مصدر القبول الهندسي PR #4 يضم **32 معيارًا تابعًا** لبوابات Hermes: 18 UNVERIFIED و14 DESIGN_ONLY، لا تُجمع فوق الـ45 حزمة على أنها مهام إضافية.
- قاعدة العمل الجاري WIP ≤ 3: (أ) P0/P1 safety/evidence، (ب) بحث تجاري موثق غير مدفوع، (ج) مراجعة مصدر شحن عند الحاجة. المشاريع الأخرى تصطف ولا تُلغى.
- أول اختبار Windows يجب أن يكون قراءة فقط، ثم backup+actual isolated functional restore؛ بعده إثبات ACL مستقل يمنع Executor من كتابة أو حذف acceptance.db والمجلد الأب، ثم Effect Ledger/UNKNOWN/Recovery Challenge. P0/P1 غير مغلقين.
- أي أثر إنجاز سابق أو عدّ اختبارات من حزمة مستقلة هو دليل محصور ببيئة الاختبار، وليس تصريحًا لإعادة تشغيل أو دمج الإنتاج.
