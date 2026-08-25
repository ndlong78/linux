// Router: mọi trang render tại request, không có file HTML nào trong git.

import { renderHome } from "./render/home.js";
import { renderPost } from "./render/post.js";
import { renderFeed, renderSitemap } from "./render/feed.js";
import { renderNotFound } from "./render/notfound.js";
import { postBySlug } from "./content.js";
import site from "../site.json";

const HTML = "text/html; charset=utf-8";
const XML = "application/xml; charset=utf-8";

// Trang render tại request nên không cache lâu ở edge; revalidate giữ cho bài
// mới xuất hiện ngay mà vẫn tận dụng được conditional request.
const CACHE = "public, max-age=0, must-revalidate";

function respond(body, type, status = 200) {
  return new Response(body, {
    status,
    headers: { "content-type": type, "cache-control": CACHE },
  });
}

export function handle(request) {
  const { pathname } = new URL(request.url);

  if (request.method !== "GET" && request.method !== "HEAD") {
    return new Response("Method Not Allowed", { status: 405, headers: { allow: "GET, HEAD" } });
  }

  if (pathname === "/" ) return respond(renderHome(), HTML);
  if (pathname === `/${site.feed_path}`) return respond(renderFeed(), XML);
  if (pathname === `/${site.sitemap_path}`) return respond(renderSitemap(), XML);
  if (pathname === "/robots.txt") {
    // Trong lúc chạy song song với linux-daily, chặn index để không tạo
    // duplicate content giữa hai domain.
    const body = site.noindex
      ? "User-agent: *\nDisallow: /\n"
      : `User-agent: *\nAllow: /\n\nSitemap: ${new URL(site.sitemap_path, site.url)}\n`;
    return respond(body, "text/plain; charset=utf-8");
  }

  const post = pathname.startsWith("/posts/") && postBySlug(pathname.slice("/posts/".length));
  if (post) {
    const html = renderPost(post);
    if (html) return respond(html, HTML);
  }

  return respond(renderNotFound(pathname), HTML, 404);
}

export default { fetch: (request) => handle(request) };
