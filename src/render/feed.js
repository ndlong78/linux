import { allPosts } from "../content.js";
import { absolute, esc } from "./layout.js";
import site from "../../site.json";

const FEED_LIMIT = 10;

export function renderFeed() {
  const items = allPosts()
    .slice(0, FEED_LIMIT)
    .map(
      (post) => `  <item>
    <title>${esc(post.title)}</title>
    <link>${esc(absolute(`posts/${post.slug}`))}</link>
    <guid isPermaLink="true">${esc(absolute(`posts/${post.slug}`))}</guid>
    <pubDate>${new Date(`${post.date}T00:00:00+07:00`).toUTCString()}</pubDate>
    <description>${esc(post.description)}</description>
  </item>`,
    )
    .join("\n");
  return `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <title>${esc(site.title)}</title>
  <link>${esc(site.url)}</link>
  <description>${esc(site.description)}</description>
  <language>${esc(site.language)}</language>
${items}
</channel></rss>
`;
}

export function renderSitemap() {
  const urls = [absolute(""), ...allPosts().map((p) => absolute(`posts/${p.slug}`))];
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.map((url) => `  <url><loc>${esc(url)}</loc></url>`).join("\n")}
</urlset>
`;
}
