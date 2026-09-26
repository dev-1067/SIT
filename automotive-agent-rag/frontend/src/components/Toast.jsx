import { IconCheck, IconX, IconAlert } from "./Icons";

const STYLES = {
  success: { bg: "bg-emerald-600", Icon: IconCheck },
  error: { bg: "bg-rose-600", Icon: IconX },
  info: { bg: "bg-zinc-800", Icon: IconAlert },
};

export default function Toast({ toast }) {
  if (!toast) return null;
  const { bg, Icon } = STYLES[toast.type] || STYLES.info;
  return (
    <div className="fixed bottom-6 right-6 z-50 animate-[fadein_0.2s_ease-out]">
      <div className={`${bg} text-white text-sm font-medium pl-3 pr-4 py-3 rounded-xl shadow-lg max-w-sm flex items-center gap-2`}>
        <Icon className="w-4 h-4 shrink-0" />
        {toast.message}
      </div>
    </div>
  );
}
