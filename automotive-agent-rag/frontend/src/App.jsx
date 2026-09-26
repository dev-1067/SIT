import { useEffect, useState, useCallback } from "react";
import { api } from "./api/client";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import EvidenceDrawer from "./components/EvidenceDrawer";
import Toast from "./components/Toast";

export default function App() {
  const [health, setHealth] = useState(null);
  const [providers, setProviders] = useState(null);
  const [provider, setProvider] = useState("groq");
  const [model, setModel] = useState("");
  const [brand, setBrand] = useState("Volkswagen");
  const [vehicleModel, setVehicleModel] = useState("Taos");
  const [year, setYear] = useState("2023");

  const [manuals, setManuals] = useState([]);
  const [preloadedManuals, setPreloadedManuals] = useState([]);
  const [busyKey, setBusyKey] = useState(null);

  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [evidenceOpen, setEvidenceOpen] = useState(null);
  const [toast, setToast] = useState(null);
  const [initError, setInitError] = useState(null);

  const showToast = (message, type = "info") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3500);
  };

  const refreshManuals = useCallback(async () => {
    const [manualList, preloadList, healthData] = await Promise.all([
      api.listManuals(),
      api.listPreloadedManuals(),
      api.health(),
    ]);
    setManuals(manualList);
    setPreloadedManuals(preloadList);
    setHealth(healthData);
  }, []);

  useEffect(() => {
    (async () => {
      try {
        const providerData = await api.getProviders();
        setProviders(providerData);
        const firstAvailable = Object.entries(providerData).find(([, v]) => v.available);
        const chosenKey = firstAvailable ? firstAvailable[0] : Object.keys(providerData)[0];
        setProvider(chosenKey);
        setModel(providerData[chosenKey]?.default_model || "");
        await refreshManuals();
      } catch (err) {
        setInitError(err.message || "Could not reach the backend API.");
      }
    })();
  }, [refreshManuals]);

  useEffect(() => {
    if (providers && providers[provider]) {
      setModel(providers[provider].default_model);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [provider]);

  const handlePreloadManual = async (key) => {
    setBusyKey(key);
    try {
      const result = await api.preloadManual(key);
      showToast(`✅ Loaded ${result.manual.brand} ${result.manual.model} (${result.num_chunks} chunks)`, "success");
      await refreshManuals();
    } catch (err) {
      showToast(`❌ ${err.message}`, "error");
    } finally {
      setBusyKey(null);
    }
  };

  const handleUploadManual = async (file) => {
    setBusyKey("upload");
    try {
      const result = await api.uploadManual({ file, brand, model: vehicleModel, year });
      showToast(`✅ Indexed ${result.num_chunks} chunks for ${brand} ${vehicleModel} (${year})`, "success");
      await refreshManuals();
    } catch (err) {
      showToast(`❌ ${err.message}`, "error");
    } finally {
      setBusyKey(null);
    }
  };

  const handleResetManuals = async () => {
    if (!window.confirm("This will permanently delete all indexed manuals. Continue?")) return;
    try {
      await api.resetManuals();
      showToast("Database cleared.", "success");
      await refreshManuals();
    } catch (err) {
      showToast(`❌ ${err.message}`, "error");
    }
  };

  const handleSend = async (text) => {
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);
    try {
      const result = await api.chat({ message: text, provider, model, brand, vehicleModel, year });
      setMessages((prev) => [...prev, { role: "assistant", content: result.answer, evidence: result.evidence }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "assistant", content: `❌ ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  if (initError) {
    return (
      <div className="h-screen flex items-center justify-center bg-slate-100 px-6">
        <div className="max-w-md text-center bg-white border border-rose-200 rounded-2xl shadow-lg p-8">
          <div className="text-4xl mb-3">🚧</div>
          <h1 className="text-lg font-bold text-slate-800 mb-2">Can't reach the backend API</h1>
          <p className="text-sm text-slate-500 mb-1">{initError}</p>
          <p className="text-xs text-slate-400 mt-3">
            Make sure the FastAPI backend is running (see backend/README or run `uvicorn app.main:app`).
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col lg:flex-row overflow-hidden">
      <Sidebar
        providers={providers}
        provider={provider}
        setProvider={setProvider}
        model={model}
        setModel={setModel}
        brand={brand}
        setBrand={setBrand}
        vehicleModel={vehicleModel}
        setVehicleModel={setVehicleModel}
        year={year}
        setYear={setYear}
        manuals={manuals}
        preloadedManuals={preloadedManuals}
        onUploadManual={handleUploadManual}
        onPreloadManual={handlePreloadManual}
        onResetManuals={handleResetManuals}
        health={health}
        busyKey={busyKey}
      />

      <main className="flex-1 min-w-0">
        <ChatWindow
          messages={messages}
          loading={loading}
          onSend={handleSend}
          onShowEvidence={setEvidenceOpen}
          onClear={() => setMessages([])}
          provider={providers?.[provider]?.label || provider}
        />
      </main>

      {evidenceOpen && <EvidenceDrawer evidence={evidenceOpen} onClose={() => setEvidenceOpen(null)} />}
      <Toast toast={toast} />
    </div>
  );
}
