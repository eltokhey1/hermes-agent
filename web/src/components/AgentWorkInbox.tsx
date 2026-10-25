import { useState } from "react";

/**
 * Original, dependency-free agent inbox pilot inspired by affectUI's single-file
 * component approach. Not an affectUI Pro source copy; not mounted in any route.
 * Callbacks navigate to review/detail views: they never authorize execution.
 */
export type AgentWorkStatus =
  | "queued"
  | "running"
  | "needs_review"
  | "done"
  | "failed"
  | "unknown";

export interface AgentWorkItem {
  id: string;
  project: string;
  title: string;
  agent: string;
  status: AgentWorkStatus;
  summary?: string;
  updatedAt?: string;
  costUsd?: number;
}

interface AgentWorkInboxProps {
  items: readonly AgentWorkItem[];
  productionHold?: boolean;
  locale?: "en" | "ar";
  onInspect?: (taskId: string) => void;
  onOpenHumanReview?: (taskId: string) => void;
}

const css = `
.aui-inbox {
  --aui-fg: var(--midground, #f1f5f9);
  --aui-base: var(--background-base, #152525);
  --aui-line: color-mix(in srgb, var(--aui-fg) 23%, transparent);
  --aui-muted: color-mix(in srgb, var(--aui-fg) 74%, transparent);
  --aui-card: color-mix(in srgb, var(--aui-base) 90%, var(--aui-fg));
  color: var(--aui-fg); font-family: var(--theme-font-sans, system-ui, sans-serif);
  border: 1px solid var(--aui-line); border-radius: var(--theme-radius, 12px);
  padding: clamp(12px, 2vw, 22px); max-width: 100%;
}
.aui-inbox *, .aui-inbox *::before, .aui-inbox *::after { box-sizing: border-box; }
.aui-head { display: flex; justify-content: space-between; align-items: start; gap: 12px; flex-wrap: wrap; }
.aui-inbox h2 { font-size: 1.15rem; font-weight: 700; margin: 0 0 5px; }
.aui-subtitle { color: var(--aui-muted); font-size: .84rem; margin: 0; }
.aui-hold { border: 1px solid currentColor; border-radius: 999px; padding: 5px 10px; font-size: .76rem; font-weight: 700; }
.aui-filters { display: flex; flex-wrap: wrap; gap: 7px; margin-block: 18px 12px; }
.aui-inbox button { font: inherit; cursor: pointer; color: inherit; }
.aui-filter, .aui-action { border: 1px solid var(--aui-line); background: transparent; border-radius: 9px; padding: 7px 11px; font-size: .83rem; }
.aui-filter[aria-pressed="true"] { background: var(--aui-fg); color: var(--aui-base); }
.aui-inbox button:focus-visible, .aui-inbox summary:focus-visible { outline: 3px solid var(--aui-fg); outline-offset: 3px; }
.aui-inbox button:disabled { cursor: not-allowed; opacity: .5; }
.aui-list { list-style: none; padding: 0; margin: 0; display: grid; gap: 9px; }
.aui-item { border: 1px solid var(--aui-line); border-radius: 12px; background: var(--aui-card); min-width: 0; }
.aui-item summary { cursor: pointer; list-style-position: inside; padding: 12px; }
.aui-task-top { display: inline-flex; gap: 8px; align-items: center; flex-wrap: wrap; width: calc(100% - 18px); vertical-align: top; }
.aui-title { font-weight: 650; min-width: 0; overflow-wrap: anywhere; flex: 1 1 180px; }
.aui-state { border: 1px solid var(--aui-line); border-radius: 999px; padding: 2px 7px; font-size: .73rem; white-space: nowrap; }
.aui-meta { color: var(--aui-muted); font-size: .78rem; margin-top: 5px; }
.aui-body { border-top: 1px solid var(--aui-line); padding: 12px; }
.aui-body p { margin: 0 0 12px; overflow-wrap: anywhere; }
.aui-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.aui-empty { color: var(--aui-muted); padding: 16px 5px; }
@media (prefers-reduced-motion: no-preference) {
  .aui-inbox button { transition: background-color .15s ease, opacity .15s ease; }
}
`;

