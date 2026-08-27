// Danh sách bài, mới nhất trước — trang 1 ở `/`, các trang sau ở `/trang/N`.

import { page, esc, absolute } from "./layout.js";
import { postsPage, axes, POSTS_PER_PAGE } from "../content.js";
import site from "../../site.json";

/** Trang 1 sống ở gốc site, không ở `/trang/1` — một trang, một URL. */
function pagePath(number) {
  return number <= 1 ? "/" : `/trang/${number}`;
}

function card(post) {
  const issue = String(post.issue).padStart(3, "0");
  return `<li class="post-card">
<a class="post-card-link" href="/posts/${esc(post.slug)}">
<span class="post-card-issue">#${issue}</span>
<span class="post-card-body">
<span class="post-card-title">${esc(post.title)}</span>
<span class="post-card-lede">${esc(post.lede)}</span>
<span class="post-card-meta"><span class="level">L${esc(String(post.level))}</span><span class="tag">${esc(post.axis)}</span><time datetime="${esc(post.date)}">${esc(post.date)}</time></span>
</span>
</a>
</li>`;
}

/** Hàng trục dưới hero: lối vào thứ hai, cho người tới vì chủ đề chứ không vì bài mới. */
function axisNav(list) {
  if (!list.length) return "";
  const links = list
    .map(
      (axis) =>
        `<a class="tag" href="/truc/${esc(axis.slug)}">${esc(axis.name)} <span class="tag-count">${axis.count}</span></a>`,
    )
    .join("\n");
  return `<nav class="axis-nav" aria-label="Các trục">\n${links}\n</nav>`;
}

/**
 * "Mới hơn / Cũ hơn" chứ không phải "Trước / Sau": danh sách xếp ngược thời
 * gian nên "trang trước" mang hai nghĩa ngược nhau, tuỳ người đọc đang nghĩ
 * theo thứ tự trang hay theo thứ tự thời gian.
 */
function pagination({ number, pageCount }) {
  if (pageCount <= 1) return "";
  const parts = [
    number > 1
      ? `<a class="pagination-link" rel="prev" href="${esc(pagePath(number - 1))}">← Mới hơn</a>`
      : '<span class="pagination-link is-off" aria-hidden="true">← Mới hơn</span>',
    `<span class="pagination-status">Trang ${number} / ${pageCount}</span>`,
    number < pageCount
      ? `<a class="pagination-link" rel="next" href="${esc(pagePath(number + 1))}">Cũ hơn →</a>`
      : '<span class="pagination-link is-off" aria-hidden="true">Cũ hơn →</span>',
  ];
  return `<nav class="pagination" aria-label="Phân trang">\n${parts.join("\n")}\n</nav>`;
}

/**
 * Trình duyệt và bot dùng rel=prev/next để hiểu đây là một chuỗi trang chứ
 * không phải nhiều trang rời nhau cùng tiêu đề.
 */
function seriesLinks({ number, pageCount }) {
  const links = [];
  if (number > 1) links.push(`<link rel="prev" href="${esc(absolute(pagePath(number - 1)))}">`);
  if (number < pageCount) links.push(`<link rel="next" href="${esc(absolute(pagePath(number + 1)))}">`);
  return links.join("\n");
}

/**
 * @param {number} [number] số trang, 1 là trang chủ
 * @returns {string|null} null khi số trang nằm ngoài khoảng — router ra 404
 */
export function renderHome(number = 1, { now, size = POSTS_PER_PAGE } = {}) {
  const view = postsPage(number, { now: now ?? Date.now(), size });
  if (!view) return null;

  const items = view.posts.length
    ? view.posts.map(card).join("\n")
    : '<li class="post-empty">Chưa có bài nào. Bài đầu tiên đang trên đường tới.</li>';

  // Trang 1 là trang giới thiệu series; các trang sau là phần đuôi của cùng một
  // danh sách, nên không lặp lại lời giới thiệu — vừa thừa với người đọc, vừa
  // tạo mấy trang gần trùng nhau cho bot.
  const first = view.number === 1;
  const from = (view.number - 1) * size + 1;
  const to = from + view.posts.length - 1;

  const header = first
    ? `<section class="hero">
<h1>${esc(site.title)}</h1>
<p class="hero-lede">${esc(site.description)}</p>
${axisNav(axes(now))}
</section>`
    : `<section class="hero hero-compact">
<p class="section-label">Trang ${view.number} / ${view.pageCount}</p>
<h1>Bài đã đăng</h1>
<p class="hero-lede">Bài ${from}–${to} trong tổng số ${view.total}, mới nhất trước.</p>
</section>`;

  return page({
    title: first ? site.title : `Trang ${view.number} — ${site.title}`,
    description: first
      ? site.description
      : `Bài ${from}–${to} trong tổng số ${view.total} bài của series ${site.title}.`,
    canonicalPath: first ? "" : `trang/${view.number}`,
    headExtra: seriesLinks(view),
    body: `${header}
<section class="post-index" aria-label="Danh sách bài">
${first ? '<h2 class="section-label">Bài đã đăng</h2>' : ""}
<ol class="post-list">
${items}
</ol>
</section>
${pagination(view)}`,
  });
}
