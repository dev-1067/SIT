import { useRef, useState } from "react";
import { VEHICLE_PRESETS, CUSTOM_BRAND_KEY } from "../data/vehiclePresets";
import {
  IconGauge,
  IconBolt,
  IconUpload,
  IconTrash,
  IconBook,
  IconChevronRight,
  IconLogout,
} from "./Icons";

function VehicleChip({ manual, onSelect }) {
  return (
    <button
      onClick={() => onSelect(manual)}
      title="Set as target vehicle"
      className="group inline-flex items-center gap-1 bg-zinc-100 dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 text-zinc-700 dark:text-zinc-200 text-xs font-medium pl-2.5 pr-1.5 py-1 rounded-full mr-1.5 mb-1.5 hover:border-amber-400 hover:text-amber-700 dark:hover:text-amber-300 transition"
    >
      {manual.brand} {manual.model} ({manual.year})
      <IconChevronRight className="w-3 h-3 opacity-40 group-hover:opacity-100 transition" />
    </button>
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
  onSelectVehicle,
  user,
  onLogout,
  busyKey,
}) {
  const fileInputRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [customBrand, setCustomBrand] = useState(false);

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

  const handleBrandSelect = (value) => {
    if (value === CUSTOM_BRAND_KEY) {
      setCustomBrand(true);
      return;
    }
    setCustomBrand(false);
    const preset = VEHICLE_PRESETS.find((p) => p.brand === value);
    setBrand(value);
    if (preset) setVehicleModel(preset.models[0]);
  };

  const currentPreset = VEHICLE_PRESETS.find((p) => p.brand === brand);

  return (
    <aside className="w-full lg:w-80 shrink-0 bg-zinc-950 text-zinc-100 h-full overflow-y-auto">
      <div className="p-5 space-y-6">
        <div>
          <h2 className="font-display text-lg font-bold flex items-center gap-2">
            <IconGauge className="w-5 h-5 text-amber-400" />
            Console
          </h2>
        </div>

        {/* 1. AI Engine & Model */}
        <section>
          <h3 className="text-xs font-semibold text-zinc-400 uppercase tracking-widest mb-2">
            01 · Engine &amp; Model
          </h3>
          <label className="block text-xs font-medium text-zinc-500 mb-1">Provider</label>
          <select
            className="w-full rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:ring-2 focus:ring-amber-500"
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
          >
            {Object.entries(providers || {}).map(([key, info]) => (
              <option key={key} value={key}>
                {info.label}
              </option>
            ))}
          </select>

          <label className="block text-xs font-medium text-zinc-500 mt-3 mb-1">Model</label>
          <select
            className="w-full rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:ring-2 focus:ring-amber-500"
            value={model}
            onChange={(e) => setModel(e.target.value)}
          >
            {models.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </section>

        <hr className="border-zinc-800" />

        {/* 2. Target Vehicle Details */}
        <section>
          <h3 className="text-xs font-semibold text-zinc-400 uppercase tracking-widest mb-2">
            02 · Target Vehicle
          </h3>
          <div className="space-y-2">
            <div>
              <label className="block text-xs font-medium text-zinc-500 mb-1">Brand</label>
              {customBrand ? (
                <input
                  autoFocus
                  className="w-full rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:ring-2 focus:ring-amber-500"
                  value={brand}
                  onChange={(e) => setBrand(e.target.value)}
                  onBlur={() => !brand && setCustomBrand(false)}
                />
              ) : (
                <select
                  className="w-full rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:ring-2 focus:ring-amber-500"
                  value={VEHICLE_PRESETS.some((p) => p.brand === brand) ? brand : CUSTOM_BRAND_KEY}
                  onChange={(e) => handleBrandSelect(e.target.value)}
                >
                  {VEHICLE_PRESETS.map((p) => (
                    <option key={p.brand} value={p.brand}>
                      {p.brand}
                    </option>
                  ))}
                  <option value={CUSTOM_BRAND_KEY}>Other (type your own)…</option>
                </select>
              )}
            </div>
            <div>
              <label className="block text-xs font-medium text-zinc-500 mb-1">Model</label>
              {currentPreset ? (
                <select
                  className="w-full rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:ring-2 focus:ring-amber-500"
                  value={currentPreset.models.includes(vehicleModel) ? vehicleModel : CUSTOM_BRAND_KEY}
                  onChange={(e) =>
                    e.target.value === CUSTOM_BRAND_KEY ? setVehicleModel("") : setVehicleModel(e.target.value)
                  }
                >
                  {currentPreset.models.map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                  <option value={CUSTOM_BRAND_KEY}>Other (type your own)…</option>
                </select>
              ) : (
                <input
                  className="w-full rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:ring-2 focus:ring-amber-500"
                  value={vehicleModel}
                  onChange={(e) => setVehicleModel(e.target.value)}
                />
              )}
              {currentPreset && !currentPreset.models.includes(vehicleModel) && (
                <input
                  autoFocus
                  placeholder="Custom model name"
                  className="mt-2 w-full rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:ring-2 focus:ring-amber-500"
                  value={vehicleModel}
                  onChange={(e) => setVehicleModel(e.target.value)}
                />
              )}
            </div>
            <div>
              <label className="block text-xs font-medium text-zinc-500 mb-1">Year</label>
              <input
                className="w-full rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 focus:outline-none focus:ring-2 focus:ring-amber-500"
                value={year}
                onChange={(e) => setYear(e.target.value)}
              />
            </div>
          </div>
        </section>

        <hr className="border-zinc-800" />

        {/* 3. Knowledge Base & Manuals */}
        <section>
          <h3 className="text-xs font-semibold text-zinc-400 uppercase tracking-widest mb-2">
            03 · Knowledge Base
          </h3>
          <p className="text-xs text-zinc-500 mb-2">Embeddings run locally — no API key needed for indexing.</p>

          <input
            ref={fileInputRef}
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
            className="block w-full text-xs text-zinc-400 file:mr-3 file:py-2 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-zinc-800 file:text-amber-300 hover:file:bg-zinc-700"
          />
          <button
            onClick={handleUploadClick}
            disabled={!selectedFile || busyKey === "upload"}
            className="mt-2 w-full inline-flex items-center justify-center gap-2 rounded-lg bg-amber-500 text-zinc-950 font-semibold py-2 hover:bg-amber-400 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-150 hover:shadow-md active:scale-[0.98] disabled:active:scale-100"
          >
            <IconUpload className="w-4 h-4" />
            {busyKey === "upload" ? "Indexing…" : "Process & Index PDF"}
          </button>

          <div className="mt-4 space-y-2">
            {preloadedManuals?.map((pm) => (
              <button
                key={pm.key}
                onClick={() => onPreloadManual(pm.key)}
                disabled={busyKey === pm.key}
                className={`w-full flex items-center gap-2 text-left rounded-lg border px-3 py-2 text-xs font-medium transition-all duration-150 hover:shadow-md active:scale-[0.98] disabled:active:scale-100 ${
                  pm.loaded
                    ? "border-emerald-700 bg-emerald-500/10 text-emerald-300 hover:bg-emerald-500/20"
                    : "border-zinc-700 bg-zinc-900 text-zinc-300 hover:bg-zinc-800"
                } disabled:opacity-50`}
              >
                <IconBolt className="w-3.5 h-3.5 shrink-0" />
                {busyKey === pm.key ? "Indexing…" : pm.loaded ? `Reload ${pm.label}` : `Load ${pm.label}`}
              </button>
            ))}
          </div>
        </section>

        <hr className="border-zinc-800" />

        <section>
          <div className="flex items-center mb-2">
            <h3 className="text-xs font-semibold text-zinc-400 uppercase tracking-widest flex items-center gap-1.5">
              <IconBook className="w-3.5 h-3.5" />
              Registered Vehicles
            </h3>
          </div>
          <div className="flex flex-wrap">
            {manuals && manuals.length > 0 ? (
              manuals.map((m) => <VehicleChip key={m.id} manual={m} onSelect={onSelectVehicle} />)
            ) : (
              <p className="text-xs text-zinc-500">No vehicles indexed yet. Load a sample manual above.</p>
            )}
          </div>

          {manuals && manuals.length > 0 && (
            <button
              onClick={onResetManuals}
              className="mt-3 w-full inline-flex items-center justify-center gap-2 rounded-lg border border-rose-800 text-rose-400 text-xs font-semibold py-2 hover:bg-rose-500/10 transition-all duration-150 hover:shadow-md active:scale-[0.98]"
            >
              <IconTrash className="w-3.5 h-3.5" />
              Reset Database
            </button>
          )}
        </section>

        {user && (
          <>
            <hr className="border-zinc-800" />
            <section className="flex items-center justify-between">
              <div className="min-w-0">
                <p className="text-xs text-zinc-500">Signed in as</p>
                <p className="text-sm font-medium text-zinc-200 truncate" title={user.email}>
                  {user.email}
                </p>
              </div>
              <button
                onClick={onLogout}
                title="Log out"
                className="shrink-0 inline-flex items-center gap-1.5 text-xs font-semibold text-zinc-400 hover:text-rose-400 border border-zinc-700 hover:border-rose-800 rounded-lg px-3 py-2 transition-all duration-150 hover:shadow-md active:scale-[0.98]"
              >
                <IconLogout className="w-3.5 h-3.5" />
                Log out
              </button>
            </section>
          </>
        )}
      </div>
    </aside>
  );
}
