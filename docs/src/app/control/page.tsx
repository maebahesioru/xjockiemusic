// コントロールパネルページ（サイト制御方式）
import SiteShell from "@/components/SiteShell";
import ControlPanel from "@/components/ControlPanel";
import { getDict } from "@/lib/i18n";

export default function ControlPage() {
  const dict = getDict("ja");
  return (
    <SiteShell dict={dict} locale="ja">
      <ControlPanel />
    </SiteShell>
  );
}
