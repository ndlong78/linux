// `esc` và `jsonLd` là hai chỗ duy nhất đứng giữa dữ liệu tác giả viết và HTML
// gửi đi. Cổng nội dung không kiểm ký tự đặc biệt trong tiêu đề — nó không cần,
// miễn là hai hàm này giữ được ranh giới.

import { describe, expect, test } from "vitest";
import { esc, jsonLd, absolute } from "../src/render/layout.js";
import site from "../site.json";

describe("esc", () => {
  test("đóng được cả text node lẫn attribute value", () => {
    expect(esc('<img src=x onerror="alert(1)">')).toBe(
      "&lt;img src=x onerror=&quot;alert(1)&quot;&gt;",
    );
  });

  test("& được escape trước, không sinh entity kép", () => {
    expect(esc("&lt;")).toBe("&amp;lt;");
  });
});

describe("jsonLd", () => {
  test("không chuỗi nào đóng sớm được thẻ script", () => {
    const html = jsonLd({ headline: "</script><script>alert(1)</script>" });
    expect(html).not.toContain("</script><script>");
    expect(html.endsWith("</script>")).toBe(true);
    const payload = html.slice(html.indexOf(">") + 1, html.lastIndexOf("<"));
    expect(JSON.parse(payload).headline).toBe("</script><script>alert(1)</script>");
  });
});

describe("absolute", () => {
  test("ghép theo site.url dù path có hay không có dấu / đầu", () => {
    expect(absolute("/feed.xml")).toBe(`${site.url}feed.xml`);
    expect(absolute("feed.xml")).toBe(`${site.url}feed.xml`);
    expect(absolute("")).toBe(site.url);
  });
});
