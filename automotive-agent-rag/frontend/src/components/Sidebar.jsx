import { useRef, useState } from "react";

function VehicleTag({ brand, model, year }) {
  return (
    <span className="inline-flex items-center gap-1 bg-slate-100 border border-slate-300 text-slate-700 text-xs font-medium px-2.5 py-1 rounded-full mr-1.5 mb-1.5">
      🚗 {brand} {model} ({year})
    </span>
  );
}

export default function Sidebar({
  providers,
  provider,
  setProvider,
  model,
  setModel,
  brand,
  setBrand,
  vehicleModel,
  setVehicleModel,
  year,
  setYear,
  manuals,
  preloadedManuals,
  onUploadManual,
  onPreloadManual,
  onResetManuals,
  health,
  busyKey,
}) {
  const fileInputRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);

  const providerInfo = providers?.[provider];
  const models = providerInfo?.models || [];

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files?.[0] || null);
  };

  const handleUploadClick = async () => {
    if (!selectedFile) return;
    await onUploadManual(selectedFile);
    setSelectedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <aside className="w-full lg:w-80 shrink-0 bg-white border-r border-slate-200 h-full overflow-y-auto">
      <div className="p-5 space-y-6">
        <div>
          <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">⚙️ Control Panel</h2>
          {health && (
            <p className="mt-1 text-xs text-slate-500">
              Storage:{" "}
              <span
                className={`font-semibold ${
                  health.storage_backend === "mongodb" ? "text-emerald-600" : "text-amber-600"
                }`}
              >
                {health.storage_backend === "mongodb" ? "MongoDB (connected)" : "Local fallback"}
              </span>
            </p>
          )}
        </div>

        {/* 1. AI Engine & Model */}
        <section>
          <h3 className="text-sm font-semibold text-slate-600 uppercase tracking-wide mb-2">
            1. AI Engine &amp; Model
          </h3>
          <label className="block text-xs font-medium text-slate-500 mb-1">AI Provider</label>
          <select
            className="w-full rounded-lg border border-slate-300 bg-slate-50 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
          >
            {Object.entries(providers || {}).map(([key, info]) => (
              <option key={key} value={key}>
                {info.label} {info.available ? "" : "(no API key)"}
              </option>
            ))}
          </select>

          <label className="block text-xs font-medium text-slate-500 mt-3 mb-1">Model</label>
          <select
            className="w-full rounded-lg border border-slate-300 bg-slate-50 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            value={model}
            onChange={(e) => setModel(e.target.value)}
          >
            {models.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
          {providerInfo && !providerInfo.available && (
            <p className="mt-2 text-xs text-amber-600 bg-amber-50 border border-amber-200 rounded-lg px-2 py-1.5">
              ⚠️ No API key configured for this provider in the server's .env file.
            </p>
          )}
        </section>

        <hr className="border-slate-200" />

        {/* 2. Target Vehicle Details */}
        <section>
          <h3 className="text-sm font-semibold text-slate-600 uppercase tracking-wide mb-2">
            2. Target Vehicle Details
          </h3>
          <div className="space-y-2">
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1">Brand</label>
              <input
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                value={brand}
                onChange={(e) => setBrand(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1">Model</label>
              <input
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                value={vehicleModel}
                onChange={(e) => setVehicleModel(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1">Year</label>
              <input
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                value={year}
                onChange={(e) => setYear(e.target.value)}
              />
            </div>
          </div>
        </section>

        <hr className="border-slate-200" />

        {/* 3. Knowledge Base & Manuals */}
        <section>
          <h3 className="text-sm font-semibold text-slate-600 uppercase tracking-wide mb-2">
            3. Knowledge Base &amp; Manuals
          </h3>
          <p className="text-xs text-slate-400 mb-2">⚡ Embeddings run locally — no API key needed for indexing.</p>

          <input
            ref={fileInputRef}
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
            className="block w-full text-xs text-slate-600 file:mr-3 file:py-2 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
          />
          <button
            onClick={handleUploadClick}
            disabled={!selectedFile || busyKey === "upload"}
            className="mt-2 w-full rounded-lg bg-indigo-600 text-white text-sm font-semibold py-2 hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition"
          >
            {busyKey === "upload" ? "Indexing…" : "📤 Process & Index PDF"}
          </button>

          <div className="mt-4 space-y-2">
            {preloadedManuals?.map((pm) => (
              <button
                key={pm.key}
                onClick={() => onPreloadManual(pm.key)}
                disabled={busyKey === pm.key}
                className={`w-full text-left rounded-lg border px-3 py-2 text-xs font-medium transition ${
                  pm.loaded
                    ? "border-emerald-300 bg-emerald-50 text-emerald-700 hover:bg-emerald-100"
                    : "border-slate-300 bg-slate-50 text-slate-700 hover:bg-slate-100"
                } disabled:opacity-50`}
              >
                {busyKey === pm.key
                  ? "Indexing…"
                  : pm.loaded
                  ? `🔄 Reload ${pm.label}`
                  : `⚡ Load ${pm.label}`}
              </button>
            ))}
          </div>
        </section>

        <hr className="border-slate-200" />

        <section>
          <h3 className="text-sm font-semibold text-slate-600 uppercase tracking-wide mb-2">
            📚 Registered Vehicles
          </h3>
          <div className="flex flex-wrap">
            {manuals && manuals.length > 0 ? (
              manuals.map((m) => <VehicleTag key={m.id} brand={m.brand} model={m.model} year={m.year} />)
            ) : (
              <p className="text-xs text-slate-400">No vehicles indexed yet. Load a sample manual above!</p>
            )}
          </div>

          {manuals && manuals.length > 0 && (
            <button
              onClick={onResetManuals}
              className="mt-3 w-full rounded-lg border border-rose-300 text-rose-600 text-xs font-semibold py-2 hover:bg-rose-50 transition"
            >
              🗑️ Reset Database
            </button>
          )}
        </section>
      </div>
    </aside>
  );
}
