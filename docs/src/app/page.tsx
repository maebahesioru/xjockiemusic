// ルート /（日本語版トップ・共通コンポーネントの薄いラッパー）
import SiteShell from "@/components/SiteShell";
import HomeContent from "@/components/HomeContent";
import { getDict } from "@/lib/i18n";

export default function RootHomePage() {
  const dict = getDict("ja");
  return (
    <SiteShell dict={dict} locale="ja">
      <HomeContent locale="ja" />
    </SiteShell>
  );
}
