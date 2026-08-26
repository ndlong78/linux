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

// Ngày trong `meta.date` là ngày theo giờ Việt Nam, không phải UTC: bài của một
// series hằng ngày phải lên đúng 00:00 giờ bạn đọc, không phải 07:00.
const PUBLISH_OFFSET = "+07:00";

function publishedAt(post) {
  return Date.parse(`${post.date}T00:00:00${PUBLISH_OFFSET}`);
}

/**
 * Bài có `date` ở tương lai thì chưa xuất bản.
 *
 * Đây là toàn bộ cơ chế lên lịch, và nó gần như miễn phí vì mọi trang được
 * render tại request: viết trước mười bài, merge một lần, mỗi bài tự hiện đúng
 * ngày của nó. Không cron, không job, không deploy lại — bundle đã có sẵn bài,
 * chỉ là chưa tới lúc trả nó ra.
 *
 * `date` hỏng thì coi như đã xuất bản: cổng nội dung mới là chỗ bắt lỗi định
 * dạng, còn ở đây giấu mất một bài là hỏng theo cách khó thấy hơn nhiều.
 */
export function isPublished(post, now = Date.now()) {
  const at = publishedAt(post);
  return Number.isNaN(at) || at <= now;
}

/**
 * Bài đã xuất bản, mới nhất trước.
 * `description` là trường riêng, KHÔNG suy từ `lede`: đo trên kho linux-daily
 * thì 34/56 bài có description khác lede. Gộp hai trường là mất SEO copy.
 * @returns {PostMeta[]}
 */
export function allPosts(now = Date.now()) {
  return manifest.posts.filter((post) => isPublished(post, now)).sort((a, b) => b.issue - a.issue);
}

/**
 * Bài chưa tới ngày thì URL của nó cũng chưa tồn tại — trả undefined để router
 * ra 404. Để nó mở được bằng đường dẫn trực tiếp là xuất bản sớm bằng cửa sau.
 * @returns {PostMeta|undefined}
 */
export function postBySlug(slug, now = Date.now()) {
  return allPosts(now).find((post) => post.slug === slug);
}

/** Fragment HTML của thân bài. */
export function postBody(slug) {
  return manifest.bodies[slug];
}

/**
 * Bài liền trước/liền sau theo cùng trục, dùng cho related-nav.
 * Chỉ nối tới bài đã xuất bản: link "bài sau" trỏ vào một trang 404 còn tệ hơn
 * là không có link nào.
 */
export function seriesNeighbours(post, now = Date.now()) {
  const sameAxis = allPosts(now)
    .filter((item) => item.axis === post.axis)
    .sort((a, b) => a.issue - b.issue);
  const at = sameAxis.findIndex((item) => item.issue === post.issue);
  return {
    previous: at > 0 ? sameAxis[at - 1] : null,
    next: at >= 0 && at < sameAxis.length - 1 ? sameAxis[at + 1] : null,
  };
}
