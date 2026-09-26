import { useState } from "react";
import { api, setAuthToken } from "../api/client";
import { IconCar, IconAlert } from "./Icons";

export default function LoginPage({ onAuthenticated }) {
  const [mode, setMode] = useState("login"); // "login" | "register"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const isLogin = mode === "login";

  const submit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const data = isLogin ? await api.login(email, password) : await api.register(email, password);
      setAuthToken(data.token);
      onAuthenticated(data.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen flex items-center justify-center bg-zinc-100 dark:bg-zinc-950 px-4 transition-colors duration-300">
      <div className="w-full max-w-sm">
        <div className="flex flex-col items-center mb-8 animate-[fadein_0.4s_ease-out]">
          <div className="w-12 h-12 rounded-2xl bg-zinc-950 dark:bg-amber-500 flex items-center justify-center mb-3 shadow-lg transition-transform duration-300 hover:scale-105">
            <IconCar className="w-6 h-6 text-amber-500 dark:text-zinc-950" />
          </div>
          <h1 className="font-display text-xl font-bold text-zinc-900 dark:text-zinc-50">
            Automotive Customer Service Agent
          </h1>
          <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">Sign in to continue</p>
        </div>

        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl shadow-xl p-6 animate-[fadein_0.4s_ease-out]">
          <div className="flex mb-6 rounded-xl bg-zinc-100 dark:bg-zinc-800 p-1 relative">
            <div
              className={`absolute top-1 bottom-1 w-[calc(50%-4px)] rounded-lg bg-white dark:bg-zinc-950 shadow transition-transform duration-300 ease-out ${
                isLogin ? "translate-x-0" : "translate-x-[calc(100%+8px)]"
              }`}
            />
            <button
              type="button"
              onClick={() => {
                setMode("login");
                setError(null);
              }}
              className={`relative z-10 flex-1 text-sm font-semibold py-2 rounded-lg transition-colors duration-200 ${
                isLogin ? "text-zinc-900 dark:text-zinc-50" : "text-zinc-500 dark:text-zinc-400"
              }`}
            >
              Sign in
            </button>
            <button
              type="button"
              onClick={() => {
                setMode("register");
                setError(null);
              }}
              className={`relative z-10 flex-1 text-sm font-semibold py-2 rounded-lg transition-colors duration-200 ${
                !isLogin ? "text-zinc-900 dark:text-zinc-50" : "text-zinc-500 dark:text-zinc-400"
              }`}
            >
              Create account
            </button>
          </div>

          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-zinc-500 dark:text-zinc-400 mb-1">Email</label>
              <input
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-950 text-zinc-900 dark:text-zinc-100 px-3 py-2.5 text-sm transition focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                placeholder="you@example.com"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-zinc-500 dark:text-zinc-400 mb-1">Password</label>
              <input
                type="password"
                required
                minLength={6}
                autoComplete={isLogin ? "current-password" : "new-password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-950 text-zinc-900 dark:text-zinc-100 px-3 py-2.5 text-sm transition focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                placeholder={isLogin ? "••••••••" : "At least 6 characters"}
              />
            </div>

            {error && (
              <div className="flex items-start gap-2 text-sm text-rose-700 dark:text-rose-300 bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-900 rounded-lg px-3 py-2 animate-[fadein_0.2s_ease-out]">
                <IconAlert className="w-4 h-4 shrink-0 mt-0.5" />
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-amber-500 text-zinc-950 font-semibold py-2.5 text-sm transition-all duration-150 hover:bg-amber-400 hover:shadow-md active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100"
            >
              {loading ? "Please wait…" : isLogin ? "Sign in" : "Create account"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
