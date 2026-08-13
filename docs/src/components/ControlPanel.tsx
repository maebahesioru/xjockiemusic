"use client";

// コントロールパネル（サイト制御方式・APIキーでbotを操作）
import { useCallback, useEffect, useState } from "react";

const API_BASE = "https://jockiemusic.hikamer.f5.si/api";
const API_KEY_STORAGE = "jockiemusic_api_key";

type QueueItem = { title: string; user: string };
type Status = {
  ok: boolean;
  current: { title: string; user: string } | null;
  queue: QueueItem[];
  queue_len: number;
  space_id: string | null;
  joined: boolean;
  history_len: number;
};

async function apiCall(path: string, key: string, body?: object) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: body ? "POST" : "GET",
    headers: {
      Authorization: `Bearer ${key}`,
      "Content-Type": "application/json",
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  return res.json();
}

export default function ControlPage() {
  const [apiKey, setApiKey] = useState("");
  const [status, setStatus] = useState<Status | null>(null);
  const [query, setQuery] = useState("");
  const [spaceUrl, setSpaceUrl] = useState("");
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setApiKey(localStorage.getItem(API_KEY_STORAGE) || "");
  }, []);

  const refresh = useCallback(async () => {
    if (!apiKey) return;
    try {
      const s = await apiCall("/status", apiKey);
      if (s.ok) setStatus(s);
    } catch {
      /* 通信エラーは無視 */
    }
  }, [apiKey]);

  useEffect(() => {
    if (!apiKey) return;
    refresh();
    const timer = setInterval(refresh, 10000);
    return () => clearInterval(timer);
  }, [apiKey, refresh]);

  function saveKey() {
    localStorage.setItem(API_KEY_STORAGE, apiKey);
    setMsg("APIキーを保存しました");
    setErr("");
    refresh();
  }

  async function doCall(path: string, body?: object, successMsg?: string) {
    if (!apiKey) {
      setErr("APIキーを入力して保存してください");
      return;
    }
    setLoading(true);
    setErr("");
    setMsg("");
    try {
      const r = await apiCall(path, apiKey, body);
      if (r.ok) {
        setMsg(successMsg || "OK");
        refresh();
      } else {
        setErr(r.error || "エラー");
      }
    } catch (e) {
      setErr(String(e));
    }
    setLoading(false);
  }

  async function doPlay(opts: { insert?: boolean; now?: boolean }) {
    if (!query.trim()) {
      setErr("曲名かURLを入力してください");
      return;
    }
    await doCall("/play", { query: query.trim(), opts, user: "control" }, "追加しました");
    setQuery("");
  }

  async function doJoin() {
    await doCall("/join", { space_url: spaceUrl.trim() }, "スペース参加を開始しました");
  }

  const btn =
    "rounded-lg bg-jockie px-4 py-2 text-sm font-semibold text-white hover:opacity-90 disabled:opacity-50";
  const btnGray =
    "rounded-lg border border-neutral-700 px-4 py-2 text-sm text-neutral-200 hover:bg-white/5 disabled:opacity-50";

  return (
    <div className="mx-auto max-w-4xl px-4 py-10">
      <h1 className="mb-2 text-3xl font-bold text-white">🎛️ コントロールパネル</h1>
      <p className="mb-6 text-sm text-neutral-400">
        botをサイトから操作（リプ方式は廃止）。再生・キュー・スペース接続をここで制御します。
      </p>

      {/* APIキー */}
      <div className="mb-6 rounded-lg border border-neutral-800 bg-[#1d1925] p-4">
        <div className="mb-2 text-sm font-semibold text-white">🔑 APIキー</div>
        <div className="flex gap-2">
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="APIキーを入力"
            className="flex-1 rounded-lg border border-neutral-700 bg-black/30 px-4 py-2 text-sm text-white outline-none placeholder:text-neutral-500 focus:border-jockie"
          />
          <button onClick={saveKey} className={btn}>
            保存
          </button>
        </div>
        {err && <div className="mt-2 text-sm text-red-400">⚠️ {err}</div>}
        {msg && <div className="mt-2 text-sm text-green-400">✅ {msg}</div>}
      </div>

      {/* 再生中 */}
      <div className="mb-6 rounded-lg border border-neutral-800 bg-[#1d1925] p-4">
        <div className="mb-2 text-sm font-semibold text-white">🎵 再生中</div>
        {status?.current ? (
          <div className="text-white">
            {status.current.title}
            <span className="ml-2 text-xs text-neutral-500">
              （リクエスト: {status.current.user}）
            </span>
          </div>
        ) : (
          <div className="text-neutral-500">再生中の曲はありません</div>
        )}
        <div className="mt-2 text-xs text-neutral-500">
          スペース: {status?.joined ? `接続中（${status.space_id || "?"}）` : "未接続"}
          {status ? ` / 履歴: ${status.history_len}曲` : ""}
        </div>
      </div>

      {/* 再生操作 */}
      <div className="mb-6 rounded-lg border border-neutral-800 bg-[#1d1925] p-4">
        <div className="mb-3 text-sm font-semibold text-white">🎮 再生操作</div>
        <div className="mb-3 flex flex-col gap-2 sm:flex-row">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && doPlay({})}
            placeholder="曲名 or URL（例: 星野源 SUN）"
            className="flex-1 rounded-lg border border-neutral-700 bg-black/30 px-4 py-2 text-sm text-white outline-none placeholder:text-neutral-500 focus:border-jockie"
          />
          <button onClick={() => doPlay({})} disabled={loading} className={btn}>
            追加
          </button>
          <button onClick={() => doPlay({ insert: true })} disabled={loading} className={btnGray}>
            次の曲に
          </button>
          <button onClick={() => doPlay({ now: true })} disabled={loading} className={btnGray}>
            すぐ再生
          </button>
        </div>
        <div className="flex flex-wrap gap-2">
          <button onClick={() => doCall("/skip", {}, "スキップ")} disabled={loading} className={btn}>
            ⏭️ スキップ
          </button>
          <button onClick={() => doCall("/pause", {}, "一時停止")} disabled={loading} className={btnGray}>
            ⏸️ 一時停止
          </button>
          <button onClick={() => doCall("/resume", {}, "再開")} disabled={loading} className={btnGray}>
            ▶️ 再開
          </button>
          <button onClick={() => doCall("/shuffle", {}, "シャッフル")} disabled={loading} className={btnGray}>
            🔀 シャッフル
          </button>
          <button onClick={() => doCall("/clear", {}, "全消去")} disabled={loading} className={btnGray}>
            🧹 全消去
          </button>
          <button
            onClick={() => doCall("/volume", { value: 100 }, "音量100")}
            disabled={loading}
            className={btnGray}
          >
            🔊 音量100
          </button>
          <button
            onClick={() => doCall("/volume", { value: 150 }, "音量150")}
            disabled={loading}
            className={btnGray}
          >
            🔊 音量150
          </button>
        </div>
      </div>

      {/* スペース */}
      <div className="mb-6 rounded-lg border border-neutral-800 bg-[#1d1925] p-4">
        <div className="mb-3 text-sm font-semibold text-white">🎙️ スペース</div>
        <div className="mb-3 flex gap-2">
          <input
            type="text"
            value={spaceUrl}
            onChange={(e) => setSpaceUrl(e.target.value)}
            placeholder="スペースURL（https://x.com/i/spaces/...）"
            className="flex-1 rounded-lg border border-neutral-700 bg-black/30 px-4 py-2 text-sm text-white outline-none placeholder:text-neutral-500 focus:border-jockie"
          />
          <button onClick={doJoin} disabled={loading} className={btn}>
            参加
          </button>
        </div>
        <button onClick={() => doCall("/leave", {}, "離脱")} disabled={loading} className={btnGray}>
          👋 離脱
        </button>
      </div>

      {/* キュー */}
      <div className="rounded-lg border border-neutral-800 bg-[#1d1925] p-4">
        <div className="mb-3 text-sm font-semibold text-white">
          📋 キュー（{status?.queue_len ?? 0}曲）
        </div>
        {status?.queue && status.queue.length > 0 ? (
          <div className="space-y-1">
            {status.queue.map((it, i) => (
              <div
                key={i}
                className="flex items-center justify-between gap-2 border-b border-neutral-800 py-1.5 text-sm last:border-b-0"
              >
                <div className="min-w-0">
                  <span className="mr-2 text-neutral-500">{i + 1}.</span>
                  <span className="text-white">{it.title}</span>
                  <span className="ml-2 text-xs text-neutral-500">（{it.user}）</span>
                </div>
                <button
                  onClick={() => doCall("/remove", { index: i + 1 }, "削除")}
                  disabled={loading}
                  className="shrink-0 rounded bg-red-900/40 px-2 py-1 text-xs text-red-300 hover:bg-red-900/60"
                >
                  削除
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-neutral-500">キューは空です</div>
        )}
      </div>
    </div>
  );
}
