# Điều cần biết khi viết bài cho phiên bản mục tiêu

Ghi chú rút từ tài liệu chính chủ, kèm nguồn và kèm việc nó ảnh hưởng tới bài
nào trong `backlog.md`. Đây không phải bản dịch release notes — chỉ giữ những
thay đổi làm **sai** một bài viết theo phiên bản cũ.

Trạng thái xác nhận nằm ở `platforms.json`, trường `verified`.

> Bài được trỏ tới bằng **slug** hoặc bằng **tên nhánh**, không bằng số hiệu. Số
> hiệu trong `backlog.md` đổi mỗi lần danh sách được sắp lại; slug thì không.


---

## Ubuntu 26.04 LTS — đã đọc trực tiếp, 2026-08-26

Nguồn: <https://documentation.ubuntu.com/release-notes/26.04/> và hai trang con
*summary for LTS users* / *changes since previous interim*.

**Resolute Raccoon**, phát hành **23/04/2026**, hỗ trợ tới **04/2031** (10 năm
với Ubuntu Pro/ESM). Nâng cấp từ 22.04 phải đi qua 24.04 hoặc 25.10 trước.

### rust-coreutils là mặc định

`cat`, `ls`, `head`, `tail`, `cp`… trên bản cài mặc định giờ là **uutils**, không
phải GNU coreutils. Đổi qua lại:

    sudo apt install coreutils-from-gnu --allow-remove-essential
    sudo apt install coreutils-from-uutils --allow-remove-essential

→ **Ảnh hưởng `post-004-doc-file-khong-can-editor`, `post-040-grep-sed-awk`** và
mọi bài dán output của lệnh coreutils. Cờ hiếm và định dạng output có thể khác GNU; bài nào dựa vào một cờ
lạ thì phải nói rõ đang chạy bản nào.

### APT 3.1 (từ 2.7 ở 24.04)

Có giao diện lịch sử mới:

    apt history-list
    apt history-info 0
    sudo apt history-undo 0
    sudo apt history-redo 0
    sudo apt history-rollback 1

APT cũng chuyển từ GnuTLS/gcrypt sang OpenSSL cho TLS và băm file.

→ **Ảnh hưởng `post-010-cai-go-ghim-goi`** và **`post-011-kho-goi-va-khoa-gpg`**.
Bài cài/gỡ gói nên dạy `history-undo` — đó chính là mục "Gỡ / Hoàn tác" mà cổng
nội dung đòi, và giờ nó có lệnh chính chủ.

### Linux kernel 7.0 (từ 6.8)

Bản GA generic dùng kernel 7.0. Real-time kernel giờ nằm trong kho chính, dùng
được miễn phí không cần Ubuntu Pro. Livepatch hỗ trợ thêm ARM64.

→ **Ảnh hưởng `post-001-nhan-dien-he-dieu-hanh`**: ví dụ chuỗi kernel
`6.8.0-51-generic` là dạng của 24.04; trên 26.04 nó thuộc dòng `7.0`.

### systemd 259.5

→ **Ảnh hưởng cả nhánh systemd (cấp 2)**. Kiểm lại cờ và tên thuộc tính trước
khi viết — xem mục "Mốc systemd chung" ở dưới.

### OpenSSH 10.2 (từ 9.6)

Gói GSS-API tách riêng thành `openssh-client-gssapi` và `openssh-server-gssapi`.
Các thuật toán `gss-group14-sha1-` và `gss-gex-sha1-` đã bị bỏ theo RFC 8732.

→ **Ảnh hưởng `post-014-ssh-khoa-va-config`**.

### Netplan 1.2 (từ 1.0)

Có thiết lập riêng cho `systemd-networkd-wait-online`; cờ parser để bỏ qua cấu
hình hỏng thay vì chết cả file.

→ **Ảnh hưởng `post-026-cau-hinh-mang-tinh`** và **`post-030-mo-dong-cong`**.

### AppArmor

Thêm nhiều profile mới cho ứng dụng, và có chế độ enforce.

→ **Ảnh hưởng `post-031-selinux-apparmor`**.

### Khác

Python 3.14 (từ 3.12), GCC 15.2, LLVM 21, Rust 1.93.1. OpenSSL có QUIC cả client
lẫn server.

---

## Debian 13 (Trixie) — rút từ tìm kiếm web, 2026-08-26

Nguồn: <https://www.debian.org/News/2025/20250809>

Phát hành **09/08/2025**. Kernel **6.12 LTS**, **systemd 257**, GCC 14.2, Python 3.13,
GNOME 48. Bỏ trình cài đặt cho i386 và armel, bỏ hẳn mipsel; thêm riscv64 64-bit.

### systemd 257, không phải 259

Ubuntu 26.04 đi với systemd 259.5, Debian 13 đi với 257. Chênh hai vòng phát hành.

→ **Ảnh hưởng cả nhánh systemd (cấp 2)**. Bài dùng cờ hoặc thuộc tính chỉ có từ
258 trở lên sẽ đúng trên Ubuntu và sai trên Debian. Kiểm `systemctl --version`
trên cả hai trước khi dán lệnh.

### Kernel 6.12 LTS

→ **Ảnh hưởng `post-001-nhan-dien-he-dieu-hanh`**: ba hệ Linux mục tiêu giờ ở ba
dòng kernel khác nhau —
Ubuntu 26.04 dòng 7.0, Fedora 44 dòng 6.19, Debian 13 dòng 6.12. Đúng cái bài #001
muốn nói: `uname -r` không cho biết distro.

