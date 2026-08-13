import type { Metadata } from "next";
import SiteShell from "@/components/SiteShell";
import { getDict, locales } from "@/lib/i18n";

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
        en: `${BASE}/en/`,
        zh: `${BASE}/zh/`,
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

  return (
    <SiteShell dict={dict} locale={locale}>
      {children}
    </SiteShell>
  );
}
