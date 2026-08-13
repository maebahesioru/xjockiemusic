import type { Metadata } from "next";
import Link from "next/link";
import LangSwitcher from "@/components/LangSwitcher";
import { getDict, locales, localeNames } from "@/lib/i18n";

const BASE = "https://maebahesioru.github.io/xjockiemusic";

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  const dict = getDict(locale);
  const path = locale === "ja" ? "" : `/${locale}`;
  const langAttr = locale === "ja" ? "ja" : locale === "zh" ? "zh" : "en";
  return {
    title: `${dict.siteName} | ${dict.tagline}`,
    description: dict.description,
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
      canonical: `${BASE}${path}`,
      languages: {
        ja: `${BASE}/`,
        en: `${BASE}/en`,
        zh: `${BASE}/zh`,
        "x-default": `${BASE}/`,
      },
    },
    openGraph: {
      title: `${dict.siteName} | ${dict.tagline}`,
      description: dict.description,
      url: `${BASE}${path}`,
      siteName: dict.siteName,
      locale: langAttr === "ja" ? "ja_JP" : langAttr === "zh" ? "zh_CN" : "en_US",
      type: "website",
    },
    twitter: {
      card: "summary",
      title: `${dict.siteName} | ${dict.tagline}`,
      description: dict.description,
    },
  };
}

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const dict = getDict(locale);
  const home = locale === "ja" ? "/" : `/${locale}`;

  return (
    <>
      <header className="border-b border-neutral-800 bg-[#1d1925]">
        <div className="mx-auto flex max-w-4xl items-center justify-between gap-2 px-4 py-3">
          <Link href={home} className="text-lg font-bold text-white">
            🎵 <span className="text-jockie">{dict.siteName}</span>
          </Link>
          <nav className="flex items-center gap-3 text-sm">
            <Link href={home} className="hover:text-jockie">
              {dict.navHome}
            </Link>
            <Link href={`${home}commands`} className="hover:text-jockie">
              {dict.navCommands}
            </Link>
            <LangSwitcher current={locale} />
          </nav>
        </div>
      </header>
      <main className="flex-1">{children}</main>
      <footer className="border-t border-neutral-800 py-4 text-center text-xs text-neutral-500">
        {dict.footer}
      </footer>
    </>
  );
}
