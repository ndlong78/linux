// Cờ `noindex` trong site.json điều khiển hai chỗ cùng lúc: thẻ
// <meta name="robots"> ở mọi trang HTML, và nội dung /robots.txt.
//
// Bộ test này kiểm CƠ CHẾ chứ không kiểm giá trị đang đặt. Bản trước khẳng định
// `site.noindex === true`, nên ngày bật lập chỉ mục — một thay đổi cấu hình hoàn
// toàn hợp lệ — bộ test đỏ mà không có gì hỏng. Test phải đỏ khi code sai, không
// phải khi người ta đổi ý.

import { describe, expect, test, vi } from "vitest";
import realSite from "../site.json";

/** Dựng router với một giá trị `noindex` cho trước. */
async function siteWith(noindex) {
  vi.resetModules();
  vi.doMock("../site.json", () => ({ default: { ...realSite, noindex } }));
  vi.doMock("../content/manifest.json", async () => {
    const fixture = await import("./fixtures/manifest.json");
    return { default: fixture.default };
  });
  const { handle } = await import("../src/index.js");
  return (path) => handle(new Request(new URL(path, realSite.url))).text();
}

const PAGES = ["/", "/posts/post-001-vi-du", "/truc/mang-co-ban"];

describe("noindex = true", () => {
  test("mọi trang HTML mang thẻ robots", async () => {
    const text = await siteWith(true);
    for (const path of PAGES) {
      expect(await text(path), path).toContain('content="noindex, nofollow"');
    }
  });

  test("robots.txt chặn toàn bộ và không công bố sitemap", async () => {
    const body = await (await siteWith(true))("/robots.txt");
    expect(body).toContain("Disallow: /");
    expect(body).not.toContain("Allow: /");
    // Chặn bot mà vẫn đưa sitemap là tự mâu thuẫn.
    expect(body).not.toContain("Sitemap:");
  });
});

describe("noindex = false", () => {
  test("trang HTML không còn thẻ robots", async () => {
    const text = await siteWith(false);
    for (const path of PAGES) {
      expect(await text(path), path).not.toContain('content="noindex, nofollow"');
    }
  });

  test("robots.txt mở và trỏ tới sitemap tuyệt đối", async () => {
    const body = await (await siteWith(false))("/robots.txt");
    expect(body).toContain("Allow: /");
    expect(body).not.toContain("Disallow: /");
    expect(body).toContain(`Sitemap: ${new URL(realSite.sitemap_path, realSite.url)}`);
  });
});

describe("bất kể cờ", () => {
  test("trang 404 luôn noindex", async () => {
    // Trang lỗi lọt vào kết quả tìm kiếm là hỏng theo cách không ai sửa hộ được.
    for (const flag of [true, false]) {
      const html = await (await siteWith(flag))("/posts/khong-co-that");
      expect(html, `noindex=${flag}`).toContain('content="noindex, nofollow"');
    }
  });
});
