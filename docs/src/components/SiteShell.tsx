import Link from "next/link";
import LangSwitcher from "./LangSwitcher";
import type { Dict } from "@/lib/i18n";

export default function SiteShell({
  dict,
  locale,
  children,
}: {
  dict: Dict;
  locale: string;
  children: React.ReactNode;
}) {
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
            <Link href={`${home}control`} className="font-semibold text-jockie hover:opacity-80">
              {dict.navControl}
            </Link>
            <LangSwitcher current={locale} />
          </nav>
        </div>
      </header>
      <main className="flex-1">{children}</main>
      <footer className="border-t border-neutral-800 py-4 text-center text-xs text-neutral-500">
        <div>{dict.footer}</div>
        <div className="mt-1">
          <a
            href={dict.donateUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-jockie hover:underline"
          >
            {dict.donate}
          </a>
        </div>
      </footer>
    </>
  );
}
