# Linux | Unix Daily — bản dynamic

Series bài học Linux/Unix system administration bằng tiếng Việt, render tại request
bằng Cloudflare Workers. Không có file HTML dẫn xuất nào trong git.

Chạy trên `nix.no.id.vn`. Bản static tiền nhiệm là
[`ndlong78/linux-daily`](https://github.com/ndlong78/linux-daily), vẫn đang phục vụ
trên `linux.no.id.vn`. Repo này bắt đầu lại từ đầu về nội dung.

## Vì sao dynamic

Bản static commit HTML đã render vào git và gác bằng so sánh byte-exact. Cách đó
đúng, nhưng kéo theo: mỗi bài mới phải dựng lại cả cụm artifact (`index.html`,
`feed.xml`, `sitemap.xml`, `search-index.json`, related-nav của các bài lân cận),
và agent không có Python runtime thì phải nhờ một workflow riêng dựng hộ.

Đo trên kho linux-daily: **34% dung lượng bài là khung lặp lại** — head/og, nav,
masthead, footer. Ở đây khung là một hàm.

## Bố cục

```
site.json                     cấu hình site; đổi domain là đổi một giá trị
content/posts/<slug>/
  meta.json                   metadata — nguồn sự thật duy nhất của bài
  body.html                   fragment thân bài
content/manifest.json         artifact dẫn xuất, KHÔNG commit (tools/build_manifest.py)
src/
  index.js                    router
  content.js                  truy cập kho nội dung
  render/                     layout, post, home, notfound, feed/sitemap
tools/
  content.py                  đọc kho nội dung (dùng chung)
  build_manifest.py           gộp kho nội dung thành manifest cho bundle
  validate_content.py         cổng nội dung
assets/style.css              CSS — phục vụ qua Workers static assets
test/                         vitest + pytest, chung một bộ fixture
```

## Nội dung là HTML fragment, không phải Markdown

Có chủ đích. Bộ validator của series kiểm `code-label`, `data-run-as`,
`<pre class="bsd">`, số SVG/figcaption — toàn thứ chỉ tồn tại trong HTML. Chuyển
sang Markdown là vứt lớp kiểm định đã bắt được lỗi thật (metadata lệch, nguồn
không tồn tại, thiếu khối FreeBSD).

Fragment = thân bài. Head, nav, masthead, related-nav, footer do renderer sinh.

`description` là trường metadata **riêng**, không suy từ `lede`: đo trên 56 bài của
linux-daily thì 34 bài có description khác lede. Gộp hai trường là mất SEO copy.

## Metadata sinh ra trang, không chỉ để kiểm

Cổng nội dung bắt mỗi bài khai `sources` (tối thiểu hai nguồn official/upstream),
`tested_on`, `last_verified`, `changes_system`. Renderer hiển thị đủ những trường
đó ở cuối bài, và sinh luôn khối JSON-LD từ chúng.

Đây là chỗ bản static hỏng: khối `<script id="ld-meta">` được viết tay cạnh phần
hiển thị, tức hai bản của cùng một dữ liệu — và chúng lệch nhau thật. Ở đây
metadata chỉ tồn tại trong `meta.json`; mọi thứ khác là hàm của nó. Bắt tác giả
khai một trường rồi không render nó ra là biến quy tắc thành nghi thức: chỉ cần
một lần không ai đọc là nó bắt đầu sai mà không ai biết.

## Chạy

```bash
npm install
npm test          # dựng manifest rồi chạy vitest
npm run gate      # cổng nội dung + pytest + vitest — chạy trước khi merge
npm run dev       # wrangler dev
```

Bộ test JS chạy trên chính manifest do `tools/build_manifest.py` dựng từ
`test/fixtures/` — không phải object viết tay. Renderer đọc một trường mà bước
dựng manifest không mang theo thì test đỏ, chứ không phải phát hiện lúc deploy.

## Bản nháp

Bài chưa chạy thật xong nằm ở `content/drafts/<slug>/`, không phải `content/posts/`.
Cổng nội dung từ chối mọi `review_status` khác `reviewed`, và đó là hành vi đúng:
`reviewed` là chữ ký nói rằng từng lệnh trong bài đã được chạy trên đúng những hệ
ghi ở `tested_on`. Không ai ký hộ được chữ ký đó.

```bash
npm run gate:draft   # kiểm nháp bằng đúng bộ quy tắc, chỉ trừ chữ ký review
npm run dev:draft    # dựng manifest từ content/drafts/ rồi wrangler dev để xem thử
```

`--allow-draft` nới đúng một quy tắc chứ không nới bộ quy tắc: thiếu heading, thiếu
khối FreeBSD, nguồn sai dạng — vẫn đỏ ngay lúc còn nháp.

Khi bài đã chạy thật:

```bash
git mv content/drafts/<slug> content/posts/<slug>
```

rồi sửa `review_status` thành `reviewed`, cập nhật `tested_on` và `last_verified`
cho khớp với những gì bạn vừa chạy, và chạy `npm run gate`.

## Đang chạy song song

`site.json` đặt `noindex: true` trong khi `linux.no.id.vn` còn phục vụ nội dung
tương tự — hai domain cùng nội dung sẽ bị tính duplicate content. Tắt cờ đó khi
`nix.no.id.vn` tiếp quản hẳn.
