// Đường dẫn tĩnh trong HTML phải trỏ tới thứ có thật.
//
// Lỗi này đã xảy ra và sống sót qua toàn bộ 133 test: `<link rel="stylesheet"
// href="/assets/style.css">` trong khi Workers static assets ánh xạ thư mục
// `assets/` vào GỐC URL, tức file được phục vụ ở `/style.css`. Trang vẫn trả
// 200, HTML vẫn đúng từng chữ, chỉ là không có một dòng CSS nào được nạp — và
// không test HTML nào bắt được, vì test đọc chuỗi chứ không đi theo link.

import { describe, expect, test, vi } from "vitest";
import { readdirSync, statSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { join, posix } from "node:path";
import site from "../site.json";

vi.mock("../content/manifest.json", async () => {
  const fixture = await import("./fixtures/manifest.json");
  return { default: fixture.default };
});

const { handle } = await import("../src/index.js");

const ASSETS = fileURLToPath(new URL("../assets/", import.meta.url));

/** Mọi file trong assets/, theo đúng URL mà Workers sẽ phục vụ chúng. */
function assetUrls(dir = ASSETS, prefix = "/") {
  const urls = new Set();
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) {
      for (const nested of assetUrls(full, posix.join(prefix, entry, "/"))) urls.add(nested);
    } else {
      urls.add(posix.join(prefix, entry));
    }
  }
  return urls;
}

/** Đường dẫn do router xử lý, không phải file tĩnh. */
const ROUTES = new Set([`/${site.feed_path}`, `/${site.sitemap_path}`, "/robots.txt"]);

const text = async (path) => (await handle(new Request(new URL(path, site.url)))).text();

describe("đường dẫn tĩnh", () => {
  test("assets/ được phục vụ ở gốc URL, không phải dưới /assets/", () => {
    const urls = assetUrls();
    expect(urls.has("/style.css")).toBe(true);
    expect(urls.has("/assets/style.css")).toBe(false);
  });

  test.each([
    ["trang chủ", "/"],
    ["trang bài", "/posts/post-001-vi-du"],
    ["404", "/posts/khong-co-that"],
  ])("%s không trỏ tới file tĩnh không tồn tại", async (_name, path) => {
    const html = await text(path);
    const urls = assetUrls();
    const refs = [...html.matchAll(/(?:href|src)="(\/[^"#?]+)"/g)].map((m) => m[1]);
    // Chỉ xét đường dẫn có phần mở rộng: đó là file, không phải route.
    const files = refs.filter((ref) => /\.[a-z0-9]{2,5}$/i.test(ref) && !ROUTES.has(ref));
    expect(files.length).toBeGreaterThan(0);
    for (const ref of files) {
      expect(urls, `${path} trỏ tới ${ref} nhưng không có file nào ở đó`).toContain(ref);
    }
  });
});
