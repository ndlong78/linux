// Kiểm renderer trên kho nội dung thật của bộ test: hai fixture cùng trục.
//
// Manifest dùng ở đây do chính `tools/build_manifest.py` dựng ra (xem script
// `manifest:fixtures`), không phải một object viết tay trong test. Nhờ vậy nếu
// renderer đọc một trường mà bước dựng manifest không mang theo thì test đỏ —
// chứ không phải phát hiện lúc deploy.

import { describe, expect, test, vi } from "vitest";
import site from "../site.json";

vi.mock("../content/manifest.json", async () => {
  const fixture = await import("./fixtures/manifest.json");
  return { default: fixture.default };
});

const { handle } = await import("../src/index.js");

// Host lấy từ site.json chứ không viết cứng: đổi domain phải là đổi đúng một
// giá trị, kể cả với bộ test.
const get = (path) => handle(new Request(new URL(path, site.url)));
const text = async (path) => (await get(path)).text();

const POST_1 = "/posts/post-001-vi-du";
const POST_2 = "/posts/post-002-vi-du";

/** Nội dung khối JSON-LD của trang, đã parse. */
function structuredData(html) {
  const match = html.match(
    /<script type="application\/ld\+json" id="ld-meta">(.*?)<\/script>/s,
  );
  expect(match, "trang bài phải có khối ld-meta").not.toBeNull();
  return { raw: match[1], data: JSON.parse(match[1]) };
}

describe("router", () => {
  test("slug không tồn tại trả 404 và vẫn là một trang hoàn chỉnh", async () => {
    const response = await get("/posts/khong-co-that");
    expect(response.status).toBe(404);
    const html = await response.text();
    // Mẩu HTML trần không có <meta charset> — tiếng Việt sẽ hỏng theo đoán mò
    // của trình duyệt.
    expect(html).toContain("<!DOCTYPE html>");
    expect(html).toContain(`<html lang="${site.language}">`);
    expect(html).toContain('<meta charset="UTF-8">');
    expect(html).toContain("Không tìm thấy");
    // Trang lỗi không bao giờ được index, kể cả sau khi site bỏ noindex.
    expect(html).toContain('content="noindex, nofollow"');
  });

  test("chỉ nhận GET/HEAD", () => {
    const response = handle(new Request(site.url, { method: "POST" }));
    expect(response.status).toBe(405);
    expect(response.headers.get("allow")).toBe("GET, HEAD");
  });
});

describe("trang chủ", () => {
  test("liệt kê bài, mới nhất trước", async () => {
    const html = await text("/");
    expect(html).toContain("Bài ví dụ dùng cho test cổng nội dung");
    expect(html).toContain("Bài ví dụ thứ hai, cùng trục với bài một");
    expect(html.indexOf("#002")).toBeLessThan(html.indexOf("#001"));
  });
});

describe("trang bài", () => {
  test("khung sinh từ metadata, thân bài lấy nguyên fragment", async () => {
    const response = await get(POST_1);
    expect(response.status).toBe(200);
    const html = await response.text();
    expect(html).toContain("<h1>Bài ví dụ dùng cho test cổng nội dung</h1>");
    expect(html).toContain('<p class="eyebrow">Networking · Ví dụ</p>');
    expect(html).toContain('<meta property="og:type" content="article">');
    expect(html).toContain(
      `<link rel="canonical" href="${site.url}posts/post-001-vi-du">`,
    );
    // fragment vào nguyên vẹn, không bị escape
    expect(html).toContain('<pre class="bsd"><code class="language-bash">ifconfig -a</code></pre>');
  });

  test("nguồn trong meta được render ra trang", async () => {
    // Bắt tác giả khai hai nguồn official/upstream rồi giấu đi là biến quy tắc
    // đó thành nghi thức.
    const html = await text(POST_1);
    expect(html).toContain("man7.org — ip(8)");
    expect(html).toContain("https://man7.org/linux/man-pages/man8/ip.8.html");
    expect(html).toContain("FreeBSD Handbook — Network");
    expect(html).toContain("docs.freebsd.org");
    expect(html).toContain("upstream");
  });

  test("xuất xứ: đã kiểm trên đâu, kiểm lần cuối bao giờ", async () => {
    const html = await text(POST_1);
    expect(html).toContain("Ubuntu 24.04 LTS, FreeBSD 14.4-RELEASE");
    expect(html).toContain('<time datetime="2026-06-01">');
  });

  test("changes_system=false thì không có cảnh báo thay đổi hệ thống", async () => {
    expect(await text(POST_1)).not.toContain("changes-system");
  });
});

