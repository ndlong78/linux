// Trang trục và phép tạo slug tiếng Việt.
//
// Slug chạy ở hai chỗ — lúc sinh link và lúc router khớp đường dẫn. Sai lệch
// giữa hai chỗ đó cho ra link 404 mà HTML vẫn hợp lệ, nên nó phải là một hàm
// dùng chung và hàm đó phải có test riêng.

import { describe, expect, test, vi } from "vitest";
import site from "../site.json";
import { slugify } from "../src/slug.js";

vi.mock("../content/manifest.json", async () => {
  const fixture = await import("./fixtures/manifest.json");
  return { default: fixture.default };
});

const { handle } = await import("../src/index.js");
const { axes, postsInAxis } = await import("../src/content.js");

const get = (path) => handle(new Request(new URL(path, site.url)));
const text = async (path) => (await get(path)).text();

describe("slugify", () => {
  test.each([
    ["Nền tảng", "nen-tang"],
    ["Networking", "networking"],
    ["Tiến trình & dịch vụ", "tien-trinh-dich-vu"],
    ["Quan sát & sự cố", "quan-sat-su-co"],
    ["Lưu trữ", "luu-tru"],
  ])("%s → %s", (input, expected) => {
    expect(slugify(input)).toBe(expected);
  });

  test("chữ đ phải thành d, không bị bỏ mất", () => {
    // `đ` không tổ hợp được nên NFD không tách được dấu của nó: quên thay riêng
    // thì "tự động hoá" ra "t-ng-ho".
    expect(slugify("Shell & tự động hoá")).toBe("shell-tu-dong-hoa");
    expect(slugify("Đường dẫn")).toBe("duong-dan");
  });

  test("kết quả luôn an toàn cho URL", () => {
    expect(slugify("  Ổ đĩa / phân vùng!  ")).toBe("o-dia-phan-vung");
    expect(slugify("Ổ đĩa")).toMatch(/^[a-z0-9-]+$/);
  });
});

describe("trục", () => {
  test("mỗi trục cho một slug khác nhau", () => {
    // Hai trục trùng slug thì một trong hai không bao giờ mở được.
    const slugs = axes().map((axis) => axis.slug);
    expect(new Set(slugs).size).toBe(slugs.length);
  });

  test("trang trục liệt kê đúng bài của trục đó", async () => {
    const html = await text("/truc/networking");
    expect(html).toContain("Bài ví dụ dùng cho test cổng nội dung");
    expect(html).toContain("Bài ví dụ thứ hai, cùng trục với bài một");
    expect(html).not.toContain("Bài ví dụ chỉ dành cho Linux");
  });

  test("trang trục xếp cũ nhất trước, ngược với trang chủ", async () => {
    // Trang chủ trả lời "có gì mới"; trang trục trả lời "bắt đầu từ đâu".
    const axis = await text("/truc/networking");
    const home = await text("/");
    expect(axis.indexOf("#001")).toBeLessThan(axis.indexOf("#002"));
    expect(home.indexOf("#002")).toBeLessThan(home.indexOf("#001"));
  });

  test("trục không tồn tại trả 404", async () => {
    expect((await get("/truc/khong-co-that")).status).toBe(404);
  });

  test("chip trục trên trang bài dẫn tới trang trục", async () => {
    const html = await text("/posts/post-001-vi-du");
    expect(html).toContain('href="/truc/networking"');
  });

  test("trang chủ có lối vào theo trục", async () => {
    const html = await text("/");
    expect(html).toContain('class="axis-nav"');
    expect(html).toContain('href="/truc/nen-tang"');
  });

  test("sitemap có trang trục", async () => {
    const xml = await text("/sitemap.xml");
    for (const axis of axes()) {
      expect(xml).toContain(`${site.url}truc/${axis.slug}`);
    }
  });

  test("postsInAxis chỉ nhận slug, không nhận tên có dấu", () => {
    expect(postsInAxis("networking")).toHaveLength(2);
    expect(postsInAxis("Networking")).toHaveLength(0);
  });
});
