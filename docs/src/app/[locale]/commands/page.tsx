"use client";

import { useEffect, useMemo, useState } from "react";
import { commandsData, type Command } from "@/lib/commands";
import { getDict } from "@/lib/i18n";

function CommandRow({
  cmd,
  dict,
  loc,
}: {
  cmd: Command;
  dict: ReturnType<typeof getDict>;
  loc: string;
}) {
  const [open, setOpen] = useState(false);
  const name = cmd.command || "";
  return (
    <div className="border-b border-neutral-800 last:border-b-0">
      <button
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between gap-2 px-4 py-3 text-left hover:bg-white/5"
      >
        <code className="font-mono text-sm font-semibold text-jockie">
          !{name}
        </code>
        <span className="text-xs text-neutral-500">{open ? "▲" : "▼"}</span>
      </button>
      {open && (
        <div className="space-y-2 bg-black/20 px-4 pb-4">
          {loc === "ja" ? (
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
        </div>
      )}
    </div>
  );
}

// X版対応（x: true）コマンドだけを抽出
function xCommands(): { name: string; commands: Command[] }[] {
  const result: { name: string; commands: Command[] }[] = [];
  for (const cat of commandsData.categories) {
    const cmds = cat.commands.filter((c) => c.x);
    if (cmds.length > 0) result.push({ name: cat.name, commands: cmds });
  }
  const unknown = commandsData.unknown.filter((c) => c.x);
  if (unknown.length > 0) result.push({ name: "unknown", commands: unknown });
  return result;
}

export default function CommandsPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const [loc, setLoc] = useState("ja");
  const [query, setQuery] = useState("");
  const [catFilter, setCatFilter] = useState<string>("all");

  // クライアントではURLからlocaleを読む
  useEffect(() => {
    const m = window.location.pathname.match(/^\/(en|zh)\b/);
    setLoc(m ? m[1] : "ja");
  }, []);

  const dict = getDict(loc);

  const cats = useMemo(() => xCommands(), []);
  const total = useMemo(
    () => cats.reduce((a, c) => a + c.commands.length, 0),
    [cats]
  );

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    const result: { name: string; commands: Command[] }[] = [];
    for (const cat of cats) {
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
    return result;
  }, [query, catFilter, cats]);

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
          {cats.map((c) => (
            <option key={c.name} value={c.name}>
              {c.name}
            </option>
          ))}
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
                  loc={loc}
                />
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
