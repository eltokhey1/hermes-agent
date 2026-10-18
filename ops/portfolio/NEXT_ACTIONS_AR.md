# الأولويات التنفيذية — 26 نقطة عمل فرعية، 2026-10-18

هذه نقاط فرعية مرتبطة بالـ45 حزمة السابقة. **لا تنشئ لها حزمًا مستقلة أو PRs إضافية** دون دليل حاجة.

| المعرف | الحزمة | الإجراء | الحالة/الحاجز |
|---|---|---|---|
| NEXT-001 | GOV-01 | توحيد 120 معرفًا في 45 حزمة مع روابط | DONE_DOCS — offline evidence only |
| NEXT-002 | GOV-02 | التحقق من ملفات PR #9 | DONE_REMOTE_DOCS — draft, not merged |
| NEXT-003 | GOV-03 | مصالحة أدلة جلسات Work السابقة | PENDING_RECONCILIATION |
| NEXT-004 | P0-01 | جرد Windows وDocker وGit قراءة فقط | BLOCKED_HOST |
| NEXT-005 | P0-02 | اختبار الأسرار والصلاحيات وعدم التسريب | BLOCKED_HOST |
| NEXT-006 | P0-03 | نسخة احتياطية واستعادة حقيقية معزولة | BLOCKED_HOST |
| NEXT-007 | P0-04 | رفض الأربع حالات (timeout/empty/malformed/network) | BLOCKED_HOST |
| NEXT-008 | P0-05 | ESTOP وسقف $0 وعزل المستأجرين | BLOCKED_HOST |
| NEXT-009 | P0-06 | قبول P0 من مراجع مستقل | BLOCKED_DEPENDENCIES |
| NEXT-010 | P1-01 | durable intent قبل الأثر الخارجي | BLOCKED_P0 |
| NEXT-011 | P1-02 | UNKNOWN no-retry بعد restart | BLOCKED_P0 |
| NEXT-012 | P1-03 | RBAC / payload/tool/env approvals | BLOCKED_P0 |
| NEXT-013 | P1-05 | Acceptance & Evidence + تقييم iFixAi منفصل | BLOCKED_P0 |
| NEXT-014 | P1-06 | Golden Set/Shadow + human Go/No-Go | BLOCKED_P0 |
| NEXT-015 | ARC-01 | MCP namespaces & capability policy | DESIGN_ONLY |
| NEXT-016 | ARC-02 | اختبارات hosts/models والميزانية | BLOCKED_P1 |
| NEXT-017 | RAD-02 | تحديث 20 مصدرًا لـSaaS وStartups.RIP | READY_RESEARCH |
| NEXT-018 | RAD-03 | إدراج 20 دراسة + 3 أفكار دون تضخيم التنفيذ | DONE_DOCS |
| NEXT-019 | MKT-02 | مقابلات TradeDocs وإشارة دفع | WAITING_COMMERCIAL |
| NEXT-020 | MKT-02 | اختبار عملاء ExportLead بمصادر مرخصة | WAITING_COMMERCIAL |
| NEXT-021 | SHP-01 | تتبع الشحنات بالأحداث المؤرخة من المصادر | PENDING_FRESH_CHECK |
| NEXT-022 | SHP-02 | Carrier/DCSA/AIS مع عدم يقين ETA | BLOCKED_P1 |
| NEXT-023 | VIR-02 | Viral Kit isolation/regression/restore | BLOCKED_HOST |
| NEXT-024 | CRM-01 | Leads 500 root cause + regression | BLOCKED_HOST |
| NEXT-025 | BRG-01 | مقارنة Bridge v0.4 وretention/separation | BLOCKED_HOST |
| NEXT-026 | CLD-01 | دراسة تشغيل السحابة/الميزانية | BLOCKED_P1 |

## كيف تغلق الإجراء؟
الحالة DONE مطلوبة بنطاق محدد وevidence URI وتاريخ وhash أو trace عند وجود تشغيل، مع نتائج الاختبارات السلبية. فتح PR أو نجاح fixture لا يثبت أن الحزمة دخلت الإنتاج.

## روابط المستندات
- Original historical registry: `Hermes_Unified_Portfolio_2026-10-18.xlsx` (Library, not committed).
- Offline control workbook derived: `Hermes_Unified_Command_Center_v2_2026-10-18.xlsx` (generated artifact, not committed).
- This is a GitHub draft review, **not a runtime integration**.
