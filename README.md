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
npm run gate      # cổng nội dung + pytest + vitest + kiểm link — chạy trước khi merge
npm run dev       # wrangler dev
```

Bộ test JS chạy trên chính manifest do `tools/build_manifest.py` dựng từ
`test/fixtures/` — không phải object viết tay. Renderer đọc một trường mà bước
dựng manifest không mang theo thì test đỏ, chứ không phải phát hiện lúc deploy.

## Kiểm link

Cổng nội dung chạy offline — nó phải chạy được trong container không có egress.
Việc hỏi xem URL còn sống hay đã chết là của một công cụ riêng:

```bash
npm run links          # kiểm content/posts
npm run links:draft    # kiểm content/drafts
```

Nó phân biệt **"sai"** với **"không biết"**, và mã thoát nói rõ điều đó:

| mã | nghĩa |
|---|---|
| 0 | mọi URL đều sống |
| 1 | có URL chết (4xx) hoặc redirect vĩnh viễn (301/308) — phải sửa |
| 2 | không có URL chết, nhưng có URL không kết luận được (429, timeout, 5xx, 403) |

Phân biệt này là lý do công cụ được tách ra ngay từ đầu: một link bị rate limit
không phải link chết, và gộp hai thứ đó lại là dạy người dùng bỏ qua kết quả.
Gặp 429 thì nó chờ theo đúng `Retry-After` của server rồi hỏi lại; hết lượt vẫn
429 thì báo "không kết luận được" chứ không báo chết.

301/308 bị tính là phải sửa dù link vẫn mở được: nó mở được hôm nay nhờ redirect,
và sẽ hỏng vào ngày người ta gỡ redirect đi.

### Cache

Kiểm lại toàn bộ nguồn ở mỗi lần chạy gate là thứ không dùng được khi kho lớn
dần: công cụ đợi 1 giây giữa hai request tới cùng một host để không tự chuốc
429, nên vài chục bài là vài phút. Kết quả "sống" vì thế được ghi lại ở
`content/.link-cache.json` (ngoài git — nó là quan sát về thế giới bên ngoài
tại một thời điểm, không tái tạo được từ mã nguồn).

Một URL chỉ được bỏ qua khi **cả hai** điều kiện cùng đúng:

- lần kiểm gần nhất chưa quá `--max-age` ngày (mặc định 14) — link chết mà không
  ai đụng vào bài thì vẫn phải bị phát hiện;
- lần kiểm đó diễn ra **sau** `last_verified` của mọi bài trích dẫn nó — đẩy
  `last_verified` lên nghĩa là tác giả vừa rà lại bài, nguồn của nó phải được
  hỏi lại chứ không lấy kết quả cũ.

Thất bại thì **không bao giờ được cache**: 404, 301 và 429 đều bị xoá khỏi cache
để lần sau hỏi lại. Cache một thất bại là để nó tự khỏi sau vài ngày mà không ai
hỏi lại — đúng thứ công cụ này sinh ra để chặn. `--no-cache` hỏi lại tất cả.

### Trong gate

`npm run gate` gọi công cụ này với `--allow-unknown`, tức **link chết chặn merge,
còn "không kiểm được" thì không**. Nếu không tách hai thứ đó ra thì gate sẽ đỏ ở
mọi máy đang mất mạng và trong mọi container không có egress — đỏ vì lý do chẳng
liên quan gì tới nội dung, và đó là kiểu đỏ mà người ta học cách bỏ qua.

Cờ đó không im lặng: nó vẫn in đủ danh sách URL chưa kiểm được kèm một dòng cảnh
báo. Chạy `npm run links` ở máy có mạng để có kết luận thật.

## Phiên bản hệ điều hành mà series nhắm tới

`content/platforms.json` giữ ma trận đó, và nó là bản duy nhất — cổng nội dung
đọc danh sách tên hệ từ đây thay vì chép lại vào code.

| Hệ | Phiên bản mục tiêu |
|---|---|
| Ubuntu / Xubuntu | 26.04 LTS |
| Debian | 13 (Trixie) |
| Fedora | 44 |
| FreeBSD | 15.0-RELEASE |

**Nâng phiên bản ở file này không làm bài nào tự nhiên được kiểm lại.** Ma trận
nói series *nhắm tới* đâu; `tested_on` của từng bài nói bài đó *đã chạy thật* ở
đâu. Hai thứ khác nhau, và chỉ một trong hai đổi được bằng cách gõ phím.

Nên khi bạn bump ma trận, việc còn lại là chạy lại từng bài trên phiên bản mới,
rồi mới sửa `tested_on` và `last_verified` của bài đó. Bài nào chưa chạy lại thì
cứ để nguyên bằng chứng cũ — nó vẫn đúng, chỉ là cũ.

Cổng nội dung kiểm một điều duy nhất về trường này: `tested_on` phải nhắc tới ít
nhất một hệ có trong ma trận. Đủ để bắt lỗi gõ sai (`Ubunut 26.04`) và bắt trường
bị điền cho có, mà không ép mọi bài phải chạy trên cả năm hệ.

## Viết một bài

```bash
npm run new-post -- post-002-ten-bai --axis "Networking"
npm run gate:draft        # kiểm; khung vừa sinh ra đã qua sẵn
npm run dev:draft         # xem thử trang thật
```

Dấu `--` là bắt buộc và không bỏ được: thiếu nó thì npm hiểu `--axis` là cờ của
chính npm, nuốt luôn tên cờ và chỉ đẩy giá trị trần xuống script — lỗi hiện ra ở
tận argparse dưới dạng `unrecognized arguments`, không nhắc gì tới npm.

`new-post` dựng `content/drafts/<slug>/{meta.json,body.html}` với đủ heading bắt
buộc và số hiệu kế tiếp. Khung đó **qua được cổng ngay** — chủ đích là để lần
chạy cổng đầu tiên xanh, mọi lần đỏ sau đó đều là một thứ bạn vừa làm, chứ không
phải mười lỗi có sẵn phải lội qua. Mọi chỗ cần bạn viết đều mang chữ `TODO`.

Cờ hữu ích, tất cả đặt sau dấu `--`: `--changes-system` (thêm sẵn mục Gỡ /
Hoàn tác mà cổng sẽ đòi), `--scope linux-only` (xem dưới), `--date 2026-09-01`
(bài tự lên đúng ngày đó, xem mục Lên lịch).

### Hợp đồng của một bài

`meta.json` — ngoài các trường hiển thị còn có phần chứng minh bài đã được chạy
thật: `tested_on`, `last_verified`, `changes_system`, và `sources` (≥ 2 nguồn
`official`/`upstream`, không nhận blog). `title` ≤ 52 ký tự, `description` ≤ 160
và phải khác `lede`.

`body.html` là **thân bài**, không phải trang: cấm `<h1>`, `<footer>`,
`class="lede"`, `global-nav`, `related-nav`, `ld-meta` — khung do renderer sinh.
Bắt buộc có sáu `<h2>`: mục tiêu · yêu cầu tiên quyết · các bước thực hiện ·
kiểm chứng · lưu ý &amp; khắc phục lỗi · bài tập.

Bốn chỗ hay vướng, tất cả đều có lý do:

- **Dấu `#` đầu dòng trong code block** bị bắt là shell prompt. Chú thích shell
  phải ra ngoài `<pre>`.
