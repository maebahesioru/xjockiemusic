import Link from "next/link";
import { commandsData, categoryCounts } from "@/lib/commands";

export default function Home() {
  const counts = categoryCounts();
  const total = Object.values(counts).reduce((a, b) => a + b, 0);

  return (
    <div className="mx-auto max-w-4xl px-4 py-10">
      <section className="mb-10 text-center">
        <h1 className="mb-3 text-4xl font-bold text-white">
          🎵 X版<span className="text-jockie">Jockie Music</span>
        </h1>
        <p className="mb-2 text-lg text-neutral-300">
          X (Twitter) のスペースで動く音楽リクエストbot
        </p>
        <p className="mb-6 text-sm text-neutral-400">
          Jockie Music（Discord）の非公式Xポート。
          <br />
          <span className="text-jockie">スペースツイートのリプにメンションするだけ</span>
          で曲をリクエスト・再生できます。
        </p>
        <div className="flex justify-center gap-3">
          <Link
            href="/commands"
            className="rounded-lg bg-jockie px-5 py-2.5 font-semibold text-white hover:bg-jockie-dark"
          >
            コマンド一覧（{total}個）
          </Link>
        </div>
      </section>

      <section className="mb-8">
        <h2 className="mb-3 text-xl font-bold text-white">🚀 使い方</h2>
        <div className="space-y-3">
          {[
            {
              step: "1",
              title: "スペースを立てる",
              desc: "Xでスペースを開始（Xが自動でスペースURLのツイートを投稿します）",
            },
            {
              step: "2",
              title: "スペースツイートのリプにメンション",
              desc: "@JockieMusicPort にメンションしてコマンドを送るだけでOK",
            },
            {
              step: "3",
              title: "スピーカーリクエストを承認",
              desc: "botが自動で参加 → スピーカーリクエスト送信 → ホストが承認",
            },
            {
              step: "4",
              title: "曲が流れる！",
              desc: "キューに追加された曲を順番にスペースで再生",
            },
          ].map((s) => (
            <div
              key={s.step}
              className="flex gap-4 rounded-lg border border-neutral-800 bg-[#1d1925] p-4"
            >
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-jockie font-bold text-white">
                {s.step}
              </div>
              <div>
                <div className="font-semibold text-white">{s.title}</div>
                <div className="text-sm text-neutral-400">{s.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="mb-8">
        <h2 className="mb-3 text-xl font-bold text-white">💬 コマンド例</h2>
        <div className="overflow-hidden rounded-lg border border-neutral-800">
          {[
            ["@JockieMusicPort play 星野源 SUN", "曲名で検索してキューに追加"],
            ["@JockieMusicPort play https://youtu.be/xxx", "URLでキューに追加"],
            ["@JockieMusicPort insert 曲名", "再生中の次に挿入"],
            ["@JockieMusicPort skip", "今の曲をスキップ"],
            ["@JockieMusicPort volume 150", "音量を150に設定"],
            ["@JockieMusicPort queue", "キューを表示"],
            ["@JockieMusicPort shuffle", "キューをシャッフル"],
          ].map(([cmd, desc]) => (
            <div
              key={cmd}
              className="flex flex-col gap-1 border-b border-neutral-800 bg-[#1d1925] px-4 py-3 last:border-b-0 sm:flex-row sm:items-center sm:justify-between"
            >
              <code className="font-mono text-sm text-jockie">{cmd}</code>
              <span className="text-sm text-neutral-400">{desc}</span>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-xl font-bold text-white">📋 カテゴリ一覧</h2>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {Object.entries(counts).map(([name, n]) => (
            <Link
              key={name}
              href="/commands"
              className="rounded-lg border border-neutral-800 bg-[#1d1925] p-4 hover:border-jockie"
            >
              <div className="font-semibold text-white">{name}</div>
              <div className="text-sm text-neutral-500">{n}コマンド</div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
