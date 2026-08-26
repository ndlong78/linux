// Trang trục: mọi bài cùng một trục, cũ nhất trước.
//
// Trang chủ xếp theo thời gian vì nó trả lời "có gì mới". Trang trục xếp ngược
// lại vì nó trả lời câu khác: "học chủ đề này thì bắt đầu từ đâu" — và câu đó
// chỉ đúng khi đọc từ bài đầu tiên.

import { page, esc } from "./layout.js";
import { postsInAxis } from "../content.js";
import { slugify } from "../slug.js";
import site from "../../site.json";

export function renderAxis(slug) {
  const posts = postsInAxis(slug);
  if (!posts.length) return null;
  const name = posts[0].axis;

  const items = posts
    .map(
      (post) => `<li class="post-card">
<a class="post-card-link" href="/posts/${esc(post.slug)}">
<span class="post-card-issue">#${String(post.issue).padStart(3, "0")}</span>
<span class="post-card-body">
<span class="post-card-title">${esc(post.title)}</span>
<span class="post-card-lede">${esc(post.lede)}</span>
</span>
</a>
</li>`,
    )
    .join("\n");

  const count = posts.length;
  return page({
    title: `${name} — ${site.title}`,
    description: `${count} bài thuộc trục ${name} trong series ${site.title}, xếp theo thứ tự nên đọc.`,
    canonicalPath: `truc/${slugify(name)}`,
    body: `<section class="hero">
<p class="section-label">Trục</p>
<h1>${esc(name)}</h1>
<p class="hero-lede">${count} bài, xếp theo thứ tự nên đọc.</p>
</section>
<section class="post-index" aria-label="Bài trong trục ${esc(name)}">
<ol class="post-list">
${items}
</ol>
</section>
<p class="back-link"><a href="/">← Tất cả các bài</a></p>`,
  });
}
