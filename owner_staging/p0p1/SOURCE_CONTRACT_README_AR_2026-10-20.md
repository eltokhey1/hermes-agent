# Hermes Open Builder — حزمة تدقيق عقود الأمان P0/P1 (إضافة 20 أكتوبر 2026)

**الوضع: `OFFLINE_TESTED_ONLY`؛ لا وصول إلى تثبيت Windows الفعلي ولا اعتماد إنتاجي.**

## النطاق

- `runtime_safety_audit.py`: فحص ثابت محافظ لملف `config.yaml` ووجود علامات ESTOP وأسماء overrides وبصمات أرشيف مشفر عند إدخالها صراحة. لا يطبع أسراراً ولا يقرأ محتوى الملفات المحمية.
- `source_contract_audit.py`: فحص AST محدود/قراءة فقط من مسار مصدر Hermes لملفات `agent/estop.py`, `tools/environments/docker.py`, `tools/terminal_tool_backends.py`. يسجّل SHA-256 لكل ملف قابل للقراءة، ويرصد بنية الواجهات والافتراضات الأمنية القابلة للاستنتاج **دون استيراد الكود أو تنفيذه**.
- `tests/`: 50 اختباراً اصطناعياً/سلبياً تشمل رفض الملفات المفقودة والكبيرة والروابط والبيانات المجهولة، بالإضافة إلى اختبارات فحص الإعدادات. لا تشمل اختبار تعامل Hermes الحقيقي مع Docker أو Windows.

## الأدلة المصدرية أثناء المراجعة

المستودع `eltokhey1/hermes-agent` عند `main` SHA `251e5f7c0a067239655f3421812ab7492a206065`:

1. `agent/estop.py`: `hermes pause` يضع علامة ESTOP وتوثيقه يذكر أن العمل الجاري **لا يُقتل**؛ وقف بدء العمل الجديد لا يكفي ليكون زر إيقاف قاتلاً للأعمال الجارية.
2. `tools/terminal_tool_backends.py`: قيم افتراضية مصدرية تشمل `docker_network=True`, `container_persistent=True`, `docker_persist_across_processes=True`؛ **ليست إثباتاً لإعدادات Windows الفعلية**.
3. `tools/environments/docker.py`: سياسة Docker الأساسية تسقط capabilities ثم تضيف بعضها للحالات المسموح بها؛ وجود `no-new-privileges` في المصدر لا يعني إثبات تفعيله في كل حالة ولا أن الحاوية للقراءة فقط. يجب اختبار سلوك Hermes نفسه.

**تنبيه:** لعدم توافر مستودع Hermes الكامل في بيئة الاختبار الحالية، تم اختبار القواعد على ملفات اصطناعية وليس تشغيل `source_contract_audit.py` على شجرة الإصدار الفعلي. أرقام اختبارات هذه الحزمة لا تثبت التطابق الآلي مع GitHub.

## أوامر المراجعة في بيئة معزولة

```powershell
python -m unittest discover -s .\tests -p "test_*.py" -v
python .\source_contract_audit.py --source-root "C:\Users\m\AppData\Local\hermes\hermes-agent"
python .\runtime_safety_audit.py --hermes-home "$env:LOCALAPPDATA\hermes"
```

هذه الأوامر قراءة فقط في الملفات المحددة؛ لا تستخدم إدخالاً مجهول المصدر في اختبارات تستورد كوداً غير موثوق. احفظ التقارير بعد تنقيحها، ولا ترفع `.env` أو GPG أو أسراراً إلى GitHub.

## حدود القرار

- تجربة Docker Alpine الأساسية المنفذة على Windows سابقاً (`BASIC_ISOLATION_PASS`) هي دليل **لحاوية مستقلة** وليس لتكامل Hermes.
- النسخة المشفرة الأولى verified ضمن نطاق تطوير/legacy، والثانية native critical verified **جزئياً** فقط (1,811 ملفاً)؛ `pending_messages` inaccessible (`WinError 5`)؛ `gateway.heartbeat` متغير؛ لا يوجد دليل backup/functional restore لكل الـ20.9GB.
- طلب نقل التنفيذ من `local` إلى Docker لا يغير إعداداتك تلقائياً، ولا يُستعمل كدليل صلاحية حتى لو أمكن فحص YAML.
- اختبار ESTOP للتوقف عن العمل الجديد **غير كافٍ** دون دليل قطع صلاحيات استدعاء الأدوات وإيقاف الأعمال الجارية، وإقرار بشري مستقل.
- احتفظ بسجل المحافظ الموحد: 45 حزمة و120 معرّفاً تاريخياً و16 مساراً. هذه الحزمة **إضافة أدلة، ليست سجل مهام جديداً**.

`G0=NO-GO` · `G-CODE=NO-GO` · `G1=NO-GO` · `PRODUCTION=HOLD`.
