// Kho nội dung: bài viết nằm trong git dưới dạng (metadata JSON + fragment HTML).
//
// Fragment chứ không phải trang đầy đủ — head, nav, masthead, footer do renderer
// sinh tại request. Và HTML chứ không phải Markdown: bộ validator kiểm được
// `code-label`, `data-run-as`, `<pre class="bsd">`, số SVG/figcaption chỉ đọc
// được HTML. Đổi sang Markdown là vứt lớp kiểm định đó đi.
//
// Nội dung được bundle vào Worker lúc deploy (import tĩnh), không đọc I/O mỗi
// request: kho bài của một series hằng ngày đủ nhỏ để nằm gọn trong bundle, và
// như vậy render không phụ thuộc storage nào.

import manifest from "../content/manifest.json";

/** @typedef {{issue:number,date:string,axis:string,slug:string,title:string,
 *   lede:string,description:string,eyebrow:string}} PostMeta */

/**
 * Bài đã publish, mới nhất trước.
 * `description` là trường riêng, KHÔNG suy từ `lede`: đo trên kho linux-daily
 * thì 34/56 bài có description khác lede. Gộp hai trường là mất SEO copy.
 * @returns {PostMeta[]}
 */
export function allPosts() {
  return [...manifest.posts].sort((a, b) => b.issue - a.issue);
}

/** @returns {PostMeta|undefined} */
export function postBySlug(slug) {
  return manifest.posts.find((post) => post.slug === slug);
}

/** Fragment HTML của thân bài. */
export function postBody(slug) {
  return manifest.bodies[slug];
}

/** Bài liền trước/liền sau theo cùng trục, dùng cho related-nav. */
export function seriesNeighbours(post) {
  const sameAxis = allPosts()
    .filter((item) => item.axis === post.axis)
    .sort((a, b) => a.issue - b.issue);
  const at = sameAxis.findIndex((item) => item.issue === post.issue);
  return {
    previous: at > 0 ? sameAxis[at - 1] : null,
    next: at >= 0 && at < sameAxis.length - 1 ? sameAxis[at + 1] : null,
  };
}
