// Kho rỗng là trạng thái thật của repo này lúc bắt đầu lại nội dung: mọi trang
// vẫn phải render, không trang nào được vỡ vì `posts` rỗng.

import { describe, expect, test, vi } from "vitest";
import site from "../site.json";

vi.mock("../content/manifest.json", () => ({ default: { posts: [], bodies: {} } }));

const { handle } = await import("../src/index.js");

const get = (path) => handle(new Request(new URL(path, site.url)));
const text = async (path) => (await get(path)).text();

describe("kho rỗng", () => {
  test("trang chủ render được khi chưa có bài nào", async () => {
    const response = await get("/");
    expect(response.status).toBe(200);
    expect(response.headers.get("content-type")).toContain("text/html");
    expect(await response.text()).toContain("Chưa có bài nào");
  });

  test("feed và sitemap vẫn là XML hợp lệ", async () => {
    expect(await text("/feed.xml")).toContain("<channel>");
    expect(await text("/sitemap.xml")).toContain("<urlset");
  });

  test("mọi slug đều 404", async () => {
    expect((await get("/posts/bat-ky")).status).toBe(404);
  });
});
