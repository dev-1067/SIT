import { useEffect, useState } from "react";
import { api } from "../api/client";
import { IconX, IconCheck, IconAlert, IconRefresh } from "./Icons";

const STATUS_STYLE = {
  ok: {
    label: "Authenticated",
    box: "border-emerald-300 bg-emerald-50 text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300",
    Icon: IconCheck,
  },
  invalid: {
    label: "Rejected by provider",
    box: "border-rose-300 bg-rose-50 text-rose-800 dark:border-rose-800 dark:bg-rose-950/40 dark:text-rose-300",
    Icon: IconX,
  },
  missing: {
    label: "No key configured",
    box: "border-zinc-300 bg-zinc-50 text-zinc-600 dark:border-zinc-700 dark:bg-zinc-800/60 dark:text-zinc-300",
    Icon: IconAlert,
  },
  network_error: {
    label: "Could not reach provider from this server",
    box: "border-amber-300 bg-amber-50 text-amber-800 dark:border-amber-800 dark:bg-amber-950/40 dark:text-amber-300",
    Icon: IconAlert,
  },
  error: {
    label: "Unexpected response",
    box: "border-amber-300 bg-amber-50 text-amber-800 dark:border-amber-800 dark:bg-amber-950/40 dark:text-amber-300",
    Icon: IconAlert,
  },
};

export default function KeyVerifyPanel({ providers, onClose }) {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);

  const runCheck = async () => {
    setLoading(true);
    try {
      const data = await api.verifyProviders();
      setResults(data);
    } catch {
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runCheck();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-zinc-950/60 animate-[fadein_0.15s_ease-out]" onClick={onClose} />
      <div className="relative w-full max-w-lg max-h-[85vh] overflow-y-auto rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-2xl animate-[fadein_0.15s_ease-out]">
        <div className="sticky top-0 bg-white dark:bg-zinc-900 border-b border-zinc-200 dark:border-zinc-800 px-6 py-4 flex items-center justify-between">
          <h3 className="font-display font-bold text-zinc-900 dark:text-zinc-100">API Key Check</h3>
          <div className="flex items-center gap-2">
            <button
              onClick={runCheck}
              disabled={loading}
              title="Re-check"
              className="text-zinc-400 hover:text-amber-600 dark:hover:text-amber-400 p-1 rounded-lg transition-all duration-150 hover:scale-110 active:scale-90 disabled:opacity-40 disabled:active:scale-100"
            >
              <IconRefresh className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            </button>
            <button onClick={onClose} className="text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200 p-1 rounded-lg transition-all duration-150 hover:scale-110 active:scale-90">
              <IconX className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="p-6 space-y-3">
          <p className="text-xs text-zinc-500 dark:text-zinc-400 -mt-2 mb-2">
            Makes one real, free "list models" call per configured provider directly from this server, so you can
            confirm each key actually authenticates.
          </p>
          {loading && !results && <p className="text-sm text-zinc-500">Checking…</p>}
          {results &&
            Object.entries(results).map(([key, result]) => {
              const style = STATUS_STYLE[result.status] || STATUS_STYLE.error;
              const Icon = style.Icon;
              const label = providers?.[key]?.label || key;
              return (
                <div key={key} className={`rounded-xl border px-4 py-3 text-sm ${style.box}`}>
                  <div className="flex items-center justify-between">
                    <span className="font-semibold flex items-center gap-2">
                      <Icon className="w-4 h-4 shrink-0" />
                      {label}
                    </span>
                    <span className="text-xs font-medium">{style.label}</span>
                  </div>
                  {result.key_preview && (
                    <p className="mt-1 font-mono text-xs opacity-80">{result.key_preview}</p>
                  )}
                  <p className="mt-1 text-xs opacity-80">{result.detail}</p>
                </div>
              );
            })}
        </div>
      </div>
    </div>
  );
}
