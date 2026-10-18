# Hermes Cloud — شروط قبول قابلة للاختبار

| البوابة | اختبار النجاح الحقيقي | الحالة |
|---|---|---|
| هوية السحابة والتكلفة | PROJECT_ID وIAM وفوترة وكلفة موثقة وموافقة | HOLD |
| البنية وSSH | Terraform plan مراجع، IAP/OS Login؛ لا Gateway عام | HOLD |
| مصدر Hermes | فرق fork/نسخة Windows، مراجعة installer وcommit مثبت | HOLD |
| أسرار Gemini | 0600 أو secret store؛ اختبار تسرب المفتاح في السجلات/Git | HOLD |
| استجابة النموذج | اختبار prompt واحد بلا إجراء خارجي وقياس كلفته | HOLD |
| Fail-closed | أربعة اختبارات حقيقية: timeout، empty، malformed، network loss وكلها رفض | HOLD |
| استعادة كاملة | نسخة مشفرة، استخراج معزول، وتشغيل Hermes المستعاد فعليًا | HOLD |
| استمرار الخدمة | systemd scope واحد وإعادة تشغيل VM وتحقق Gateway | HOLD |
| Recovery | حفظ نية كل عملية، ومصالحة UNKNOWN دون إعادة تلقائية | HOLD |
| Acceptance evidence | سجل قرار/مصدر/نتيجة مستقل لكل نجاح | HOLD |
| حدود التكلفة | حدود خطوات/توكنات/استدعاءات واختبار إيقاف فعلي | HOLD |

## سياسة P1 الصارمة

كل عملية مؤثرة تسجل Intent متينًا قبل التنفيذ؛ الحالات المسموحة PENDING/RUNNING/SUCCEEDED/FAILED/UNKNOWN. حالة UNKNOWN تتطلب إيقافًا آمنًا ومراجعة بشرية، دون retries تلقائية. يراقب watchdog حياة العملية وتقدم المهام والموارد وحالة الأدوات الفرعية ضمن حدود محددة. لا تُحذف الأدلة عند recovery.

## تأجيل الميزات

GraphRAG والرادار التجاري وربط الشحنات وMCP والإضافات المستجدة جزء P2/P3 تصميميًا فقط إلى أن تجتاز P0/P1. لا تستبدل أو تعيد هيكلة Hermes الموجود على Windows خلال التحصين.

## الوضع

PRODUCTION_READY=NO وPRODUCTION_APPROVED=NO وCLOUD_DEPLOYED=NO حتى تظهر أدلة مباشرة مستقلة. هذه الوثيقة ليست محرك تحكم أو اختبارًا فعليًا.
