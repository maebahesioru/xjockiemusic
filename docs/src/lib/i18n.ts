// i18n 翻訳データ（ja / en / zh）
export const locales = ["ja", "en", "zh"] as const;
export type Locale = (typeof locales)[number];

export const defaultLocale: Locale = "ja";

export const localeNames: Record<Locale, string> = {
  ja: "日本語",
  en: "English",
  zh: "中文",
};

export const i18n = {
  ja: {
    siteName: "X版Jockie Music",
    tagline: "X (Twitter) のスペースで動く音楽リクエストbot",
    description:
      "X (Twitter) のスペースで動く音楽リクエストbot。スペースツイートのリプにメンションするだけで曲をリクエスト・再生できる、Jockie Musicの非公式Xポート。",
    navHome: "使い方",
    navCommands: "コマンド一覧",
    heroTitle: "X版Jockie Music",
    heroDesc1: "X (Twitter) のスペースで動く音楽リクエストbot",
    heroDesc2:
      "Jockie Music（Discord）の非公式Xポート。スペースツイートのリプにメンションするだけで曲をリクエスト・再生できます。",
    commandsButton: "コマンド一覧（{n}個）",
    howto: "🚀 使い方",
    howtoSteps: [
      { title: "スペースを立てる", desc: "Xでスペースを開始（Xが自動でスペースURLのツイートを投稿します）" },
      { title: "スペースツイートのリプにメンション", desc: "@JockieMusicPort にメンションしてコマンドを送るだけでOK" },
      { title: "スピーカーリクエストを承認", desc: "botが自動で参加 → スピーカーリクエスト送信 → ホストが承認" },
      { title: "曲が流れる！", desc: "キューに追加された曲を順番にスペースで再生" },
    ],
    examples: "💬 コマンド例",
    categories: "📋 カテゴリ一覧",
    commandsTitle: "📋 コマンド一覧（{n}個）",
    commandsDesc:
      "Jockie Music公式コマンドの全一覧です。スペースツイートのリプに @JockieMusicPort コマンド で送ってね。",
    searchPlaceholder: "🔍 コマンド名・説明で検索…",
    allCategories: "すべてのカテゴリ",
    noCommands: "該当するコマンドがありません",
    commandsUnit: "コマンド",
    usage: "使い方",
    options: "オプション",
    examplesLabel: "例",
    alias: "alias",
    xSupported: "✅ X版対応",
    xNotSupported: "X版非対応",
    donate: "💝 寄付",
    donateUrl: "https://ofuse.me/maebahesioru",
    footer: "X版Jockie Music - Jockie Musicの非公式Xポート（本家とは無関係です）",
  },
  en: {
    siteName: "Jockie Music for X",
    tagline: "Music request bot that runs in X (Twitter) Spaces",
    description:
      "A music request bot that runs in X (Twitter) Spaces. Just mention the bot in a reply to your Space tweet to request and play music — an unofficial X port of Jockie Music.",
    navHome: "Usage",
    navCommands: "Commands",
    heroTitle: "Jockie Music for X",
    heroDesc1: "Music request bot that runs in X (Twitter) Spaces",
    heroDesc2:
      "Unofficial X port of Jockie Music (Discord). Just mention the bot in a reply to your Space tweet to request and play music.",
    commandsButton: "All Commands ({n})",
    howto: "🚀 How to use",
    howtoSteps: [
      { title: "Start a Space", desc: "Start a Space on X (X automatically posts the Space URL tweet)" },
      { title: "Mention the bot in a reply", desc: "Reply to the Space tweet mentioning @JockieMusicPort with a command" },
      { title: "Approve the speaker request", desc: "The bot joins automatically → sends a speaker request → the host approves" },
      { title: "Music plays!", desc: "Queued tracks are played in the Space in order" },
    ],
    examples: "💬 Command examples",
    categories: "📋 Categories",
    commandsTitle: "📋 All Commands ({n})",
    commandsDesc:
      "All official Jockie Music commands. Send them as a reply to your Space tweet with @JockieMusicPort command.",
    searchPlaceholder: "🔍 Search commands…",
    allCategories: "All categories",
    noCommands: "No matching commands",
    commandsUnit: "commands",
    usage: "Usage",
    options: "Options",
    examplesLabel: "Examples",
    alias: "alias",
    xSupported: "✅ X-ready",
    xNotSupported: "not X-ready",
    donate: "💝 Donate",
    donateUrl: "https://ofuse.me/maebahesioru",
    footer: "Jockie Music for X - unofficial X port of Jockie Music (not affiliated)",
  },
  zh: {
    siteName: "X版Jockie Music",
    tagline: "在 X（Twitter）Space 中运行的音乐点歌机器人",
    description:
      "在 X（Twitter）Space 中运行的音乐点歌机器人。只需在 Space 推文的回复中提及机器人，即可点歌和播放——Jockie Music 的非官方 X 移植版。",
    navHome: "使用方法",
    navCommands: "命令列表",
    heroTitle: "X版Jockie Music",
    heroDesc1: "在 X（Twitter）Space 中运行的音乐点歌机器人",
    heroDesc2:
      "Jockie Music（Discord）的非官方 X 移植版。只需在 Space 推文的回复中提及机器人，即可点歌和播放。",
    commandsButton: "全部命令（{n}个）",
    howto: "🚀 使用方法",
    howtoSteps: [
      { title: "开启 Space", desc: "在 X 上开启 Space（X 会自动发布 Space 链接推文）" },
      { title: "在回复中提及机器人", desc: "在 Space 推文的回复中 @JockieMusicPort 并发送命令即可" },
      { title: "批准发言请求", desc: "机器人自动加入 → 发送发言请求 → 主持人批准" },
      { title: "开始播放！", desc: "队列中的歌曲将按顺序在 Space 中播放" },
    ],
    examples: "💬 命令示例",
    categories: "📋 分类列表",
    commandsTitle: "📋 全部命令（{n}个）",
    commandsDesc:
      "Jockie Music 官方命令完整列表。在 Space 推文的回复中发送 @JockieMusicPort 命令 即可。",
    searchPlaceholder: "🔍 搜索命令…",
    allCategories: "所有分类",
    noCommands: "没有匹配的命令",
    commandsUnit: "个命令",
    usage: "用法",
    options: "选项",
    examplesLabel: "示例",
    alias: "别名",
    xSupported: "✅ X版可用",
    xNotSupported: "X版不可用",
    donate: "💝 捐赠",
    donateUrl: "https://ofuse.me/maebahesioru",
    footer: "X版Jockie Music - Jockie Music 的非官方 X 移植版（与本家无关）",
  },
} as const;

export type Dict = (typeof i18n)[Locale];

export function getDict(locale: string): Dict {
  if (locale in i18n) return i18n[locale as Locale];
  return i18n[defaultLocale];
}