- **Mọi `<pre>` phải chứa `class="language-*"`**, kể cả khối output —
  dùng `language-text`.
- **Mỗi khối `language-bash` cần `data-run-as`** trong 400 ký tự ngay trước nó.
  Chèn một đoạn văn dài giữa nhãn và khối là đứt.
- **`changes_system: true` kéo theo một mục Gỡ / Hoàn tác.**

### Bài không có đối ứng FreeBSD

Mặc định mỗi bài phải có ít nhất một `<pre class="bsd">` và nhắc đủ năm tên
Ubuntu, Xubuntu, Debian, Fedora, FreeBSD. Nhưng phần lớn chủ đề nâng cao —
systemd unit, cgroup v2, eBPF, SELinux, netplan — không có đối ứng FreeBSD, và
khi đó tác giả chỉ còn hai lối tệ: nhét một khối gượng ép cho qua cổng, hoặc bỏ
luôn chủ đề.

Lối thứ ba là khai báo thẳng:

```json
"scope": "linux-only"
```

Cổng bỏ hai quy tắc FreeBSD, giữ nguyên mọi quy tắc còn lại — vẫn phải đủ
Ubuntu, Xubuntu, Debian, Fedora. Khai báo này đúng theo cả hai chiều: bài
`linux-only` mà vẫn có khối `bsd` hoặc nhãn `code-label bsd` thì đỏ, vì khi đó
một trong hai thứ sai mà không ai biết là thứ nào.

