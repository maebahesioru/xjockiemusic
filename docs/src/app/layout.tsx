import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const BASE = "https://maebahesioru.github.io/xjockiemusic";

export const metadata: Metadata = {
  metadataBase: new URL(BASE),
  title: "X版Jockie Music | スペースで音楽リクエストbot",
  description:
    "X (Twitter) のスペースで動く音楽リクエストbot。スペースツイートのリプにメンションするだけで曲をリクエスト・再生できる、Jockie Musicの非公式Xポート。",
  keywords: [
    "Jockie Music",
    "X Spaces",
    "Twitter Spaces",
    "music bot",
    "音楽リクエスト",
    "スペース",
    "点歌机器人",
  ].join(", "),
  alternates: {
    canonical: `${BASE}/`,
    languages: {
      ja: `${BASE}/`,
      en: `${BASE}/en/`,
      zh: `${BASE}/zh/`,
      "x-default": `${BASE}/`,
    },
  },
  openGraph: {
    title: "X版Jockie Music | スペースで音楽リクエストbot",
    description:
      "X (Twitter) のスペースで動く音楽リクエストbot。スペースツイートのリプにメンションするだけで曲をリクエスト・再生できる、Jockie Musicの非公式Xポート。",
    url: `${BASE}/`,
    siteName: "X版Jockie Music",
    locale: "ja_JP",
    type: "website",
  },
  twitter: {
    card: "summary",
    title: "X版Jockie Music | スペースで音楽リクエストbot",
    description:
      "X (Twitter) のスペースで動く音楽リクエストbot。スペースツイートのリプにメンションするだけで曲をリクエスト・再生できる、Jockie Musicの非公式Xポート。",
  },
  icons: {
    icon: "icon.png",
    apple: "apple-icon.png",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="ja"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-[#17141c] text-neutral-200">
        {children}
      </body>
    </html>
  );
}
