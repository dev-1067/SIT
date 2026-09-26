import { api } from "../api/client";
import { IconX, IconLayers, IconFile } from "./Icons";

function RelevanceBar({ value }) {
  if (value == null) return null;
  const pct = Math.round(Math.min(Math.max(value, 0), 1) * 100);
  return (
    <div className="flex items-center gap-2">
      <div className="w-16 h-1.5 rounded-full bg-zinc-200 dark:bg-zinc-700 overflow-hidden">
        <div className="h-full bg-amber-500" style={{ width: `${pct}%` }} />
      </div>
      <span className="text-[10px] text-zinc-400">{pct}%</span>
    </div>
  );
}

export default function EvidenceDrawer({ evidence, onClose }) {
  if (!evidence) return null;

  return (
    <div className="fixed inset-0 z-40 flex justify-end">
      <div className="absolute inset-0 bg-zinc-950/40 animate-[fadein_0.15s_ease-out]" onClick={onClose} />
      <div className="relative w-full max-w-md h-full bg-white dark:bg-zinc-900 shadow-2xl overflow-y-auto animate-[slidein_0.2s_ease-out]">
        <div className="sticky top-0 bg-white dark:bg-zinc-900 border-b border-zinc-200 dark:border-zinc-800 px-5 py-4 flex items-center justify-between">
          <h3 className="font-display font-bold text-zinc-900 dark:text-zinc-100 flex items-center gap-2">
            <IconLayers className="w-4 h-4 text-amber-600 dark:text-amber-400" />
            Evidence &amp; Sources
          </h3>
          <button
            onClick={onClose}
            className="text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200 p-1 rounded-lg transition-all duration-150 hover:scale-110 active:scale-90"
            aria-label="Close"
          >
            <IconX className="w-5 h-5" />
          </button>
        </div>

        <div className="p-5 space-y-4">
          {evidence.length === 0 && (
            <p className="text-sm text-zinc-500">No manual sections were retrieved for this answer.</p>
          )}
          {evidence.map((item, idx) => (
            <div key={idx} className="rounded-xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950 p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-amber-700 dark:text-amber-400 bg-amber-100 dark:bg-amber-500/10 px-2 py-0.5 rounded-full">
                  {item.brand} {item.model} ({item.year})
                </span>
                {item.page && <span className="text-xs font-medium text-zinc-500 dark:text-zinc-400">Page {item.page}</span>}
              </div>
              <p className="text-sm text-zinc-700 dark:text-zinc-200 whitespace-pre-wrap leading-relaxed">{item.content}</p>
              <div className="flex items-center justify-between mt-3">
                {item.manual_id && (
                  <a
                    href={`${api.manualFileUrl(item.manual_id)}${item.page ? `#page=${item.page}` : ""}`}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-xs font-semibold text-amber-700 dark:text-amber-400 hover:underline transition-transform duration-150 active:scale-95"
                  >
                    <IconFile className="w-3.5 h-3.5" />
                    Open source{item.page ? ` (p.${item.page})` : ""}
                  </a>
                )}
                <RelevanceBar value={item.relevance} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
