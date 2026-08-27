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
import { slugify } from "./slug.js";

/** @typedef {{issue:number,date:string,level:number,axis:string,slug:string,
 *   title:string,lede:string,description:string,eyebrow:string}} PostMeta */

// Ngày trong `meta.date` là ngày theo giờ Việt Nam, không phải UTC: bài của một
// series hằng ngày phải lên đúng 00:00 giờ bạn đọc, không phải 07:00.
const PUBLISH_OFFSET = "+07:00";

/**
 * Thứ tự bài KHÔNG phụ thuộc thời gian — `issue` cố định từ lúc bài ra đời —
 * nên sắp một lần lúc khởi tạo module thay vì mỗi request. Chỉ bộ lọc theo ngày
 * mới cần chạy lại từng lần, và lọc là O(n) chứ không phải O(n log n).
 *
 * Đo trên kho nhân bản: ở 2000 bài, sắp lại mỗi request tốn ~1.2 ms cho một
 * trang bài — mà trang bài chỉ cần đúng một phần tử trong mảng đó.
 */
const BY_ISSUE_DESC = [...manifest.posts].sort((a, b) => b.issue - a.issue);

// slugify() chuẩn hoá Unicode và bỏ dấu — không đắt, nhưng gọi nó một lần cho
// mỗi bài ở MỖI request trang trục thì thành O(n) lần chuẩn hoá cho một trang
// chỉ hiện vài bài. Tên trục là tập nhỏ và cố định, nên nhớ luôn kết quả.
const AXIS_SLUG = new Map();
function axisSlug(name) {
  let slug = AXIS_SLUG.get(name);
  if (slug === undefined) {
    slug = slugify(name);
    AXIS_SLUG.set(name, slug);
  }
  return slug;
}

/** Số bài mỗi trang của danh sách. Xem `postsPage` để biết vì sao có giới hạn. */
export const POSTS_PER_PAGE = 30;

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
  return BY_ISSUE_DESC.filter((post) => isPublished(post, now));
}

/**
 * Một trang của danh sách bài, mới nhất trước.
 *
 * Trang chủ không thể đổ hết bài ra được: mỗi thẻ bài tốn ~0.67 KB HTML, nên ở
 * 500 bài trang chủ nặng 336 KB — cho một trang chỉ để liệt kê. Với nhịp hai
 * bài/tuần thì mốc khó chịu (~150 bài) tới trong khoảng một năm.
 *
 * Số trang ngoài khoảng trả về null chứ không kẹp về trang 1: `/trang/99` là
 * một URL không tồn tại, và 404 nói đúng điều đó. Kẹp về trang 1 sẽ sinh vô số
 * URL cùng nội dung.
 *
 * @returns {{number:number,pageCount:number,total:number,posts:PostMeta[]}|null}
 */
export function postsPage(number, { now = Date.now(), size = POSTS_PER_PAGE } = {}) {
  const posts = allPosts(now);
  // Kho rỗng vẫn có trang 1 — để trang chủ hiện được lời nhắn "chưa có bài nào"
  // thay vì 404.
  const pageCount = Math.max(1, Math.ceil(posts.length / size));
  if (!Number.isInteger(number) || number < 1 || number > pageCount) return null;
  const from = (number - 1) * size;
  return { number, pageCount, total: posts.length, posts: posts.slice(from, from + size) };
}

/**
 * Bài chưa tới ngày thì URL của nó cũng chưa tồn tại — trả undefined để router
 * ra 404. Để nó mở được bằng đường dẫn trực tiếp là xuất bản sớm bằng cửa sau.
 * @returns {PostMeta|undefined}
 */
export function postBySlug(slug, now = Date.now()) {
  return BY_ISSUE_DESC.find((post) => post.slug === slug && isPublished(post, now));
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
  // BY_ISSUE_DESC đã sắp sẵn, nên lọc xong chỉ cần đảo chiều để có cũ-nhất-trước.
  const sameAxis = allPosts(now)
    .filter((item) => item.axis === post.axis)
    .reverse();
  const at = sameAxis.findIndex((item) => item.issue === post.issue);
  return {
    previous: at > 0 ? sameAxis[at - 1] : null,
    next: at >= 0 && at < sameAxis.length - 1 ? sameAxis[at + 1] : null,
  };
}

/** Mọi trục có bài đã xuất bản, kèm số bài — dùng cho trang chủ và sitemap. */
export function axes(now = Date.now()) {
  const byName = new Map();
  for (const post of allPosts(now)) {
    const entry = byName.get(post.axis) || { name: post.axis, slug: axisSlug(post.axis), count: 0 };
    entry.count += 1;
    byName.set(post.axis, entry);
  }
  return [...byName.values()].sort((a, b) => a.name.localeCompare(b.name, "vi"));
}

/**
 * Bài trong một trục, CŨ NHẤT TRƯỚC.
 * Trang chủ xếp mới nhất trước vì nó trả lời "có gì mới"; trang trục xếp ngược
 * lại vì nó trả lời "bắt đầu từ đâu".
 *
 * Trang trục không phân trang: mỗi trục chỉ chiếm 1/26 kho bài, nên ngay cả ở
 * 500 bài một trục cũng chỉ khoảng 20 bài. Và cắt đôi một lộ trình học là hỏng
 * đúng thứ trang này tồn tại để làm.
 */
export function postsInAxis(slug, now = Date.now()) {
  return allPosts(now)
    .filter((post) => axisSlug(post.axis) === slug)
    .reverse();
}
