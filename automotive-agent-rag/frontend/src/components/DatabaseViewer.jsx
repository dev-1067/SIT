import { useState } from "react";
import { IconX, IconDatabase, IconCheck, IconAlert } from "./Icons";

export default function DatabaseViewer({ health, manuals, onClose }) {
  const [showRaw, setShowRaw] = useState(false);
  const isMongo = health?.storage_backend === "mongodb";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-zinc-950/60" onClick={onClose} />
      <div className="relative w-full max-w-3xl max-h-[85vh] overflow-y-auto rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-2xl animate-[fadein_0.15s_ease-out]">
        <div className="sticky top-0 bg-white dark:bg-zinc-900 border-b border-zinc-200 dark:border-zinc-800 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <IconDatabase className="w-5 h-5 text-amber-600 dark:text-amber-400" />
            <h3 className="font-display font-bold text-zinc-900 dark:text-zinc-100">Manual Store</h3>
          </div>
          <button
            onClick={onClose}
            className="text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200 p-1 rounded-lg"
            aria-label="Close"
          >
            <IconX className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-5">
          <div
            className={`flex items-center gap-3 rounded-xl border px-4 py-3 text-sm ${
              isMongo
                ? "border-emerald-300 bg-emerald-50 text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300"
                : "border-amber-300 bg-amber-50 text-amber-800 dark:border-amber-800 dark:bg-amber-950/40 dark:text-amber-300"
            }`}
          >
            {isMongo ? <IconCheck className="w-4 h-4 shrink-0" /> : <IconAlert className="w-4 h-4 shrink-0" />}
            <div>
              <p className="font-semibold">
                {isMongo ? "Connected to MongoDB" : "Local on-disk fallback active"}
              </p>
              <p className="text-xs opacity-80 mt-0.5">
                {isMongo
                  ? "Manual metadata and PDF files are persisted in MongoDB (GridFS)."
                  : "MongoDB was unreachable at startup, so manuals are persisted in an equivalent on-disk store instead. Set MONGODB_URI in backend/.env and restart to switch to MongoDB."}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3 text-center">
            <div className="rounded-xl border border-zinc-200 dark:border-zinc-800 py-3">
              <p className="text-2xl font-display font-bold text-zinc-900 dark:text-zinc-100">{manuals.length}</p>
              <p className="text-xs text-zinc-500 dark:text-zinc-400">Manuals stored</p>
            </div>
            <div className="rounded-xl border border-zinc-200 dark:border-zinc-800 py-3">
              <p className="text-2xl font-display font-bold text-zinc-900 dark:text-zinc-100">
                {manuals.reduce((sum, m) => sum + (m.num_chunks || 0), 0)}
              </p>
              <p className="text-xs text-zinc-500 dark:text-zinc-400">Indexed chunks</p>
            </div>
            <div className="rounded-xl border border-zinc-200 dark:border-zinc-800 py-3">
              <p className="text-2xl font-display font-bold text-zinc-900 dark:text-zinc-100">
                {manuals.reduce((sum, m) => sum + (m.num_pages || 0), 0)}
              </p>
              <p className="text-xs text-zinc-500 dark:text-zinc-400">Total pages</p>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold text-zinc-600 dark:text-zinc-300 uppercase tracking-wide">
              Stored documents
            </h4>
            <button
              onClick={() => setShowRaw((v) => !v)}
              className="text-xs font-medium text-amber-700 dark:text-amber-400 hover:underline"
            >
              {showRaw ? "Show table" : "Show raw JSON"}
            </button>
          </div>

          {showRaw ? (
            <pre className="text-xs bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl p-4 overflow-x-auto text-zinc-700 dark:text-zinc-300">
              {JSON.stringify(manuals, null, 2)}
            </pre>
          ) : (
            <div className="overflow-x-auto rounded-xl border border-zinc-200 dark:border-zinc-800">
              <table className="w-full text-sm">
                <thead className="bg-zinc-50 dark:bg-zinc-950 text-zinc-500 dark:text-zinc-400 text-xs uppercase">
                  <tr>
                    <th className="text-left px-3 py-2">Vehicle</th>
                    <th className="text-left px-3 py-2">Source</th>
                    <th className="text-left px-3 py-2">Pages</th>
                    <th className="text-left px-3 py-2">Chunks</th>
                    <th className="text-left px-3 py-2">Document ID</th>
                  </tr>
                </thead>
                <tbody>
                  {manuals.map((m) => (
                    <tr key={m.id} className="border-t border-zinc-100 dark:border-zinc-800">
                      <td className="px-3 py-2 text-zinc-800 dark:text-zinc-200 font-medium">
                        {m.brand} {m.model} ({m.year})
                      </td>
                      <td className="px-3 py-2 text-zinc-500 dark:text-zinc-400 capitalize">{m.source}</td>
                      <td className="px-3 py-2 text-zinc-500 dark:text-zinc-400">{m.num_pages}</td>
                      <td className="px-3 py-2 text-zinc-500 dark:text-zinc-400">{m.num_chunks}</td>
                      <td className="px-3 py-2 text-zinc-400 dark:text-zinc-500 font-mono text-xs">{m.id}</td>
                    </tr>
                  ))}
                  {manuals.length === 0 && (
                    <tr>
                      <td colSpan={5} className="px-3 py-6 text-center text-zinc-400">
                        No documents stored yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
