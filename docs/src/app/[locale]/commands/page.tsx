// [locale]版コマンド一覧（共通コンポーネントの薄いラッパー）
import CommandsPage from "@/components/CommandsPage";

export default async function LocaleCommandsPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  return <CommandsPage locale={locale} />;
}
