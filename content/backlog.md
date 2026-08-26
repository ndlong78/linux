# Backlog chủ đề

Danh sách này là đầu vào của lịch soạn bài tự động. Nó **chỉ được đọc**, không
được sửa bởi máy: một bài đã viết hay chưa thì suy ra từ `content/posts/`,
`content/drafts/` và các PR đang mở — chứ không từ một cột trạng thái ở đây. Nếu
để máy tự đánh dấu, hai PR mở cùng lúc sẽ sửa cùng một dòng và xung đột.

Bạn sửa file này bất cứ lúc nào: đổi thứ tự, xoá dòng, chèn chủ đề mới. Lần fire
kế tiếp đọc bản mới nhất trên `main`.

## Cột

- **scope** — `cross-platform` (mặc định, phải có khối FreeBSD) hoặc `linux-only`
  cho chủ đề không có đối ứng trên FreeBSD.
- **sửa hệ thống** — `có` thì bài bắt buộc có mục *Gỡ / Hoàn tác*, và
  `new-post` cần cờ `--changes-system`.

| # | slug | Tiêu đề dự kiến | axis | scope | sửa hệ thống |
|---|---|---|---|---|---|
| 2 | post-002-duong-dan-va-di-chuyen | Đường dẫn tuyệt đối, tương đối và cách đi lại | Nền tảng | cross-platform | không |
| 3 | post-003-doc-file-khong-can-editor | Đọc file mà không cần mở trình soạn thảo | Nền tảng | cross-platform | không |
| 4 | post-004-quyen-va-chmod | Quyền tập tin: đọc cho đúng bốn chữ số | Tập tin & quyền | cross-platform | có |
| 5 | post-005-nguoi-dung-nhom-sudo | Người dùng, nhóm và sudo | Tập tin & quyền | cross-platform | có |
| 6 | post-006-tim-file-bang-find | Tìm file bằng find, và vì sao không dùng ls | Tập tin & quyền | cross-platform | không |
| 7 | post-007-hardlink-symlink-inode | Liên kết cứng, liên kết mềm và inode | Tập tin & quyền | cross-platform | không |
| 8 | post-008-xem-tien-trinh | Xem tiến trình: ps, top và cây tiến trình | Tiến trình & dịch vụ | cross-platform | không |
| 9 | post-009-tin-hieu-va-dung-tien-trinh | Tín hiệu, và cách dừng một tiến trình tử tế | Tiến trình & dịch vụ | cross-platform | không |
| 10 | post-010-systemd-unit-co-ban | systemd unit: bật, tắt và đọc trạng thái | Tiến trình & dịch vụ | linux-only | có |
| 11 | post-011-journalctl | journalctl: đọc log mà không lạc trong đó | Quan sát & sự cố | linux-only | không |
| 12 | post-012-viet-systemd-service | Viết một systemd service của riêng bạn | Tiến trình & dịch vụ | linux-only | có |
| 13 | post-013-systemd-timer | systemd timer, và khi nào vẫn nên dùng cron | Tiến trình & dịch vụ | linux-only | có |
| 14 | post-014-cai-go-ghim-goi | Cài, gỡ và ghim phiên bản một gói | Gói & phần mềm | cross-platform | có |
| 15 | post-015-kho-goi-va-khoa-gpg | Kho gói và khoá GPG: tin ai, vì sao | Gói & phần mềm | cross-platform | có |
| 16 | post-016-ip-route-dns | Địa chỉ IP, route mặc định và DNS đang dùng | Networking | cross-platform | không |
| 17 | post-017-ssh-khoa-va-config | SSH: khoá, agent và file config | Networking | cross-platform | có |
| 18 | post-018-mo-dong-cong | Mở và đóng cổng: ufw, firewalld, pf | Bảo mật | cross-platform | có |
| 19 | post-019-ss-va-tcpdump | Nhìn lưu lượng thật bằng ss và tcpdump | Networking | cross-platform | không |
| 20 | post-020-o-dia-phan-vung-mount | Ổ đĩa, phân vùng và mount | Lưu trữ | cross-platform | có |
| 21 | post-021-fstab | fstab: mount tự động, và cách không hỏng boot | Lưu trữ | cross-platform | có |
| 22 | post-022-tim-thu-an-dung-luong | Tìm thứ đang ăn hết dung lượng đĩa | Lưu trữ | cross-platform | không |
| 23 | post-023-lvm-mo-rong | LVM: mở rộng ổ khi máy vẫn đang chạy | Lưu trữ | linux-only | có |
| 24 | post-024-rsync-va-kiem-chung | Sao lưu bằng rsync, và kiểm chứng bản sao | Shell & tự động hoá | cross-platform | không |
| 25 | post-025-bien-moi-truong-va-path | Biến môi trường, PATH và file khởi động shell | Shell & tự động hoá | cross-platform | không |
| 26 | post-026-ong-chuyen-huong-ma-thoat | Ống, chuyển hướng và mã thoát | Shell & tự động hoá | cross-platform | không |
| 27 | post-027-script-bash-chiu-loi | Viết script bash chịu được lỗi | Shell & tự động hoá | cross-platform | không |
| 28 | post-028-thoi-gian-va-mui-gio | Đồng bộ thời gian và múi giờ | Nền tảng | cross-platform | có |
| 29 | post-029-cgroup-v2 | Giới hạn tài nguyên bằng cgroup v2 | Tiến trình & dịch vụ | linux-only | có |
| 30 | post-030-selinux-apparmor | SELinux và AppArmor: khi nào chúng chặn bạn | Bảo mật | linux-only | có |
| 31 | post-031-may-khong-boot | Khi máy không boot: dmesg và chế độ cứu hộ | Quan sát & sự cố | cross-platform | có |

## Sau khi hết danh sách

Lịch tự dừng và báo lại chứ không bịa thêm chủ đề. Thêm dòng mới vào bảng là nó
chạy tiếp.
