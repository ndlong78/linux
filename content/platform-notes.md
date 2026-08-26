# Điều cần biết khi viết bài cho phiên bản mục tiêu

Ghi chú rút từ tài liệu chính chủ, kèm nguồn và kèm việc nó ảnh hưởng tới bài
nào trong `backlog.md`. Đây không phải bản dịch release notes — chỉ giữ những
thay đổi làm **sai** một bài viết theo phiên bản cũ.

Trạng thái xác nhận nằm ở `platforms.json`, trường `verified`.

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

→ **Ảnh hưởng #003** (đọc file không cần editor) và mọi bài dán output của lệnh
coreutils. Cờ hiếm và định dạng output có thể khác GNU; bài nào dựa vào một cờ
lạ thì phải nói rõ đang chạy bản nào.

### APT 3.1 (từ 2.7 ở 24.04)

Có giao diện lịch sử mới:

    apt history-list
    apt history-info 0
    sudo apt history-undo 0
    sudo apt history-redo 0
    sudo apt history-rollback 1

APT cũng chuyển từ GnuTLS/gcrypt sang OpenSSL cho TLS và băm file.

→ **Ảnh hưởng #014** (cài, gỡ, ghim gói) và **#015** (kho gói, khoá GPG). Bài
#014 nên dạy `history-undo` — đó chính là mục "Gỡ / Hoàn tác" mà cổng nội dung
đòi, và giờ nó có lệnh chính chủ.

### Linux kernel 7.0 (từ 6.8)

Bản GA generic dùng kernel 7.0. Real-time kernel giờ nằm trong kho chính, dùng
được miễn phí không cần Ubuntu Pro. Livepatch hỗ trợ thêm ARM64.

→ **Ảnh hưởng #001**: ví dụ chuỗi kernel `6.8.0-51-generic` là dạng của 24.04;
trên 26.04 nó thuộc dòng `7.0`.

### systemd 259.5

→ **Ảnh hưởng #010–#013** (unit, journalctl, viết service, timer) và **#029**
(cgroup v2). Kiểm lại cờ và tên thuộc tính trước khi viết.

### OpenSSH 10.2 (từ 9.6)

Gói GSS-API tách riêng thành `openssh-client-gssapi` và `openssh-server-gssapi`.
Các thuật toán `gss-group14-sha1-` và `gss-gex-sha1-` đã bị bỏ theo RFC 8732.

→ **Ảnh hưởng #017** (SSH: khoá, agent, config).

### Netplan 1.2 (từ 1.0)

Có thiết lập riêng cho `systemd-networkd-wait-online`; cờ parser để bỏ qua cấu
hình hỏng thay vì chết cả file.

→ **Ảnh hưởng #016** (IP, route, DNS) và **#018** (mở/đóng cổng).

### AppArmor

Thêm nhiều profile mới cho ứng dụng, và có chế độ enforce.

→ **Ảnh hưởng #030** (SELinux và AppArmor).

### Khác

Python 3.14 (từ 3.12), GCC 15.2, LLVM 21, Rust 1.93.1. OpenSSL có QUIC cả client
lẫn server.

---

## Debian 13, Fedora 44, FreeBSD 15 — CHƯA đọc được

`docs.freebsd.org` và `docs.fedoraproject.org` bị chặn ở môi trường soạn bài, nên
ba dòng này trong `platforms.json` có `verified: null`. Số phiên bản là do người
chủ repo đưa, chưa ai đối chiếu với tài liệu chính chủ.

Trước khi viết bài chạm tới ba hệ này, mở tài liệu ở máy có mạng và bổ sung mục
tương ứng vào file này:

- <https://www.debian.org/releases/trixie/>
- <https://docs.fedoraproject.org/en-US/fedora-server/>
- <https://docs.freebsd.org/en/books/handbook/>

`npm run links` kiểm được ba URL đó còn sống — nhưng "còn sống" không phải "đã
đọc".