Vắng trường `scope` nghĩa là `cross-platform`, tức luật chặt nhất — bỏ sót không
bao giờ trở thành cách lách.

Và nó hiện lên trang bài, không nằm im trong JSON: người đọc FreeBSD thấy ngay
dòng "Bài này chỉ áp dụng cho Linux" thay vì đọc hết rồi mới phát hiện.

## Backlog và lịch soạn nháp

`content/backlog.md` giữ danh sách chủ đề theo thứ tự. Một lịch tự động chạy hai
lần mỗi tuần lấy mục đầu tiên chưa có bài, dựng bản nháp bằng `new-post`, viết
nội dung, chạy `npm run gate:draft`, rồi mở PR.

Nó dừng ở đó, và không thể đi xa hơn: `review_status: "reviewed"` là chữ ký nói
rằng từng lệnh đã chạy thật trên các hệ ghi ở `tested_on`, mà môi trường tự động
chỉ có Ubuntu và không có egress để đối chiếu tài liệu. Chữ ký đó là của bạn.

Nên PR do lịch tạo ra luôn ở dạng nháp, kèm phần liệt kê lệnh nào đã chạy thật ở
đâu và lệnh nào mới chỉ viết theo tài liệu. Việc của bạn là chạy thử, bổ sung
`tested_on`, đổi `review_status`, chuyển sang `content/posts/` rồi merge.

Backlog chỉ được đọc, không được máy sửa: bài đã viết hay chưa thì suy ra từ
`content/posts/`, `content/drafts/` và các PR đang mở. Để máy tự đánh dấu thì hai
PR mở cùng lúc sẽ sửa cùng một dòng và xung đột.

## Lên lịch: bài tự xuất bản

`meta.date` là ngày bài lên, tính theo **00:00 giờ Việt Nam**. Bài có ngày ở
tương lai thì chưa xuất bản: nó không có trên trang chủ, không trong feed, không
trong sitemap, và URL của nó trả 404 — mở được bằng đường dẫn trực tiếp là xuất
bản sớm bằng cửa sau. Related-nav cũng không trỏ tới nó: link "bài sau" dẫn vào
404 còn tệ hơn không có link nào.

Viết trước mười bài, merge một lần, mỗi bài tự hiện đúng ngày của nó.

Không có cron, không có job nào chạy theo lịch, và không cần deploy lại. Mọi
trang được render tại request, nên việc lọc bài chưa tới ngày xảy ra ở từng
request — bài của tuần sau đã nằm sẵn trong bundle từ lần deploy hiện tại.

Muốn xem thử một bài đã lên lịch thì để nó ở `content/drafts/` và dùng
`npm run dev:draft`; chuyển sang `content/posts/` là lúc chốt ngày lên.

## Deploy

```bash
npm run build     # dựng manifest + wrangler dry-run, không cần tài khoản
npm run deploy    # dựng manifest + wrangler deploy
```

`npm run gate` gọi sẵn `npm run build`, nên bundle hỏng thì đỏ ở PR chứ không
đỏ sau khi merge.

`.github/workflows/xuat-ban.yml` chạy cổng nội dung trên mọi PR, và deploy khi
merge vào `main`. Cần hai secret trong repo:

| secret | lấy ở đâu |
|---|---|
| `CLOUDFLARE_API_TOKEN` | Cloudflare → My Profile → API Tokens → template "Edit Cloudflare Workers" |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare → Workers & Pages → Account ID |

Workflow cache `content/.link-cache.json` theo `hashFiles` của các `meta.json`,
nên thêm một bài chỉ kiểm link của bài đó.

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
