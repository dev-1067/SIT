import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import {
  IconCar,
  IconBell,
  IconSnow,
  IconFlame,
  IconBroom,
  IconSend,
  IconCopy,
  IconCheck,
  IconRefresh,
  IconClock,
  IconSun,
  IconMoon,
  IconLayers,
} from "./Icons";

const SAMPLE_PROMPTS = [
  { Icon: IconBell, text: "When will the alarm be triggered?" },
  { Icon: IconSnow, text: "When is the air recirculation mode turned off?" },
  { Icon: IconFlame, text: "When should the seat heating not be turned on?" },
];

function formatTime(ts) {
  return new Date(ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={async () => {
        try {
          await navigator.clipboard.writeText(text);
        } catch {
          /* clipboard unavailable */
        }
        setCopied(true);
        setTimeout(() => setCopied(false), 1500);
      }}
      title="Copy answer"
      className="text-zinc-400 hover:text-amber-600 dark:hover:text-amber-400 transition"
    >
      {copied ? <IconCheck className="w-3.5 h-3.5" /> : <IconCopy className="w-3.5 h-3.5" />}
    </button>
  );
}

function MessageCard({ msg, onShowEvidence, onRegenerate }) {
  const isUser = msg.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] rounded-2xl rounded-tr-sm bg-amber-500 text-zinc-950 px-4 py-3 text-sm leading-relaxed shadow-sm">
          <p className="whitespace-pre-wrap font-medium">{msg.content}</p>
          {msg.timestamp && (
            <p className="mt-1 text-[10px] uppercase tracking-wide text-zinc-950/60 flex items-center gap-1 justify-end">
              <IconClock className="w-3 h-3" /> {formatTime(msg.timestamp)}
            </p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start">
      <div className="max-w-[80%] rounded-r-xl rounded-l-sm border-l-4 border-amber-500 bg-white dark:bg-zinc-900 border-y border-r border-zinc-200 dark:border-zinc-800 px-4 py-3 text-sm leading-relaxed shadow-sm">
        <div className="flex items-center justify-between mb-1">
          <span className="text-[10px] font-display font-bold uppercase tracking-widest text-amber-600 dark:text-amber-400">
            Agent
          </span>
          {msg.timestamp && (
            <span className="text-[10px] text-zinc-400 flex items-center gap-1">
              <IconClock className="w-3 h-3" /> {formatTime(msg.timestamp)}
            </span>
          )}
        </div>
        <div className="markdown text-zinc-800 dark:text-zinc-100">
          <ReactMarkdown>{msg.content}</ReactMarkdown>
        </div>
        <div className="mt-2 flex items-center gap-3">
          {msg.evidence && msg.evidence.length > 0 && (
            <button
              onClick={() => onShowEvidence(msg.evidence)}
              className="inline-flex items-center gap-1 text-xs font-semibold text-amber-700 dark:text-amber-400 hover:underline"
            >
              <IconLayers className="w-3.5 h-3.5" />
              Evidence ({msg.evidence.length})
            </button>
          )}
          {!msg.isError && <CopyButton text={msg.content} />}
          {msg.sourceQuestion && (
            <button
              onClick={() => onRegenerate(msg.sourceQuestion)}
              title="Regenerate answer"
              className="text-zinc-400 hover:text-amber-600 dark:hover:text-amber-400 transition"
            >
              <IconRefresh className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default function ChatWindow({
  messages,
  loading,
  onSend,
  onShowEvidence,
  onClear,
  vehicleLabel,
  theme,
  onToggleTheme,
}) {
  const [input, setInput] = useState("");
  const scrollRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [input]);

  const submit = (text) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;
    onSend(trimmed);
    setInput("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit(input);
    }
  };

  return (
    <div className="flex flex-col h-full bg-zinc-50 dark:bg-zinc-950">
      <div className="border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 px-6 py-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="font-display text-2xl font-bold text-zinc-900 dark:text-zinc-50 flex items-center gap-2">
              <IconCar className="w-6 h-6 text-amber-500" />
              Automotive Customer Service Agent
            </h1>
            <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
              Currently servicing <span className="font-semibold text-amber-700 dark:text-amber-400">{vehicleLabel}</span>
            </p>
          </div>
          <button
            onClick={onToggleTheme}
            title="Toggle theme"
            className="shrink-0 rounded-lg border border-zinc-300 dark:border-zinc-700 p-2 text-zinc-500 dark:text-zinc-300 hover:text-amber-600 dark:hover:text-amber-400 transition-all duration-150 hover:shadow-md hover:scale-105 active:scale-95"
          >
            {theme === "dark" ? <IconSun className="w-4 h-4" /> : <IconMoon className="w-4 h-4" />}
          </button>
        </div>
      </div>

      <div className="px-6 py-3 bg-white dark:bg-zinc-900 border-b border-zinc-100 dark:border-zinc-800 flex flex-wrap gap-2">
        {SAMPLE_PROMPTS.map(({ Icon, text }) => (
          <button
            key={text}
            onClick={() => submit(text)}
            className="inline-flex items-center gap-1.5 text-xs font-medium bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 text-zinc-700 dark:text-zinc-200 px-3 py-2 rounded-lg transition-all duration-150 hover:shadow-md active:scale-[0.97]"
          >
            <Icon className="w-3.5 h-3.5" /> {text}
          </button>
        ))}
        <button
          onClick={onClear}
          className="inline-flex items-center gap-1.5 text-xs font-medium bg-rose-50 dark:bg-rose-500/10 hover:bg-rose-100 dark:hover:bg-rose-500/20 text-rose-600 dark:text-rose-400 px-3 py-2 rounded-lg transition-all duration-150 hover:shadow-md active:scale-[0.97] ml-auto"
        >
          <IconBroom className="w-3.5 h-3.5" /> Clear
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-zinc-400 dark:text-zinc-500 text-sm mt-10">
            No conversation yet — ask something below, or try a suggestion above.
          </div>
        )}
        {messages.map((msg, idx) => (
          <MessageCard key={idx} msg={msg} onShowEvidence={onShowEvidence} onRegenerate={submit} />
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="border-l-4 border-amber-500 bg-white dark:bg-zinc-900 border-y border-r border-zinc-200 dark:border-zinc-800 rounded-r-xl px-4 py-3 text-sm text-zinc-500 dark:text-zinc-400">
              <span className="inline-flex gap-1 items-center">
                <span className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-bounce [animation-delay:-0.3s]" />
                <span className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-bounce [animation-delay:-0.15s]" />
                <span className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-bounce" />
              </span>
            </div>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      <div className="border-t border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 px-6 py-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            submit(input);
          }}
          className="flex items-end gap-3"
        >
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask an automotive maintenance or operating question… (Enter to send, Shift+Enter for newline)"
            className="flex-1 resize-none rounded-xl border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-950 text-zinc-900 dark:text-zinc-100 px-4 py-3 text-sm transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-amber-500"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="inline-flex items-center gap-2 rounded-xl bg-amber-500 text-zinc-950 font-semibold px-5 py-3 text-sm hover:bg-amber-400 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-150 hover:shadow-md active:scale-[0.97] disabled:active:scale-100"
          >
            <IconSend className="w-4 h-4" />
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
