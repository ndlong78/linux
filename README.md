# Linux Daily — bản dynamic

Series bài học Linux/Unix system administration bằng tiếng Việt, render tại request
bằng Cloudflare Workers. Không có file HTML dẫn xuất nào trong git.

Bản static tiền nhiệm là [`ndlong78/linux-daily`](https://github.com/ndlong78/linux-daily),
vẫn đang chạy trên `linux.no.id.vn`. Repo này bắt đầu lại từ đầu về nội dung.

## Vì sao dynamic

Bản static commit HTML đã render vào git và gác bằng so sánh byte-exact. Cách đó
đúng, nhưng kéo theo: mỗi bài mới phải dựng lại cả cụm artifact (`index.html`,
`feed.xml`, `sitemap.xml`, `search-index.json`, related-nav của các bài lân cận),
và agent không có Python runtime thì phải nhờ một workflow riêng dựng hộ.

Đo trên kho linux-daily: **34% dung lượng bài là khung lặp lại** — head/og, nav,
masthead, footer. Ở đây khung là một hàm.

## Bố cục

```
site.json          cấu hình site; đổi domain là đổi một giá trị
content/
  manifest.json    metadata bài + fragment thân bài
src/
  index.js         router
  content.js       truy cập kho nội dung
  render/          layout, post, home, feed/sitemap
assets/            CSS, font — phục vụ qua Workers static assets
test/              vitest
```

## Nội dung là HTML fragment, không phải Markdown

Có chủ đích. Bộ validator của series kiểm `code-label`, `data-run-as`,
`<pre class="bsd">`, số SVG/figcaption — toàn thứ chỉ tồn tại trong HTML. Chuyển
sang Markdown là vứt lớp kiểm định đã bắt được lỗi thật (metadata lệch, nguồn
không tồn tại, thiếu khối FreeBSD).

Fragment = thân bài. Head, nav, masthead, related-nav, footer do renderer sinh.

`description` là trường metadata **riêng**, không suy từ `lede`: đo trên 56 bài của
linux-daily thì 34 bài có description khác lede. Gộp hai trường là mất SEO copy.

## Chạy

```bash
npm install
npm test          # vitest
npm run dev       # wrangler dev
```

## Đang chạy song song

`site.json` đặt `noindex: true` trong khi `linux.no.id.vn` còn phục vụ nội dung
tương tự — hai domain cùng nội dung sẽ bị tính duplicate content. Tắt cờ đó khi
bản này tiếp quản.
