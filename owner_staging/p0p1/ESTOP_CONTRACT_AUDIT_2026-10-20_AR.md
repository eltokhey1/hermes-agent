# Hermes Open Builder — ESTOP Source Contract, P0/P1 (2026-10-20)

**النتيجة: `OFFLINE_STATIC_ONLY`؛ جميع بوابات G0/G-CODE/G1=`NO-GO`؛ الإنتاج `HOLD`.**

هذه حزمة إضافة مستقلة إلى فرع `owner-staging/p0p1-cloud-local-20261020`، وليست تطبيقًا أو نشرًا على Hermes المحلي. المرجع الموحد: 45 حزمة عمل، 120 معرّف تاريخي، 16 مسارًا؛ لا تنشئ سجلًا بديلًا.

## واقع المصدر الذي روجع (GitHub read-only)

- المستودع: `eltokhey1/hermes-agent`، `main` عند SHA `251e5f7c0a067239655f3421812ab7492a206065` وقت القراءة.
- `agent/estop.py` Git blob `b7cc51cc5e542d3cfb6a139e78d7287a9add44ba`: `engage()` يكتب ملف ESTOP، `disengage()` يحذفه، `check_paused()` يقرأ الحالة؛ الوصف الصريح يقول إن العمل الجاري **لا يُقتل**.
- `hermes_cli/subcommands/pause.py` Git blob `5b05684a3998ab0d1053e1d64d825085d5696b00`: يعرض للمستخدم أن عمليات in-flight تستمر.
- `tools/environments/docker.py` Git blob `...` لا يُطلب نسخه هنا: القيود الفعلية تعتمد على إعدادات التنفيذ، وليس على نجاح تجربة حاوية Alpine منفصلة.
- `tools/terminal_tool_backends.py`: `docker_network=True` افتراضيًا في بعض مسارات بناء Docker؛ `local` يبقى اختيار التنفيذ الافتراضي في نموذج الإعدادات. فحص الإعداد المحلي سابقًا أشار إلى `local` دون إثبات فعالية الإعداد وقت التشغيل.

## الجديد

- `estop_contract_audit.py`: AST ثابت **دون import أو exec للكود المفحوص**. يتحقق من 7 إشارات بنيوية في مصدر ESTOP وCLI، يرفض الروابط/الملفات الضخمة/اختلاف بصمة Git blob، ويبلغ صراحة بأن hard-cancel وguard عند tool-dispatch غير مثبتين. نتيجة `STATIC_SOURCE_REVIEW_ONLY` تعني أن شكل المصدر مطابق للاختبار البنيوي، **ولا تمنح اعتمادًا أمنيًا**.
- `tests/test_estop_contract_audit.py`: 26 اختبارًا اصطناعيًا إيجابيًا وسلبيًا، تغطي انحراف البصمة، المصدر الناقص، جمل تعطيل الحراسة، الحالة المجهولة، وموانع الإنتاج.
- `EVIDENCE.json`: إيصال قابل للتدقيق يُميز الأدلة المباشرة عن اختبارات المختبر المستقلة.

## تشغيل القراءة الثابتة على نسخة مراجعة *منفصلة* (لا على التثبيت الحي)

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
python estop_contract_audit.py \
  --estop-source /STAGED/agent/estop.py \
  --pause-cli /STAGED/hermes_cli/subcommands/pause.py \
  --estop-git-blob-sha1 b7cc51cc5e542d3cfb6a139e78d7287a9add44ba \
  --cli-git-blob-sha1 5b05684a3998ab0d1053e1d64d825085d5696b00
```

بصمات blob أعلاه تخص تحديدًا لقطة `main` المشار إليها، ولن تطابق نسخ Windows القديمة أو المستقبلية بالضرورة. **لا تغير قيمة البصمة لتجاوز الفشل؛ حقق في اختلاف المصدر أولًا.**

## ما يمنع G0/G-CODE/G1

1. لا اختبار فعلي على `C:\Users\m\AppData\Local\hermes\hermes-agent`؛ HEAD هناك `7318e666c236aa8fffc3506c705d1c00a4821441` وقت جرد المستخدم، وقد يختلف تطبيق ESTOP.
2. ESTOP المنفذ حاليًا `pause NEW work` وليس قتلًا للعمل الجاري؛ لا إثبات حراسة جديدة لكل tool dispatch ولا اختبار race بعد إشارة الإيقاف، ولا اختبار إيقاف شبكة/عمليات.
3. تم إثبات Docker 29.8.2 واختبار عزل حاوية منفصلة، وليس عزل Hermes نفسه؛ backend المحلي لوحده ليس بيئة حاوية آمنة.
4. النسخة الاحتياطية المسجلة الأولى (25562 ملفًا) والثانية الجزئية (1811 ملفًا) اجتازتا تحقق المحتوى؛ native backup الكامل غير مثبت بسبب `pending_messages` WinError5، روابط Junction، وضخامة الحجم. الاستعادة الوظيفية الكاملة غير مثبتة.
5. لا تغيير ACL، ولا `hermes resume`/`pause` ولا إعادة تشغيل خدمة أو تنفيذ وكيل ولا Merge/PR/CI production.

## حدود الفحص

الـAST مؤشر بنيوي فقط: قد تنفذ الدوال سلوكًا مختلفًا عند التشغيل؛ وقد تُستدعى أو لا تُستدعى حسب المسار الفعلي. الاختبارات الـ26 لا تستورد Hermes الأصلي ولا تشغله. مراجعة تشغيلية مستقلة مطلوبة لإثبات أن ESTOP يسبق كل تنفيذ ذي أثر وأن الإلغاء يوقف الجاري بصورة موثقة.
