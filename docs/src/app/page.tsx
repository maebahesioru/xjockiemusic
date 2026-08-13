import Link from "next/link";
import SiteShell from "@/components/SiteShell";
import { getDict } from "@/lib/i18n";
import { commandsData, categoryCounts } from "@/lib/commands";

const BASE = "https://maebahesioru.github.io/xjockiemusic";

export default function RootHomePage() {
  // ルート / は日本語版（canonicalも / に統一）
  const locale = "ja";
  const dict = getDict(locale);
  const counts = categoryCounts();
  const total = Object.values(counts).reduce((a, b) => a + b, 0);

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: dict.siteName,
    url: `${BASE}/`,
    description: dict.description,
    inLanguage: "ja",
  };

  return (
    <SiteShell dict={dict} locale={locale}>
    <div className="mx-auto max-w-4xl px-4 py-10">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <section className="mb-10 text-center">
        <h1 className="mb-3 text-4xl font-bold text-white">
          🎵 <span className="text-jockie">{dict.heroTitle}</span>
        </h1>
        <p className="mb-2 text-lg text-neutral-300">{dict.heroDesc1}</p>
        <p className="mb-6 text-sm text-neutral-400">{dict.heroDesc2}</p>
        <div className="flex justify-center gap-3">
          <Link
            href="/commands"
            className="rounded-lg bg-jockie px-5 py-2.5 font-semibold text-white hover:bg-jockie-dark"
          >
            {dict.commandsButton.replace("{n}", String(total))}
          </Link>
        </div>
      </section>

      <section className="mb-8">
        <h2 className="mb-3 text-xl font-bold text-white">{dict.howto}</h2>
        <div className="space-y-3">
          {dict.howtoSteps.map((s, i) => (
            <div
              key={i}
              className="flex gap-4 rounded-lg border border-neutral-800 bg-[#1d1925] p-4"
            >
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-jockie font-bold text-white">
                {i + 1}
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
        <h2 className="mb-3 text-xl font-bold text-white">{dict.examples}</h2>
        <div className="overflow-hidden rounded-lg border border-neutral-800">
          {[
            ["@JockieMusicPort play 星野源 SUN", "search & queue"],
            ["@JockieMusicPort play https://youtu.be/xxx", "queue by URL"],
            ["@JockieMusicPort insert 曲名", "insert next"],
            ["@JockieMusicPort skip", "skip"],
            ["@JockieMusicPort volume 150", "volume"],
            ["@JockieMusicPort queue", "show queue"],
            ["@JockieMusicPort shuffle", "shuffle"],
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
        <h2 className="mb-3 text-xl font-bold text-white">{dict.categories}</h2>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {Object.entries(counts).map(([name, n]) => (
            <Link
              key={name}
              href="/commands"
              className="rounded-lg border border-neutral-800 bg-[#1d1925] p-4 hover:border-jockie"
            >
              <div className="font-semibold text-white">{name}</div>
              <div className="text-sm text-neutral-500">
                {n}
                {dict.commandsUnit}
              </div>
            </Link>
          ))}
        </div>
      </section>
    </div>
    </SiteShell>
  );
}
