# Hermes Cloud — خطة مراجعة ونشر آمن (P0/P1)

**الحالة: DESIGN / LOCAL_PREPARED / CLOUD_NOT_DEPLOYED / PRODUCTION_NOT_APPROVED**

هذه وثيقة تحضير فقط؛ لا تنفّذ أي نشر، ولا تثبت أن Hermes على Windows مطابق لهذا المستودع. افحص فرق النسخ والـcommit المحدد قبل تغيير أي بيئة.

## الهدف

تشغيل Hermes Agent على Google Compute Engine (Ubuntu 24.04)، بتخزين دائم، باستخدام Gemini API من Google AI Studio، وببوابة محمية لا تُعرَّض علنًا. يستمر تشغيله عند إغلاق الكمبيوتر، بشرط نجاح اختبارات إعادة تشغيل الخادم والخدمة فعليًا.

## قواعد التنفيذ

1. تأكد من Google Cloud PROJECT_ID وهوية المستخدم وIAM وحساب الفوترة؛ لا تعتبر authuser=2 هو معرّف مشروع.
2. راجع تكلفة VM/القرص/IPv4/المرور وGemini بالمنطقة الفعلية. تنبيهات الميزانية ليست سقف صرف مضمونًا.
3. جهز Terraform plan بدون apply؛ راجع firewall وOS Login وIAP SSH ومخزن Terraform state. إنشاء أي مورد مدفوع يتطلب مراجعة التكلفة والموافقة.
4. استخدم حساب تشغيل غير root وصلاحيات ضيقة. راجع سكربت التثبيت الخارجي وبصمته والتغييرات مقارنة بالنسخة المحلية قبل تثبيته.
5. أدخل GOOGLE_API_KEY فقط على خادم موثوق وفي مخزن أسرار مؤمّن؛ لا تحفظه هنا أو في GitHub أو tfvars أو state.
6. ابدأ باختبار محادثة واحدة غير مؤثرة في CLI. لا تشغّل أدوات خارجية أو cron أو رسائل أو مشتريات افتراضيًا.
7. جهز Gateway وفق أوامر الإصدار المثبت، واستخدم systemd بنطاق واحد فقط، ثم اختبر التشغيل بعد reboot.
8. اختبر fail-closed والموازنة والأدلة والنسخ والاستعادة التشغيلية على بيئة معزولة قبل الموافقة على الإنتاج.

## بوابات P0/P1

انظر [المصفوفة الأمنية](P0_P1_SECURITY_AR.md). يجب تسجيل أدلة تدعم PASS لكل بوابة، وإلا النتيجة HOLD. الحالة الحالية كلها HOLD حيث لم يُنشر الخادم.

## مصادر أساسية

- https://hermes-agent.nousresearch.com/docs/guides/google-gemini
- https://hermes-agent.nousresearch.com/docs/user-guide/messaging
- https://cloud.google.com/iap/docs/using-tcp-forwarding
- https://cloud.google.com/billing/docs/how-to/budgets

**لا تدمج هذا المستند باعتباره تصريح تشغيل إنتاجي.**
