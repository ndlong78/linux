// Trang bài: khung sinh từ metadata, thân bài lấy nguyên fragment trong git.

import { page, esc } from "./layout.js";
import { postBody, seriesNeighbours } from "../content.js";

function relatedNav(post) {
  const { previous, next } = seriesNeighbours(post);
  if (!previous && !next) return "";
  const link = (item, kind) =>
    item
      ? `<a class="series-link ${kind}" href="/posts/${esc(item.slug)}"><span class="series-kicker">#${String(item.issue).padStart(3, "0")}</span><span>${esc(item.title)}</span></a>`
      : '<span class="series-link is-empty" aria-hidden="true"></span>';
  return `<nav class="related-nav" aria-label="Bài cùng trục ${esc(post.axis)}">
<div class="series-links">${link(previous, "previous")}${link(next, "next")}</div>
</nav>`;
}

export function renderPost(post) {
  const body = postBody(post.slug);
  if (body === undefined) return null;
  const issue = String(post.issue).padStart(3, "0");
  return page({
    title: `${post.title} — ${"Linux Daily"} #${issue}`,
    description: post.description,
    canonicalPath: `posts/${post.slug}`,
    ogType: "article",
    body: `<article class="post">
<div class="masthead"><span class="issue">#${issue} · ${esc(post.date)}</span></div>
<header class="post"><p class="eyebrow">${esc(post.eyebrow)}</p><h1>${esc(post.title)}</h1><p class="lede">${esc(post.lede)}</p></header>
${body}
</article>
${relatedNav(post)}`,
  });
}