const statusText = {
  en: { queued: "Queued", running: "Running", needs_review: "Needs review", done: "Done", failed: "Failed", unknown: "Unknown" },
  ar: { queued: "بالانتظار", running: "قيد العمل", needs_review: "تحتاج مراجعة", done: "مكتملة", failed: "فشلت", unknown: "غير معروفة" },
} as const;

export function AgentWorkInbox({
  items,
  productionHold = true,
  locale = "en",
  onInspect,
  onOpenHumanReview,
}: AgentWorkInboxProps) {
  const [filter, setFilter] = useState<"all" | AgentWorkStatus>("all");
  const ar = locale === "ar";
  const tabs = [
    { id: "all", title: ar ? "الكل" : "All" },
    { id: "needs_review", title: ar ? "المراجعة" : "Review" },
    { id: "running", title: ar ? "قيد العمل" : "Running" },
    { id: "failed", title: ar ? "الفشل" : "Failed" },
    { id: "done", title: ar ? "المكتملة" : "Done" },
  ] as const;
  const visible = filter === "all" ? items : items.filter((item) => item.status === filter);

  return (
    <section className="aui-inbox" aria-label={ar ? "صندوق مهام الوكلاء" : "Agent work inbox"} dir={ar ? "rtl" : "ltr"}>
      <style>{css}</style>
      <header className="aui-head">
        <div>
          <h2>{ar ? "صندوق مهام الوكلاء" : "Agent work inbox"}</h2>
          <p className="aui-subtitle">{ar ? "عرض المهام؛ المراجعة البشرية منفصلة عن التفويض" : "Task visibility; human review is separate from authorization"}</p>
        </div>
        {productionHold && <span className="aui-hold" role="status">PRODUCTION HOLD</span>}
      </header>
      <nav className="aui-filters" aria-label={ar ? "تصفية الحالات" : "Filter tasks"}>
        {tabs.map((tab) => (
          <button type="button" className="aui-filter" key={tab.id} aria-pressed={filter === tab.id}
            onClick={() => setFilter(tab.id)}>
            {tab.title} ({tab.id === "all" ? items.length : items.filter((item) => item.status === tab.id).length})
          </button>
        ))}
      </nav>
      <ul className="aui-list" aria-live="polite">
        {visible.map((item) => (
          <li className="aui-item" key={item.id}>
            <details>
              <summary>
                <span className="aui-task-top">
                  <span className="aui-title">{item.title}</span>
                  <span className="aui-state">{statusText[locale][item.status] ?? statusText[locale].unknown}</span>
                </span>
                <span className="aui-meta">{item.project} · {item.agent}{item.updatedAt ? ` · ${item.updatedAt}` : ""}</span>
              </summary>
              <div className="aui-body">
                <p>{item.summary || (ar ? "لا توجد تفاصيل إضافية." : "No additional details.")}</p>
                {typeof item.costUsd === "number" && Number.isFinite(item.costUsd) && item.costUsd >= 0 && (
                  <p className="aui-meta">{ar ? "التكلفة المسجلة" : "Reported cost"}: {new Intl.NumberFormat(locale, { style: "currency", currency: "USD" }).format(item.costUsd)}</p>
                )}
                <div className="aui-actions">
                  <button type="button" className="aui-action" disabled={!onInspect} onClick={() => onInspect?.(item.id)}>
                    {ar ? "عرض التفاصيل" : "Inspect"}
                  </button>
                  {item.status === "needs_review" && (
                    <button type="button" className="aui-action" disabled={!onOpenHumanReview}
                      onClick={() => onOpenHumanReview?.(item.id)}>
                      {ar ? "فتح المراجعة البشرية" : "Open human review"}
                    </button>
                  )}
                </div>
              </div>
            </details>
          </li>
        ))}
        {visible.length === 0 && <li className="aui-empty">{ar ? "لا توجد مهام في هذه الحالة." : "No tasks in this status."}</li>}
      </ul>
    </section>
  );
}
