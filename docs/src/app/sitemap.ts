import type { MetadataRoute } from "next";

export const dynamic = "force-static";

const BASE = "https://maebahesioru.github.io/xjockiemusic";

export default function sitemap(): MetadataRoute.Sitemap {
  const pages = ["/", "/commands/"];
  const locales = ["", "/en", "/zh"];
  const entries: MetadataRoute.Sitemap = [];

  for (const loc of locales) {
    for (const p of pages) {
      entries.push({
        url: `${BASE}${loc}${p}`,
        lastModified: new Date(),
        changeFrequency: "weekly",
        priority: p === "/" ? 1.0 : 0.8,
        alternates: {
          languages: {
            ja: `${BASE}/`,
            en: `${BASE}/en/`,
            zh: `${BASE}/zh/`,
            "x-default": `${BASE}/`,
          },
        },
      });
    }
  }
  return entries;
}
