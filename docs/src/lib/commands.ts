// コマンドデータの型定義
export interface CommandOption {
  name: string;
  description: string;
}

export interface Command {
  command: string;
  aliases: string[];
  usage: string;
  description: string;
  options: CommandOption[];
  examples: string[];
  ja?: string;
  x?: boolean;
  x_alias?: string;
}

export interface CommandCategory {
  name: string;
  description: string;
  commands: Command[];
  subCategories: unknown[];
}

export interface CommandsData {
  categories: CommandCategory[];
  unknown: Command[];
}

import data from "@/data/commands.json";

export const commandsData = data as unknown as CommandsData;

// カテゴリごとのコマンド数
export function categoryCounts(): Record<string, number> {
  const counts: Record<string, number> = {};
  for (const cat of commandsData.categories) {
    counts[cat.name] = cat.commands.length;
  }
  counts["unknown"] = commandsData.unknown.length;
  return counts;
}

// X版対応（x: true）コマンドのカテゴリごとの数
export function xCategoryCounts(): Record<string, number> {
  const counts: Record<string, number> = {};
  for (const cat of commandsData.categories) {
    const n = cat.commands.filter((c) => c.x).length;
    if (n > 0) counts[cat.name] = n;
  }
  const unk = commandsData.unknown.filter((c) => c.x).length;
  if (unk > 0) counts["unknown"] = unk;
  return counts;
}
