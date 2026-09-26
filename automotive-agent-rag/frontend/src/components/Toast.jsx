export default function Toast({ toast }) {
  if (!toast) return null;
  const styles = {
    success: "bg-emerald-600",
    error: "bg-rose-600",
    info: "bg-slate-800",
  };
  return (
    <div className="fixed bottom-6 right-6 z-50 animate-[fadein_0.2s_ease-out]">
      <div
        className={`${styles[toast.type] || styles.info} text-white text-sm font-medium px-4 py-3 rounded-xl shadow-lg max-w-sm`}
      >
        {toast.message}
      </div>
    </div>
  );
}
