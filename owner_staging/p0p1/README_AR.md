# Hermes Open Builder | Cloud → Local P0/P1 Staging

**نسخة تحضيرية: 20 أكتوبر 2026.** الحالة: `OFFLINE_TESTED_ONLY`.

## القرار

Hermes Agent هو المنفّذ الأساسي محليًا، وليس ChatGPT أو Codex أو Work. يمكن للأدوات الأخرى إرسال المهام أو المراجعة فقط. **لا يوجد اتصال مباشر بجهاز Windows في هذه الجلسة**؛ لا تعني هذه الحزمة مزامنة آلية مع الجهاز. كل ما في هذا الأرشيف للتحقق ونسخ الملفات إلى **مجلد تجهيزي جديد** عند توفر الجهاز وبعد اختيار المسار.

- `owner_staging/p0p1/mutation_gate.py`: يتطلب المصدر والـtests وجميع التبعيات المعلنة. ينسخها **لكل طفرة** إلى مجلد مؤقت جديد، يجري baseline، يتحقق من عدد الاختبارات، لا يحتسب `ModuleNotFoundError`/`_FailedTest`/`sqlite3.IntegrityError`/مهلة التنفيذ كطفرة مقتولة. **لا يشغّل على بيانات أو كود غير موثوق ولا خارج sandbox مستقل**.
- `owner_staging/p0p1/local_stage.py`: يتحقق من SHA-256 خارجي ويفحص أسماء ZIP وتصادمات Windows والروابط والحدود الحجمية ثم يستخرج إلى مجلد جديد فقط. لا يثبت شيئًا ولا يغيّر إعدادات Hermes ولا يمسّ المستودع المحلي.
- `owner_staging/p0p1/tests/test_offline.py`: اختبارات اصطناعية/سلبية في Linux. لا تكافئ اختبار تكامل Hermes الحقيقي.
- `GATES_AND_LOCALIZATION_AR.md`: شرح التحقق والاستيراد عند توفر الكمبيوتر.
- `CLOUD_WORK_HANDOFF_AR.md`: تسليم قابل للاستخدام من Codex أو Work، **ليس تنفيذًا مباشرًا لهما**.
- `RELEASE_RECEIPT.json`, `MANIFEST.sha256`: إثبات سلامة هذا التسليم فقط.

## المرجع الواحد

المصنف التاريخي `Hermes_Unified_Portfolio_2026-10-18.xlsx`: 45 حزمة / 120 معرّفًا / 16 مسارًا. الملف الجاري في Library: `/Hermes/Command_Center_2026-10-18/Hermes_Unified_Command_Center_2026-10-18_CURRENT.xlsx`. لا إنشاء Master Tracker جديد، ولا نقل حالات الاعتماد، ولا تنفيذ آلي للمهام التجارية أو إرسال أي بيانات.

## الحدود الصارمة

`G0=NO-GO`, `G-CODE=NO-GO`, `G1=NO-GO`, `PRODUCTION=HOLD`, `SPEND=$0`.

لا توجد اختبارات Windows أو Docker/ESTOP حقيقي أو نسخ واستعادة تشغيلية أو CI معتمد لهذه الحزمة. لا ترسل أسرارًا أو مسارات مستخدم في تقارير الجرد. لا تُنفذ `git reset --hard` أو `git clean` أو `hermes update` أو تغييرات إنتاجية تلقائيًا.

## إجراء سريع في مختبر معزول

```sh
python -m unittest discover -s owner_staging/p0p1/tests -p 'test_*.py' -v
```

بعد فتح Windows: تحقّق من بصمة ZIP من مصدر خارجي، حمّل `local_stage.py` من نفس الإصدار المثبت ببصمته، ثم نفّذ `stage` إلى **مجلد غير موجود مسبقًا**؛ راجع `GATES_AND_LOCALIZATION_AR.md`.
