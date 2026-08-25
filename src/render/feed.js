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
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>
  <title>${esc(site.title)}</title>
  <link>${esc(site.url)}</link>
  <atom:link href="${esc(absolute(site.feed_path))}" rel="self" type="application/rss+xml"/>
  <description>${esc(site.description)}</description>
  <language>${esc(site.language)}</language>
${items}
</channel></rss>
`;
}

export function renderSitemap() {
  // `lastmod` lấy từ `last_verified`, không phải `date`: bài của series được
  // kiểm lại theo bản phát hành mới của distro, và lần kiểm lại đó mới là lần
  // nội dung thay đổi.
  const entries = [
    { loc: absolute(""), lastmod: null },
    ...allPosts().map((post) => ({
      loc: absolute(`posts/${post.slug}`),
      lastmod: post.last_verified || post.date || null,
    })),
  ];
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${entries
  .map(
    ({ loc, lastmod }) =>
      `  <url><loc>${esc(loc)}</loc>${lastmod ? `<lastmod>${esc(lastmod)}</lastmod>` : ""}</url>`,
  )
  .join("\n")}
</urlset>
`;
}
