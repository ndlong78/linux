// Router: mọi trang render tại request, không có file HTML nào trong git.

import { renderHome } from "./render/home.js";
import { renderPost } from "./render/post.js";
import { renderFeed, renderSitemap } from "./render/feed.js";
import { renderAxis } from "./render/axis.js";
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

function redirect(location) {
  return new Response(null, { status: 301, headers: { location, "cache-control": CACHE } });
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

  if (pathname.startsWith("/trang/")) {
    const raw = pathname.slice("/trang/".length);
    // Trang 1 đã sống ở gốc site. Trả nội dung ở cả `/trang/1` là tự tạo cho
    // mình một bản trùng của trang chủ, nên chuyển hướng hẳn về gốc.
    if (raw === "1") return redirect("/");
    // Chỉ số nguyên dương không có số 0 đứng đầu: `/trang/007` và `/trang/7`
    // mà cùng ra một nội dung cũng là hai URL trùng nhau.
    const html = /^[1-9][0-9]*$/.test(raw) ? renderHome(Number(raw)) : null;
    if (html) return respond(html, HTML);
  }

  if (pathname.startsWith("/truc/")) {
    const html = renderAxis(pathname.slice("/truc/".length));
    if (html) return respond(html, HTML);
  }

  const post = pathname.startsWith("/posts/") && postBySlug(pathname.slice("/posts/".length));
  if (post) {
    const html = renderPost(post);
    if (html) return respond(html, HTML);
  }

  return respond(renderNotFound(pathname), HTML, 404);
}

export default { fetch: (request) => handle(request) };
