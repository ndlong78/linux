// 404 cũng là một trang: cùng khung, cùng lang, cùng charset.
//
// Trả về một mẩu HTML trần (không doctype, không <html lang>) là để trình duyệt
// tự đoán encoding — với nội dung tiếng Việt thì đó là dấu hỏi trên màn hình.

import { page, esc } from "./layout.js";
import site from "../../site.json";

export function renderNotFound(pathname) {
  return page({
    title: `Không tìm thấy trang — ${site.title}`,
    description: "Không tìm thấy trang.",
    canonicalPath: "",
    // Trang lỗi thì không index kể cả khi site đã bỏ noindex.
    noindex: true,
    body: `<section class="not-found">
<h1>404</h1>
<p>Không tìm thấy <code>${esc(pathname)}</code>.</p>
<p><a href="/">Về trang chủ</a></p>
</section>`,
  });
}
