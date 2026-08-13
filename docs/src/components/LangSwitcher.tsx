"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { locales, localeNames, type Locale } from "@/lib/i18n";

const BASE_PATH = "/xjockiemusic";

export default function LangSwitcher({ current }: { current: string }) {
  const pathname = usePathname();

  function switchPath(locale: string): string {
    // basePath（/xjockiemusic）を除去してからlocale処理し、戻す
    let path = pathname || "/";
    if (path.startsWith(BASE_PATH)) {
      path = path.slice(BASE_PATH.length) || "/";
    }
    const segments = path.split("/").filter(Boolean);
    if (
      segments.length > 0 &&
      (locales as readonly string[]).includes(segments[0])
    ) {
      segments[0] = locale;
    } else {
      segments.unshift(locale);
    }
    if (segments[0] === "ja") segments.shift();
    return BASE_PATH + "/" + segments.join("/");
  }

  return (
    <span className="flex gap-1 text-xs">
      {locales.map((l) => (
        <Link
          key={l}
          href={switchPath(l)}
          className={
            l === current
              ? "font-bold text-jockie"
              : "text-neutral-500 hover:text-jockie"
          }
        >
          {localeNames[l as Locale]}
        </Link>
      ))}
    </span>
  );
}
