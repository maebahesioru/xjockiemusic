import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "X版Jockie Music | スペースで音楽リクエストbot",
  description:
    "X (Twitter) のスペースで動く音楽リクエストbot。スペースツイートのリプにメンションするだけで曲をリクエスト・再生できる、Jockie Musicの非公式Xポート。",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="ja"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-[#17141c] text-neutral-200">
        <header className="border-b border-neutral-800 bg-[#1d1925]">
          <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
            <Link href="/" className="text-lg font-bold text-white">
              🎵 <span className="text-jockie">X版Jockie Music</span>
            </Link>
            <nav className="flex gap-4 text-sm">
              <Link href="/" className="hover:text-jockie">
                使い方
              </Link>
              <Link href="/commands" className="hover:text-jockie">
                コマンド一覧
              </Link>
            </nav>
          </div>
        </header>
        <main className="flex-1">{children}</main>
        <footer className="border-t border-neutral-800 py-4 text-center text-xs text-neutral-500">
          X版Jockie Music - Jockie Musicの非公式Xポート（本家とは無関係です）
        </footer>
      </body>
    </html>
  );
}
