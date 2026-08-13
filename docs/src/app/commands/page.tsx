// ルート /commands/（日本語版コマンド一覧・共通コンポーネントの薄いラッパー）
import SiteShell from "@/components/SiteShell";
import CommandsPage from "@/components/CommandsPage";
import { getDict } from "@/lib/i18n";

export default function RootCommandsPage() {
  const dict = getDict("ja");
  return (
    <SiteShell dict={dict} locale="ja">
      <CommandsPage locale="ja" />
    </SiteShell>
  );
}