describe("JSON-LD sinh từ meta.json", () => {
  test("khớp đúng metadata, không phải bản viết tay thứ hai", async () => {
    const { data } = structuredData(await text(POST_1));
    expect(data.headline).toBe("Bài ví dụ dùng cho test cổng nội dung");
    expect(data.datePublished).toBe("2026-06-01");
    expect(data.dateModified).toBe("2026-06-01");
    expect(data.inLanguage).toBe(site.language);
    expect(data.url).toBe(`${site.url}posts/post-001-vi-du`);
    expect(data.citation).toHaveLength(2);
  });

  test("không có ký tự thô nào đóng sớm được thẻ script", async () => {
    const { raw } = structuredData(await text(POST_1));
    expect(raw).not.toContain("<");
    expect(raw).not.toContain(">");
  });
});

describe("điều hướng cùng trục", () => {
  // Ô trống vẫn được render (chứ không bỏ hẳn) để lưới hai cột không nhảy chỗ
  // giữa bài đầu trục và bài giữa trục.
  const EMPTY = '<span class="series-link is-empty" aria-hidden="true"></span>';

  test("bài đầu trục: ô trước bỏ trống, ô sau trỏ tới bài kế", async () => {
    const html = await text(POST_1);
    expect(html).toContain(`<div class="series-links">${EMPTY}<a class="series-link next"`);
    expect(html).toContain('class="series-link next" href="/posts/post-002-vi-du"');
  });

  test("bài cuối trục: ô trước trỏ ngược, ô sau bỏ trống", async () => {
    const html = await text(POST_2);
    expect(html).toContain('class="series-link previous" href="/posts/post-001-vi-du"');
    expect(html).toContain(`${EMPTY}</div>`);
  });
});

describe("feed và sitemap", () => {
  test("feed có đủ bài, mới nhất trước, pubDate hợp lệ", async () => {
    const xml = await text("/feed.xml");
    expect(xml.indexOf("post-002-vi-du")).toBeLessThan(xml.indexOf("post-001-vi-du"));
    expect(xml).toContain('rel="self"');
    const pubDate = xml.match(/<pubDate>(.*?)<\/pubDate>/)[1];
    expect(Number.isNaN(Date.parse(pubDate))).toBe(false);
  });

  test("feed dùng description chứ không dùng lede", async () => {
    const xml = await text("/feed.xml");
    expect(xml).toContain("Bài fixture cho bộ test");
    expect(xml).not.toContain("Fragment tối thiểu nhưng hợp lệ");
  });

  test("sitemap lấy lastmod từ last_verified", async () => {
    const xml = await text("/sitemap.xml");
    expect(xml).toContain(
      `<url><loc>${site.url}posts/post-002-vi-du</loc><lastmod>2026-06-02</lastmod></url>`,
    );
  });
});

describe("domain đọc từ site.json", () => {
  test("canonical và feed dùng đúng host cấu hình", async () => {
    const html = await text("/");
    expect(html).toContain(`<link rel="canonical" href="${site.url}">`);
    expect(html).toContain(`href="${site.url}feed.xml"`);
  });

  test("không rò host nào khác host trong site.json", async () => {
    // Bắt cả domain của linux-daily lẫn domain cũ của chính site này còn sót
    // lại sau một lần đổi tên — cả hai đều từng là giá trị đúng.
    const hosts = new Set(
      [...(await text("/")).matchAll(/https?:\/\/([^/"'\s]+)/g)].map((m) => m[1]),
    );
    expect([...hosts]).toEqual([new URL(site.url).host]);
  });

  test("tiêu đề trang bài: số hiệu trước, tên bài sau, không kèm tên site", async () => {
    const title = (await text(POST_1)).match(/<title>(.*?)<\/title>/)[1];
    expect(title).toBe("#001 · Bài ví dụ dùng cho test cổng nội dung");
  });

  test("tiêu đề render ra không vượt ngưỡng mà cổng nội dung gác", async () => {
    // Cổng nội dung giới hạn độ dài meta.title dựa trên hình dạng tiêu đề ở
    // src/render/post.js. Đổi hình dạng đó mà quên ngưỡng bên kia thì test này đỏ.
    for (const path of [POST_1, POST_2]) {
      const title = (await text(path)).match(/<title>(.*?)<\/title>/)[1];
      expect(title.length).toBeLessThanOrEqual(60);
    }
  });

  test("tên site vẫn đọc từ site.json ở những chỗ nó xuất hiện", async () => {
    const html = await text(POST_1);
    expect(html).toContain(`<meta property="og:site_name" content="${site.title}">`);
    expect(html).toContain(`<a class="global-nav-brand" href="/">${site.title}</a>`);
  });
});

describe("chạy song song với linux-daily", () => {
  test("noindex bật thì mọi trang HTML mang thẻ robots", async () => {
    expect(site.noindex).toBe(true);
    for (const path of ["/", POST_1]) {
      expect(await text(path)).toContain('content="noindex, nofollow"');
    }
  });

  test("robots.txt chặn toàn bộ khi còn noindex", async () => {
    const body = await text("/robots.txt");
    expect(body).toContain("Disallow: /");
    expect(body).not.toContain("Allow: /");
  });
});
