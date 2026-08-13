"use client";

// コマンド一覧ページ共通コンポーネント（[locale]版・ルート版の両方から使用）
// localeはpropsで受け取る（URLパース不要）
import { useMemo, useState } from "react";
import { commandsData, type Command } from "@/lib/commands";
import { getDict } from "@/lib/i18n";

function CommandRow({
  cmd,
  dict,
  locale,
}: {
  cmd: Command;
  dict: ReturnType<typeof getDict>;
  locale: string;
}) {
  const [open, setOpen] = useState(false);
  const name = cmd.command || "";
  const usage = cmd.usage || name;
  return (
    <div className="border-b border-neutral-800 last:border-b-0">
      <button
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between gap-2 px-4 py-3 text-left hover:bg-white/5"
      >
        <div className="flex flex-wrap items-center gap-2">
          <code className="font-mono text-sm font-semibold text-jockie">
            !{name}
          </code>
          {cmd.aliases?.length > 0 && (
            <span className="text-xs text-neutral-500">
              {dict.alias}: {cmd.aliases.join(", ")}
            </span>
          )}
        </div>
        <span className="text-xs text-neutral-500">{open ? "▲" : "▼"}</span>
      </button>
      {open && (
        <div className="space-y-2 bg-black/20 px-4 pb-4">
          {/* 言語ごとに説明は1つだけ（jaは日本語・それ以外は英語） */}
          {locale === "ja" ? (
            cmd.ja ? (
              <p className="text-sm text-white">{cmd.ja}</p>
            ) : (
              cmd.description && (
                <p className="text-sm text-neutral-400">{cmd.description}</p>
              )
            )
          ) : (
            cmd.description && (
              <p className="text-sm text-neutral-400">{cmd.description}</p>
            )
          )}
          {usage && (
            <p className="text-sm">
              <span className="text-neutral-500">{dict.usage}: </span>
              <code className="font-mono text-neutral-300">!{usage}</code>
            </p>
          )}
          {cmd.options && cmd.options.length > 0 && (
            <div>
              <div className="mb-1 text-xs text-neutral-500">{dict.options}:</div>
              {cmd.options.map((o) => (
                <div key={o.name} className="text-sm text-neutral-400">
                  <code className="font-mono text-jockie">{o.name}</code>{" "}
                  {locale === "ja" && o.ja ? o.ja : o.description}
                </div>
              ))}
            </div>
          )}
          {cmd.examples && cmd.examples.length > 0 && (
            <div>
              <div className="mb-1 text-xs text-neutral-500">
                {dict.examplesLabel}:
              </div>
              {cmd.examples.map((e, i) => (
                <code
                  key={i}
                  className="block font-mono text-xs text-neutral-400"
                >
                  !{e}
                </code>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function CommandsPage({ locale }: { locale: string }) {
  const [query, setQuery] = useState("");
  const [catFilter, setCatFilter] = useState<string>("all");

  const dict = getDict(locale);

  const total = useMemo(() => {
    let n = 0;
    for (const cat of commandsData.categories) n += cat.commands.length;
    return n + commandsData.unknown.length;
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    const result: { name: string; commands: Command[] }[] = [];
    for (const cat of commandsData.categories) {
      if (catFilter !== "all" && cat.name !== catFilter) continue;
      let cmds = cat.commands;
      if (q) {
        cmds = cmds.filter(
          (c) =>
            (c.command || "").toLowerCase().includes(q) ||
            (c.ja || c.description || "").toLowerCase().includes(q)
        );
      }
      if (cmds.length > 0) result.push({ name: cat.name, commands: cmds });
    }
    if (catFilter === "all" || catFilter === "unknown") {
      let cmds = commandsData.unknown;
      if (q) {
        cmds = cmds.filter(
          (c) =>
            (c.command || "").toLowerCase().includes(q) ||
            (c.ja || c.description || "").toLowerCase().includes(q)
        );
      }
      if (cmds.length > 0) result.push({ name: "unknown", commands: cmds });
    }
    return result;
  }, [query, catFilter]);

  return (
    <div className="mx-auto max-w-4xl px-4 py-10">
      <h1 className="mb-2 text-3xl font-bold text-white">
        {dict.commandsTitle.replace("{n}", String(total))}
      </h1>
      <p className="mb-6 text-sm text-neutral-400">{dict.commandsDesc}</p>

      <div className="mb-6 flex flex-col gap-3 sm:flex-row">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={dict.searchPlaceholder}
          className="flex-1 rounded-lg border border-neutral-700 bg-[#1d1925] px-4 py-2.5 text-sm text-white outline-none placeholder:text-neutral-500 focus:border-jockie"
        />
        <select
          value={catFilter}
          onChange={(e) => setCatFilter(e.target.value)}
          className="rounded-lg border border-neutral-700 bg-[#1d1925] px-3 py-2.5 text-sm text-white outline-none focus:border-jockie"
        >
          <option value="all">{dict.allCategories}</option>
          {commandsData.categories.map((c) => (
            <option key={c.name} value={c.name}>
              {c.name}
            </option>
          ))}
          <option value="unknown">unknown</option>
        </select>
      </div>

      <div className="space-y-6">
        {filtered.length === 0 && (
          <p className="text-center text-neutral-500">{dict.noCommands}</p>
        )}
        {filtered.map((cat) => (
          <section key={cat.name}>
            <h2 className="mb-2 flex items-center gap-2 text-lg font-bold text-white">
              <span className="rounded bg-jockie px-2 py-0.5 text-xs font-semibold text-white">
                {cat.name}
              </span>
              <span className="text-sm font-normal text-neutral-500">
                {cat.commands.length}
                {dict.commandsUnit}
              </span>
            </h2>
            <div className="overflow-hidden rounded-lg border border-neutral-800 bg-[#1d1925]">
              {cat.commands.map((cmd, i) => (
                <CommandRow
                  key={cmd.command || `${cat.name}-${i}`}
                  cmd={cmd}
                  dict={dict}
                  locale={locale}
                />
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
