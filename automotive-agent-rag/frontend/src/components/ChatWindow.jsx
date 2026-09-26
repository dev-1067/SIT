import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";

const SAMPLE_PROMPTS = [
  { icon: "🔔", label: "When will the alarm be triggered?", text: "When will the alarm be triggered?" },
  {
    icon: "❄️",
    label: "When is air recirculation turned off?",
    text: "When is the air recirculation mode turned off?",
  },
  {
    icon: "🔥",
    label: "When should seat heating not be used?",
    text: "When should the seat heating not be turned on?",
  },
];

function MessageBubble({ msg, onShowEvidence }) {
  const isUser = msg.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm ${
          isUser
            ? "bg-indigo-600 text-white rounded-br-sm"
            : "bg-white border border-slate-200 text-slate-800 rounded-bl-sm"
        }`}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{msg.content}</p>
        ) : (
          <div className="markdown">
            <ReactMarkdown>{msg.content}</ReactMarkdown>
          </div>
        )}
        {!isUser && msg.evidence && msg.evidence.length > 0 && (
          <button
            onClick={() => onShowEvidence(msg.evidence)}
            className="mt-2 inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-800 bg-indigo-50 hover:bg-indigo-100 px-2.5 py-1 rounded-full transition"
          >
            🔎 View Evidence ({msg.evidence.length})
          </button>
        )}
      </div>
    </div>
  );
}

export default function ChatWindow({ messages, loading, onSend, onShowEvidence, onClear, provider }) {
  const [input, setInput] = useState("");
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const submit = (text) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;
    onSend(trimmed);
    setInput("");
  };

  return (
    <div className="flex flex-col h-full">
      <div className="border-b border-slate-200 bg-white px-6 py-5">
        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          🚗 Automotive Customer Service Agent (RAG)
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Powered by <span className="font-semibold text-indigo-600">{provider}</span> + FAISS vector search over
          automotive manuals, with MongoDB-backed manual storage.
        </p>
      </div>

      <div className="px-6 py-3 bg-white border-b border-slate-100 flex flex-wrap gap-2">
        {SAMPLE_PROMPTS.map((p) => (
          <button
            key={p.text}
            onClick={() => submit(p.text)}
            className="text-xs font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-2 rounded-lg transition"
          >
            {p.icon} {p.label}
          </button>
        ))}
        <button
          onClick={onClear}
          className="text-xs font-medium bg-rose-50 hover:bg-rose-100 text-rose-600 px-3 py-2 rounded-lg transition ml-auto"
        >
          🧹 Clear Chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4 bg-slate-50">
        {messages.length === 0 && (
          <div className="text-center text-slate-400 text-sm mt-10">
            Ask a maintenance or operating question about the target vehicle to get started.
          </div>
        )}
        {messages.map((msg, idx) => (
          <MessageBubble key={idx} msg={msg} onShowEvidence={onShowEvidence} />
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-slate-200 rounded-2xl rounded-bl-sm px-4 py-3 text-sm text-slate-500 shadow-sm">
              <span className="inline-flex gap-1 items-center">
                <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
                <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
                <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" />
              </span>
            </div>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      <div className="border-t border-slate-200 bg-white px-6 py-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            submit(input);
          }}
          className="flex items-center gap-3"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask an automotive maintenance or operating question…"
            className="flex-1 rounded-xl border border-slate-300 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="rounded-xl bg-indigo-600 text-white font-semibold px-5 py-3 text-sm hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
