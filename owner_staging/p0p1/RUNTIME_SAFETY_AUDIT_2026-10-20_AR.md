# Hermes Open Builder — فحص P0 آمن ومحدود (20 أكتوبر 2026)

**الحالة: OFFLINE_TESTED_ONLY — NOT HOST VALIDATED.** هذه أداة تدقيق محافظة لا تصدر موافقة ولا تصلح إعدادات Hermes آليًا.

## ماذا أنجزت
- `runtime_safety_audit.py`: فحص **قراءة فقط** من Python standard library لإعدادات `terminal` في ملف `config.yaml`، ورصد وجود علامة `ESTOP` ومتغيرات البيئة **بالأسماء فقط**، واختيارياً مقارنة بصمة SHA-256 لملفات النسخ الاحتياطية دون فك التشفير.
- `tests/test_runtime_safety_audit.py`: 26 اختباراً اصطناعياً وسلبياً؛ منع كشف قيم مفاتيح التكوين، رفض الاستدلال من YAML المعقد أو القيم المجهولة، رصد `docker_network` وmounts وforwarded env وpersistence وحماية عدم الكتابة.
- `EVIDENCE.json`: حالة الأدلة المبلّغ عنها من جهاز Windows منفصلة عن الأدلة المنفذة في المختبر، مع بوابات الإنتاج المجمّدة.

## تحذيرات مهمة
1. `assess_config` محلل محدود وليس parser YAML كاملاً أو مُقيّم الإعدادات الفعالة. إذا وُجد `HERMES_HOME` أو أي override أو صيغة معقدة فهو يعطي HOLD. لا يستنتج أمان تشغيل فعلي من مجرد `docker_network: false`.
2. `/agent/estop.py` في مراجعة مصدر GitHub (main SHA `251e5f7...`) يوقف بدء **العمل الجديد**، وليس قتل العمل الجاري. وجود علامة `ESTOP` لا يثبت تغطية كل بوابات الإرسال والتنفيذ.
3. النسخ الاحتياطي الأول المحلي verified من تقرير المستخدم، ولم يشمل كامل التثبيت الحقيقي. النسخة الثانية 1,811 ملفاً verified جزئياً، و`pending_messages` يمنع القراءة، و`gateway.heartbeat` استُبعد لتغيّره، والتثبيت الكامل ~20.91 GB غير محفوظ. لا تغيّر ACL/الملكية ولا تستبعد أسراراً من نطاق الاستعادة الوظيفية.
4. **لا تستخدم الأداة لتشغيل الوكيل أو إيقافه.** لا تتصل Docker ولا تستورد برنامج Hermes. لا صلاحية بالدمج أو النشر أو الإنفاق.
5. الـread-only هنا تعني عدم كتابة الملفات بوساطة هذا البرنامج؛ لا تمنع سياسات النظام أو أدوات خارجية من التغيّر ولا تعادل sandbox.

## كيفية الاستخدام في مختبر مستقل (اختياري)
```powershell
python -m unittest discover -s .\tests -p "test_*.py" -v
python .\runtime_safety_audit.py --hermes-home "$env:LOCALAPPDATA\hermes"
```
ويمكن إضافة تحقق بصمة أرشيف معروف مسبقاً، **دون نسخ كلمة المرور إلى الأمر**:
```powershell
python .\runtime_safety_audit.py --hermes-home "$env:LOCALAPPDATA\hermes" --verify-backup "C:\path\to\encrypted-backup.gpg" "EXTERNAL_SHA256_64_HEX"
```
الملف **لن** يُنسخ أو يفكّ تشفيره في هذه العملية. تحقق من SHA من مصدر مستقل.

## فاصل الثقة
- المطلوب للاعتماد: اختبار الاستعادة **الوظيفية** في مسار مستقل؛ معالجة أو عزل `pending_messages` بواسطة مالك النظام دون تجاوز أمانه؛ فحص حاوية Hermes الحقيقية بما يشمل mounts/env/capabilities/egress؛ إلغاء العمل الجاري ESTOP؛ اختبارات آثار فعلية وقبول مستقل.
- `G0=NO-GO`، `G-CODE=NO-GO`، `G1=NO-GO`، `PRODUCTION=HOLD`.
- مرجعية المحافظات: **45 work packages / 120 legacy IDs / 16 streams** في المصنف الموحد القائم. لا ينشئ هذا الإصدار سجل مهام موازياً ولا يغير حالات العمل هناك.
