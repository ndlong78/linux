import { page, esc } from "./layout.js";
import { allPosts } from "../content.js";
import site from "../../site.json";

export function renderHome() {
  const posts = allPosts();
  const items = posts.length
    ? posts
        .map(
          (post) =>
            `<li><a href="/posts/${esc(post.slug)}"><span class="issue">#${String(post.issue).padStart(3, "0")}</span> ${esc(post.title)}</a><p>${esc(post.lede)}</p></li>`,
        )
        .join("\n")
    : "<li>Chưa có bài nào.</li>";
  return page({
    title: site.title,
    description: site.description,
    canonicalPath: "",
    body: `<h1>${esc(site.title)}</h1>\n<ul class="post-list">\n${items}\n</ul>`,
  });
}
