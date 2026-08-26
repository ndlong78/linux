import { page, esc } from "./layout.js";
import { allPosts, axes } from "../content.js";
import { slugify } from "../slug.js";
import site from "../../site.json";

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

export function renderHome() {
  const posts = allPosts();
  const items = posts.length
    ? posts.map(card).join("\n")
    : '<li class="post-empty">Chưa có bài nào. Bài đầu tiên đang trên đường tới.</li>';
  return page({
    title: site.title,
    description: site.description,
    canonicalPath: "",
    body: `<section class="hero">
<h1>${esc(site.title)}</h1>
<p class="hero-lede">${esc(site.description)}</p>
${axisNav(axes())}
</section>
<section class="post-index" aria-label="Danh sách bài">
<h2 class="section-label">Bài đã đăng</h2>
<ol class="post-list">
${items}
</ol>
</section>`,
  });
}