### Không còn trình cài đặt i386

→ **Ảnh hưởng `post-001-...`** phần kiến trúc: `uname -m` trả `i686` nghĩa là máy
đó không cài mới Debian 13 được.

---

## Fedora 44 — rút từ tìm kiếm web, 2026-08-26

Nguồn: <https://fedoramagazine.org/announcing-fedora-linux-44/>

Phát hành **28/04/2026**. Kernel **6.19** (kernel 7.0 không kịp vào bản chính
thức). GCC 16, LLVM 22, Ruby 4.0, Go 1.26, PHP 8.5.

### DNF5

PackageKit đã chuyển sang backend **DNF5** dựng trên libdnf5.

→ **Ảnh hưởng nhánh Gói phần mềm (cấp 1)**. Phần lớn lệnh `dnf` giữ
nguyên cú pháp, nhưng output và một số tuỳ chọn khác bản cũ. Bài nào dán output
của `dnf` phải chạy trên Fedora 44 thật, đừng chép từ bài viết thời dnf4.

---

## FreeBSD 15.1-RELEASE — rút từ tìm kiếm web, 2026-08-26

Nguồn: <https://www.freebsd.org/releases/15.1R/announce/> và
<https://www.freebsd.org/releases/15.0R/relnotes/>

Phát hành **16/06/2026**, EoL dự kiến **31/03/2027**.

### Đừng nhắm 15.0

**15.0-RELEASE hết hạn hỗ trợ 30/09/2026.** Ma trận từng ghi 15.0; đã sửa sang
15.1. Bài nào đã viết theo 15.0 thì con số trong ví dụ cần đổi.

### pkgbase — base system quản bằng pkg(8)

Từ 15.0, hệ nền có thể cài và cập nhật như một tập gói từ kho `FreeBSD-base`,
quản trọn bằng `pkg(8)`. Đây là mặc định cho mọi ảnh VM và ảnh cloud công khai.
15.0 gọi nó là technology preview và dự kiến thành cách chuẩn ở các bản sau.

→ **Ảnh hưởng `post-001-...`**: câu "sau `freebsd-update` mà chưa khởi động lại" chỉ đúng
với hệ cài theo lối cũ. Trên hệ pkgbase, đường cập nhật là `pkg upgrade`, và
`freebsd-version -kru` vẫn là chỗ đọc ba con số.
→ **Ảnh hưởng nhánh Gói phần mềm (cấp 1)**: FreeBSD giờ có hai thứ cùng dùng
`pkg` — gói ứng dụng và gói hệ nền. Bài phải nói rõ đang nói cái nào.

### Bỏ nền tảng 32-bit

i386, armv6 và powerpc 32-bit đã bị loại; chỉ còn armv7 là nền tảng 32-bit cuối
cùng. Ứng dụng 32-bit vẫn chạy được qua lớp tương thích trên bản 64-bit.

→ **Ảnh hưởng `post-001-...`** phần kiến trúc, cùng chỗ với ghi chú Debian ở trên.

### OpenZFS 2.4.0

→ **Ảnh hưởng cả nhánh Lưu trữ (cấp 2)**, đặc biệt `post-020-zfs-co-ban`, và
`post-035-snapshot-va-khoi-phuc`.

---

## Mốc systemd chung cho cả series

| Hệ | systemd |
|---|---|
| Ubuntu 26.04 LTS | 259.5 |
| Fedora 44 | 259.5 |
| Debian 13 | **257** |
| FreeBSD | không dùng systemd |

**Viết cho 257.** Hai trong ba hệ Linux mục tiêu đi với 259.5, nhưng Debian 13 —
bản stable, vòng đời dài nhất trong ba hệ — dừng ở 257. Bài dùng cờ hoặc thuộc
tính chỉ có từ 258 trở lên sẽ chạy đúng trên Ubuntu và Fedora rồi chết trên
Debian, và người đọc Debian sẽ nghĩ họ gõ sai.

Quy tắc cho nhánh systemd (cấp 2) và mọi bài khác chạm tới unit:

1. Mặc định chỉ dùng thứ có từ **257** trở xuống.
2. Cần thứ mới hơn thì nói thẳng trong bài: *"cần systemd ≥ 258, Debian 13 chưa
   có"*, và đưa cách làm thay thế.
3. Kiểm bằng `systemctl --version` trước khi dán lệnh, đừng tin trí nhớ.

Nguồn: <https://packages.fedoraproject.org/pkgs/systemd/systemd/> cho Fedora 44,
release notes của Debian 13 và Ubuntu 26.04 cho hai hệ còn lại.

---

## Cách các số liệu trên được xác nhận

Ubuntu là bản duy nhất tôi mở được trang tài liệu và đọc trực tiếp
(`verified_via: read`). Ba hệ còn lại rút từ kết quả tìm kiếm web
(`verified_via: search`) vì `docs.freebsd.org`, `docs.fedoraproject.org` và
`www.debian.org` đều bị egress proxy của môi trường soạn bài chặn ở mức host.

Khác biệt này có thật và đáng giữ: `npm run links` kiểm được URL còn sống, không
kiểm được nội dung. Trước khi viết bài chạm sâu vào một hệ, mở tài liệu gốc ở máy
có mạng và nâng dòng đó lên `read`.
