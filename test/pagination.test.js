// Phân trang danh sách bài.
//
// Fixture thật chỉ có 3 bài, mà ngưỡng phân trang là 30 — nên ở đây manifest
// được nhân bản thành 70 bài để bộ test đi qua đúng đường mà site sẽ đi khi kho
// bài lớn lên. Nhân từ fixture chứ không viết tay: trường nào renderer đọc mà
// build_manifest.py không mang theo thì vẫn đỏ như ở render.test.js.

import { describe, expect, test, vi } from "vitest";
import site from "../site.json";

const TOTAL = 70;

vi.mock("../content/manifest.json", async () => {
  const fixture = await import("./fixtures/manifest.json");
  const seed = fixture.default.posts;
  const posts = Array.from({ length: TOTAL }, (_, i) => ({
    ...seed[i % seed.length],
    issue: i + 1,
    slug: `post-${String(i + 1).padStart(3, "0")}-nhan-ban`,
    title: `Bài nhân bản số ${i + 1}`,
    // Toàn bộ nằm ở quá khứ: bài chưa tới ngày sẽ bị lọc khỏi danh sách và làm
    // sai mọi phép đếm trang bên dưới.
    date: "2026-06-01",
  }));
  return { default: { posts, bodies: fixture.default.bodies } };
});

const { handle } = await import("../src/index.js");
const { postsPage, POSTS_PER_PAGE } = await import("../src/content.js");
const { renderHome } = await import("../src/render/home.js");

const get = (path) => handle(new Request(new URL(path, site.url)));
const text = async (path) => (await get(path)).text();

const PAGES = Math.ceil(TOTAL / POSTS_PER_PAGE);

describe("postsPage", () => {
  test("cắt đúng lát và đếm đúng số trang", () => {
    const first = postsPage(1, { size: 10 });
    expect(first.posts).toHaveLength(10);
    expect(first.pageCount).toBe(7);
    expect(first.total).toBe(TOTAL);
    // Mới nhất trước: bài số 70 đứng đầu trang 1.
    expect(first.posts[0].issue).toBe(TOTAL);
    expect(postsPage(2, { size: 10 }).posts[0].issue).toBe(60);
  });

  test("trang cuối có thể ngắn hơn một trang đầy", () => {
    const last = postsPage(8, { size: 9 });
    expect(last.pageCount).toBe(8);
    expect(last.posts).toHaveLength(TOTAL - 7 * 9);
  });

  test("số trang ngoài khoảng trả null chứ không kẹp về trang 1", () => {
    // Kẹp về trang 1 sẽ biến mọi số thành một URL hợp lệ có cùng nội dung.
    expect(postsPage(0, { size: 10 })).toBeNull();
    expect(postsPage(8, { size: 10 })).toBeNull();
    expect(postsPage(-1, { size: 10 })).toBeNull();
    expect(postsPage(1.5, { size: 10 })).toBeNull();
    expect(postsPage(Number.NaN, { size: 10 })).toBeNull();
  });

  test("mỗi bài xuất hiện đúng một lần khi ghép hết các trang", () => {
    const size = 9;
    const seen = [];
    for (let n = 1; n <= postsPage(1, { size }).pageCount; n++) {
      seen.push(...postsPage(n, { size }).posts.map((post) => post.issue));
    }
    expect(seen).toHaveLength(TOTAL);
    expect(new Set(seen).size).toBe(TOTAL);
  });
});

describe("định tuyến /trang/N", () => {
  test("trang chủ chỉ hiện một trang bài, không đổ hết kho", async () => {
    const html = await text("/");
    const cards = html.match(/class="post-card"/g) || [];
    expect(cards).toHaveLength(POSTS_PER_PAGE);
    expect(html).toContain("Bài nhân bản số 70");
    expect(html).not.toContain("Bài nhân bản số 1<");
  });

  test("trang 2 mở được và nối tiếp trang 1", async () => {
    const response = await get("/trang/2");
    expect(response.status).toBe(200);
    const html = await response.text();
    expect(html).toContain(`Trang 2 / ${PAGES}`);
    expect(html).toContain('rel="prev" href="/"');
    expect(html).toContain('rel="next" href="/trang/3"');
  });

  test("trang cuối không có link cũ hơn", async () => {
    const html = await text(`/trang/${PAGES}`);
    expect(html).toContain(`Trang ${PAGES} / ${PAGES}`);
    expect(html).not.toContain('rel="next"');
    expect(html).toContain('rel="prev"');
    // Bài cũ nhất phải tới được — đó là toàn bộ lý do phân trang thay vì cắt cụt.
    expect(html).toContain("Bài nhân bản số 1<");
  });

  test("/trang/1 chuyển hướng vĩnh viễn về gốc", async () => {
    const response = await get("/trang/1");
    expect(response.status).toBe(301);
    expect(response.headers.get("location")).toBe("/");
  });

  test("số trang vượt khoảng ra 404", async () => {
    expect((await get(`/trang/${PAGES + 1}`)).status).toBe(404);
  });

  test("dạng số không chuẩn ra 404 chứ không ra bản trùng của trang 2", async () => {
    for (const path of ["/trang/02", "/trang/2.0", "/trang/abc", "/trang/", "/trang/-1", "/trang/2/"]) {
      expect((await get(path)).status, path).toBe(404);
    }
  });
});

describe("thẻ meta của trang phân trang", () => {
  test("mỗi trang có canonical riêng", async () => {
    expect(await text("/")).toContain(`<link rel="canonical" href="${site.url}">`);
    expect(await text("/trang/2")).toContain(
      `<link rel="canonical" href="${new URL("trang/2", site.url)}">`,
    );
  });

  test("trang 2 trở đi có title và description riêng", async () => {
    const html = await text("/trang/2");
    expect(html).toContain(`<title>Trang 2 — ${site.title}</title>`);
    // Trùng description với trang chủ là tự nộp mấy trang gần-trùng cho bot.
    expect(html).not.toContain(`content="${site.description}"`);
  });

  test("tiêu đề danh sách không lặp lại trên trang trong", async () => {
    // Trang 1 lấy tên site làm h1 nên còn cần nhãn "Bài đã đăng" để mở đầu danh
    // sách; trang 2 trở đi đã dùng đúng câu đó làm h1 rồi.
    const second = await text("/trang/2");
    expect(second.match(/Bài đã đăng/g)).toHaveLength(1);
    expect(await text("/")).toContain('class="section-label">Bài đã đăng</h2>');
  });

  test("lời giới thiệu series chỉ nằm ở trang 1", async () => {
    expect(await text("/")).toContain('class="axis-nav"');
    const second = await text("/trang/2");
    expect(second).not.toContain('class="axis-nav"');
    expect(second).toContain("hero-compact");
  });
});

describe("sitemap", () => {
  test("liệt kê mọi trang phân trang", async () => {
    const xml = await text(`/${site.sitemap_path}`);
    for (let n = 2; n <= PAGES; n++) {
      expect(xml).toContain(`<loc>${new URL(`trang/${n}`, site.url)}</loc>`);
    }
    // `/trang/1` là bản trùng của gốc, không được vào sitemap.
    expect(xml).not.toContain(`<loc>${new URL("trang/1", site.url)}</loc>`);
  });
});

describe("kho nhỏ", () => {
  test("một trang thì không hiện thanh phân trang", () => {
    const html = renderHome(1, { size: 1000 });
    expect(html).not.toContain('class="pagination"');
  });
});
