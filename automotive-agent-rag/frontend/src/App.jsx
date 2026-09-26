import { useEffect, useState, useCallback } from "react";
import { api } from "./api/client";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import EvidenceDrawer from "./components/EvidenceDrawer";

import Toast from "./components/Toast";
import { IconAlert } from "./components/Icons";

function getInitialTheme() {
  try {
    const stored = localStorage.getItem("theme");
    if (stored) return stored;
  } catch {
    /* ignore */
  }
  return document.documentElement.classList.contains("dark") ? "dark" : "light";
}

export default function App() {
  const [theme, setTheme] = useState(getInitialTheme);
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

  const toggleTheme = () => {
    setTheme((prev) => {
      const next = prev === "dark" ? "light" : "dark";
      document.documentElement.classList.toggle("dark", next === "dark");
      try {
        localStorage.setItem("theme", next);
      } catch {
        /* ignore */
      }
      return next;
    });
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
      showToast(`Loaded ${result.manual.brand} ${result.manual.model} (${result.num_chunks} chunks)`, "success");
      await refreshManuals();
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setBusyKey(null);
    }
  };

  const handleUploadManual = async (file) => {
    setBusyKey("upload");
    try {
      const result = await api.uploadManual({ file, brand, model: vehicleModel, year });
      showToast(`Indexed ${result.num_chunks} chunks for ${brand} ${vehicleModel} (${year})`, "success");
      await refreshManuals();
    } catch (err) {
      showToast(err.message, "error");
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
      showToast(err.message, "error");
    }
  };

  const handleSelectVehicle = (manual) => {
    setBrand(manual.brand);
    setVehicleModel(manual.model);
    setYear(String(manual.year));
    showToast(`Target vehicle set to ${manual.brand} ${manual.model} (${manual.year})`, "info");
  };

  const handleSend = async (text) => {
    setMessages((prev) => [...prev, { role: "user", content: text, timestamp: Date.now() }]);
    setLoading(true);
    try {
      const result = await api.chat({ message: text, provider, model, brand, vehicleModel, year });
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: result.answer,
          evidence: result.evidence,
          sourceQuestion: text,
          timestamp: Date.now(),
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: err.message, isError: true, sourceQuestion: text, timestamp: Date.now() },
      ]);
    } finally {
      setLoading(false);
    }
  };

  if (initError) {
    return (
      <div className="h-screen flex items-center justify-center bg-zinc-100 dark:bg-zinc-950 px-6">
        <div className="max-w-md text-center bg-white dark:bg-zinc-900 border border-rose-200 dark:border-rose-900 rounded-2xl shadow-lg p-8">
          <IconAlert className="w-10 h-10 text-rose-500 mx-auto mb-3" />
          <h1 className="font-display text-lg font-bold text-zinc-800 dark:text-zinc-100 mb-2">
            Can't reach the backend API
          </h1>
          <p className="text-sm text-zinc-500 dark:text-zinc-400 mb-1">{initError}</p>
          <p className="text-xs text-zinc-400 dark:text-zinc-500 mt-3">
            Make sure the FastAPI backend is running (see backend/README or run `uvicorn app.main:app`).
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col lg:flex-row overflow-hidden bg-zinc-50 dark:bg-zinc-950">
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
        onSelectVehicle={handleSelectVehicle}
        busyKey={busyKey}
      />

      <main className="flex-1 min-w-0">
        <ChatWindow
          messages={messages}
          loading={loading}
          onSend={handleSend}
          onShowEvidence={setEvidenceOpen}
          onClear={() => setMessages([])}
          vehicleLabel={`${brand} ${vehicleModel} (${year})`}
          theme={theme}
          onToggleTheme={toggleTheme}
        />
      </main>

      {evidenceOpen && <EvidenceDrawer evidence={evidenceOpen} onClose={() => setEvidenceOpen(null)} />}

      <Toast toast={toast} />
    </div>
  );
}
