// Trang bài: khung sinh từ metadata, thân bài lấy nguyên fragment trong git.
//
// Mọi trường mà cổng nội dung bắt buộc phải có đều được render ra ở đây. Bắt
// tác giả khai `sources`, `tested_on`, `last_verified` rồi không hiển thị là
// biến chúng thành nghi thức: chỉ cần một lần không ai đọc là chúng bắt đầu sai
// mà không ai biết.

import { page, esc, absolute, jsonLd } from "./layout.js";
import { postBody, seriesNeighbours } from "../content.js";
import site from "../../site.json";

function issueNumber(post) {
  return String(post.issue).padStart(3, "0");
}

function relatedNav(post) {
  const { previous, next } = seriesNeighbours(post);
  if (!previous && !next) return "";
  const link = (item, kind) =>
    item
      ? `<a class="series-link ${kind}" href="/posts/${esc(item.slug)}"><span class="series-kicker">#${issueNumber(item)}</span><span>${esc(item.title)}</span></a>`
      : '<span class="series-link is-empty" aria-hidden="true"></span>';
  return `<nav class="related-nav" aria-label="Bài cùng trục ${esc(post.axis)}">
<div class="series-links">${link(previous, "previous")}${link(next, "next")}</div>
</nav>`;
}

/**
 * Bài khai `scope: "linux-only"` phải nói ra điều đó ở đầu trang.
 *
 * Cổng nội dung nới hai quy tắc FreeBSD cho những bài này; nếu người đọc không
 * thấy khai báo thì họ chỉ thấy một bài thiếu FreeBSD, và phải đọc hết mới biết
 * bài không dành cho mình.
 */
function scopeNote(post) {
  if (post.scope !== "linux-only") return "";
  return '<p class="scope-note" role="note">Bài này chỉ áp dụng cho Linux — chủ đề không có đối ứng trên FreeBSD.</p>';
}

/** Nguồn official/upstream — validator đòi tối thiểu hai nguồn cho mỗi bài. */
function sources(post) {
  const list = Array.isArray(post.sources) ? post.sources : [];
  if (!list.length) return "";
  const items = list
    .map((source) => {
      const host = new URL(source.url).hostname.replace(/^www\./, "");
      return `<li><a href="${esc(source.url)}" rel="noopener">${esc(source.title)}</a><span class="source-meta"><span class="source-host">${esc(host)}</span><span class="source-kind">${esc(source.kind)}</span></span></li>`;
    })
    .join("\n");
  return `<section class="sources"><h2>Nguồn</h2>\n<ol>\n${items}\n</ol></section>`;
}

/** Bài này đã chạy thật ở đâu, kiểm lần cuối bao giờ. */
function provenance(post) {
  const parts = [];
  if (Array.isArray(post.tested_on) && post.tested_on.length) {
    parts.push(`<span class="tested-on">Đã kiểm trên: ${esc(post.tested_on.join(", "))}</span>`);
  }
  if (post.last_verified) {
    parts.push(`<span class="last-verified">Kiểm lần cuối: <time datetime="${esc(post.last_verified)}">${esc(post.last_verified)}</time></span>`);
  }
  if (!parts.length) return "";
  const warning = post.changes_system
    ? '<p class="changes-system" role="note"><strong>Bài này thay đổi hệ thống.</strong> Đọc mục hoàn tác trước khi chạy.</p>'
    : "";
  return `<footer class="provenance">${warning}<p>${parts.join(" · ")}</p></footer>`;
}

function structuredData(post) {
  const url = absolute(`posts/${post.slug}`);
  return jsonLd({
    "@context": "https://schema.org",
    "@type": "TechArticle",
    headline: post.title,
    description: post.description,
    datePublished: post.date,
    dateModified: post.last_verified || post.date,
    inLanguage: site.language,
    mainEntityOfPage: url,
    url,
    isPartOf: { "@type": "CreativeWorkSeries", name: site.title, url: absolute("") },
    citation: (Array.isArray(post.sources) ? post.sources : []).map((source) => ({
      "@type": "CreativeWork",
      name: source.title,
      url: source.url,
    })),
  });
}

export function renderPost(post) {
  const body = postBody(post.slug);
  if (body === undefined) return null;
  const issue = issueNumber(post);
  return page({
    // Số hiệu đứng trước để tab trình duyệt phân biệt được các bài ngay cả khi
    // tiêu đề bị cắt. Tên site không lặp lại ở đây: nó đã có trong og:site_name,
    // trong JSON-LD và trong chính host — nối thêm vào chỉ đẩy tiêu đề vượt
    // ngưỡng cắt của trang kết quả tìm kiếm.
    title: `#${issue} · ${post.title}`,
    description: post.description,
    canonicalPath: `posts/${post.slug}`,
    ogType: "article",
    headExtra: structuredData(post),
    body: `<article class="post">
<div class="masthead">
<span class="issue">#${issue}</span>
<time class="masthead-date" datetime="${esc(post.date)}">${esc(post.date)}</time>
<span class="tag">${esc(post.axis)}</span>
</div>
<header class="post"><p class="eyebrow">${esc(post.eyebrow)}</p><h1>${esc(post.title)}</h1><p class="lede">${esc(post.lede)}</p></header>
${scopeNote(post)}
${body}
${sources(post)}
${provenance(post)}
</article>
${relatedNav(post)}`,
  });
}
