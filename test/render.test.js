import { describe, expect, test } from "vitest";
import { handle } from "../src/index.js";
import site from "../site.json";

const get = (path) => handle(new Request(`https://linux.id.vn${path}`));
const text = async (path) => (await get(path)).text();

describe("router", () => {
  test("trang chủ render được khi chưa có bài nào", async () => {
    const response = await get("/");
    expect(response.status).toBe(200);
    expect(response.headers.get("content-type")).toContain("text/html");
    expect(await response.text()).toContain("Chưa có bài nào");
  });

  test("slug không tồn tại trả 404, không phải 200 rỗng", async () => {
    const response = await get("/posts/khong-co-that");
    expect(response.status).toBe(404);
  });

  test("chỉ nhận GET/HEAD", async () => {
    const response = handle(
      new Request("https://linux.id.vn/", { method: "POST" }),
    );
    expect(response.status).toBe(405);
    expect(response.headers.get("allow")).toBe("GET, HEAD");
  });
});

describe("domain đọc từ site.json", () => {
  test("canonical và feed dùng đúng host cấu hình", async () => {
    const html = await text("/");
    expect(html).toContain(`<link rel="canonical" href="${site.url}">`);
    expect(html).toContain(`href="${site.url}feed.xml"`);
    // Không được lẫn domain của linux-daily.
    expect(html).not.toContain("linux.no.id.vn");
  });

  test("sitemap và feed cũng theo site.url", async () => {
    expect(await text("/sitemap.xml")).toContain(`<loc>${site.url}</loc>`);
    expect(await text("/feed.xml")).toContain(`<link>${site.url}</link>`);
  });
});

describe("chạy song song với linux-daily", () => {
  test("noindex bật thì mọi trang HTML mang thẻ robots", async () => {
    expect(site.noindex).toBe(true);
    expect(await text("/")).toContain('content="noindex, nofollow"');
  });

  test("robots.txt chặn toàn bộ khi còn noindex", async () => {
    const body = await text("/robots.txt");
    expect(body).toContain("Disallow: /");
    expect(body).not.toContain("Allow: /");
  });
});

describe("escape", () => {
  test("giá trị site không được chèn HTML thô vào attribute", async () => {
    const html = await text("/");
    // description của site chứa dấu phẩy/khoảng trắng; kiểm attribute không vỡ.
    const match = html.match(/<meta name="description" content="([^"]*)"/);
    expect(match).not.toBeNull();
    expect(match[1]).not.toContain("<");
  });
});
