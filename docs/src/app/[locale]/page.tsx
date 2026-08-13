// [locale]版トップページ（共通コンポーネントの薄いラッパー）
import HomeContent from "@/components/HomeContent";

export default async function LocaleHomePage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  return <HomeContent locale={locale} />;
}
