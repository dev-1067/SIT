import { api } from "../api/client";

export default function EvidenceDrawer({ evidence, onClose }) {
  if (!evidence) return null;

  return (
    <div className="fixed inset-0 z-40 flex justify-end">
      <div className="absolute inset-0 bg-slate-900/40" onClick={onClose} />
      <div className="relative w-full max-w-md h-full bg-white shadow-2xl overflow-y-auto animate-[slidein_0.2s_ease-out]">
        <div className="sticky top-0 bg-white border-b border-slate-200 px-5 py-4 flex items-center justify-between">
          <h3 className="text-base font-bold text-slate-800">🔎 Evidence &amp; Sources</h3>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-700 text-xl leading-none px-2"
            aria-label="Close"
          >
            ×
          </button>
        </div>

        <div className="p-5 space-y-4">
          {evidence.length === 0 && (
            <p className="text-sm text-slate-500">No manual sections were retrieved for this answer.</p>
          )}
          {evidence.map((item, idx) => (
            <div key={idx} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-indigo-700 bg-indigo-100 px-2 py-0.5 rounded-full">
                  {item.brand} {item.model} ({item.year})
                </span>
                {item.page && (
                  <span className="text-xs font-medium text-slate-500">Page {item.page}</span>
                )}
              </div>
              <p className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">{item.content}</p>
              {item.manual_id && (
                <a
                  href={`${api.manualFileUrl(item.manual_id)}${item.page ? `#page=${item.page}` : ""}`}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 mt-3 text-xs font-semibold text-indigo-600 hover:text-indigo-800"
                >
                  📄 Open source PDF{item.page ? ` (page ${item.page})` : ""}
                </a>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
