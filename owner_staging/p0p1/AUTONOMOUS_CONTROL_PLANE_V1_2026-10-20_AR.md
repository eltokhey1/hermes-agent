# Hermes Open Builder — Autonomous Agent Control Plane V1 (OFFLINE)

**تاريخ الحزمة: 2026-10-20** | **الحالة: عرض تخطيط غير تنفيذي — P0/P1**

## منبع التصميم
- KodeKloud, Autonomous Agent Frameworks: https://notes.kodekloud.com/docs/AI-Agents/Agent-Architecture-Multi-Agent-Systems/Autonomous-Agent-Frameworks/page
- مبادئ: Sense → Plan → Act → Reflect، طابور مهام، ترتيب الأولويات، ذاكرة، مراقبة، حدود تكلفة ومدة، وموافقة بشرية.
- المصدر الرسمي AutoGen: https://github.com/microsoft/autogen (وضع صيانة). **لا يُثبّت AutoGen أو أي إطار آخر**.

## ما تم تنفيذه
- `agent_workflow_planner.py`: طبقة **تخطيط** نقية بـPython standard library، دون import لـHermes ودون tool-dispatch أو استدعاءات للشبكة/نظام التشغيل.
- ثمانية أدوار موحّدة: `Observer → Verifier → Predictor → Economist → Risk → Planner → Executor → Auditor`؛ **الأسماء فقط** للتصنيف وليست وكلاء عاملين.
- ترتيب `Impact × Confidence × Urgency ÷ Effort`، حد أقصى 45 مهمة (بالتوافق العددي مع 45 work packages المرجعية)، وكشف التكرار والحلقات في الاعتماديات.
- تحقق من الميزانية المخططة وعدد الخطوات واستدعاءات الأدوات؛ ليس حارس تكاليف إنتاجي.
- `ESTOP_HOLD` عند طلب ESTOP؛ منع الإجراءات ذات الأثر (الكتابة/الشبكة/الحذف/المال/الإنتاج)، وعدم منح أي تصريح بالتنفيذ حتى للقراءة فقط.
- إثبات SHA256 شكلي للإنجاز السابق؛ **ليس إثباتًا لصحة محتوى الدليل** ولا يجعل المهمة مكتملة من تلقاء نفسه.
- إخراج تقارير مختصرة بلا محتويات المهمة أو كلمات مرور أو مفاتيح؛ استخدام `SAFE_STOP` عند خلل البنية.
- لا اعتماد للذاكرة الدائمة أو checkpoint آمن أو حراسة تنفيذ أدوات Hermes؛ هذه مهام لاحقة P0/P1.

## التجربة المستقلة
```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python agent_workflow_planner.py --request request.json
```
الاختبار الأول يعمل بلا اتصال وبلا نماذج/مفاتيح. الأمر الثاني يقرأ JSON من المستخدم ويطبع **توصية فقط**. لا يغير أي ملف في Hermes.

مثال لمدخل JSON آمن بلا بيانات حقيقية:
```json
{
  "tasks": [{"id":"P0-EXAMPLE","role":"Observer","action":"READ_ONLY","dependencies":[],"impact":9,"confidence":0.9,"urgency":8,"effort":2,"estimated_cost_usd":0}],
  "completed":{},
  "limits":{"max_usd":0,"max_steps":1,"max_tool_calls":1},
  "estop_engaged":false,
  "gates":{"G0":"NO-GO","G_CODE":"NO-GO","G1":"NO-GO","production":"HOLD"}
}
```

## قبل أي تكامل
1. تجهيز نسخة Windows كاملة واستعادة وظيفية؛ `pending_messages` محمي ولا يجوز تجاوز ACL.
2. إثبات إشراف tool-dispatch وESTOP الجاري وعزل Docker داخل Hermes؛ الاختبار المنفصل لا يكفي.
3. ربط قراءة JSON بسجل العمل المرجعي **45 حزمة/120 معرفًا/16 مسارًا** دون إنشاء سجل بديل، ثم مراجعة بشرية قبل أي صلاحية تنفيذ.
4. استخدام SQLite/checkpoints لاحقًا بعد تصميم التزامن ومطابقة الدليل وقرار منح/سحب الصلاحية، وعدم اعتبار SHA شكليًا دليلًا مستقلًا.

**G0=NO-GO, G-CODE=NO-GO, G1=NO-GO, PRODUCTION=HOLD.**
