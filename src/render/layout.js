// Khung trang: head, nav, footer. Đây là phần mà bản static phải commit lặp lại
// vào từng file — đo trên kho linux-daily là 34% tổng dung lượng. Ở đây nó là
// một hàm.

import site from "../../site.json";

/** Escape cho text node và attribute value. */
export function esc(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/** URL tuyệt đối theo `site.url` — đổi domain là đổi một giá trị trong site.json. */
export function absolute(path) {
  return new URL(path.replace(/^\//, ""), site.url).toString();
}

/**
 * @param {{title:string, description:string, canonicalPath:string,
 *   ogType?:string, noindex?:boolean}} page
 */
export function head(page) {
  const canonical = absolute(page.canonicalPath);
  const lines = [
    '<meta charset="UTF-8">',
    '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
    `<title>${esc(page.title)}</title>`,
    `<meta name="description" content="${esc(page.description)}">`,
    `<link rel="canonical" href="${esc(canonical)}">`,
    `<link rel="alternate" type="application/rss+xml" title="${esc(site.title)} RSS" href="${esc(absolute(site.feed_path))}">`,
    // Workers static assets ánh xạ thư mục `assets/` vào GỐC URL, nên
    // `assets/style.css` được phục vụ ở `/style.css` chứ không phải
    // `/assets/style.css`. Đường dẫn sai thì trang vẫn 200, chỉ là không có CSS
    // — kiểu hỏng không một test HTML nào bắt được. Xem test/assets.test.js.
    '<link rel="stylesheet" href="/style.css">',
    `<meta property="og:type" content="${esc(page.ogType || "website")}">`,
    `<meta property="og:title" content="${esc(page.title)}">`,
    `<meta property="og:description" content="${esc(page.description)}">`,
    `<meta property="og:url" content="${esc(canonical)}">`,
    `<meta property="og:site_name" content="${esc(site.title)}">`,
    '<meta property="og:locale" content="vi_VN">',
  ];
  // Chạy song song với linux-daily trên domain khác: hai site cùng nội dung sẽ
  // bị tính duplicate content. Cho tới khi bản này tiếp quản hẳn, mọi trang đều
  // noindex — bật/tắt bằng site.json chứ không sửa từng trang.
  if (page.noindex ?? site.noindex) {
    lines.push('<meta name="robots" content="noindex, nofollow">');
  }
  return lines.join("\n");
}

/**
 * Nhúng JSON-LD sinh từ metadata.
 *
 * Ở bản static, khối này được viết tay trong từng trang cạnh phần hiển thị —
 * hai bản của cùng một dữ liệu, và chúng lệch nhau thật. Ở đây nó là hàm của
 * meta.json, nên không còn cửa lệch.
 *
 * `</script>` nằm trong một chuỗi bất kỳ sẽ đóng sớm thẻ script, nên escape ở
 * mức ký tự chứ không tin nội dung đầu vào.
 */
export function jsonLd(data) {
  const json = JSON.stringify(data)
    .replace(/</g, "\\u003c")
    .replace(/>/g, "\\u003e")
    .replace(/&/g, "\\u0026");
  return `<script type="application/ld+json" id="ld-meta">${json}</script>`;
}

export function page({ title, description, canonicalPath, ogType, noindex, headExtra = "", body }) {
  return `<!DOCTYPE html>
<html lang="${esc(site.language)}">
<head>
${head({ title, description, canonicalPath, ogType, noindex })}${headExtra ? `\n${headExtra}` : ""}
</head>
<body>
<a class="skip-link" href="#main">Đi tới nội dung chính</a>
<header class="site-header">
<nav class="global-nav" aria-label="Điều hướng chính">
<a class="global-nav-brand" href="/">${esc(site.title)}</a>
<span class="global-nav-links">
<a href="/${esc(site.feed_path)}">RSS</a>
</span>
</nav>
</header>
<main id="main">
${body}
</main>
<footer class="site-footer">
<p class="site-footer-brand"><a href="/">${esc(site.title)}</a></p>
<p class="site-footer-note">${esc(site.description)}</p>
<p class="site-footer-links"><a href="/${esc(site.feed_path)}">RSS</a> · <a href="/${esc(site.sitemap_path)}">Sitemap</a></p>
</footer>
</body>
</html>
`;
}
