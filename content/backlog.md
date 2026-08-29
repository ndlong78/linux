# Backlog chủ đề

Danh sách này là đầu vào của lịch soạn nháp tự động. Nó **chỉ được đọc**, không
được sửa bởi máy: một bài đã viết hay chưa thì suy ra từ `content/posts/`,
`content/drafts/` và các nhánh `bai-*` trên remote — chứ không từ một cột trạng
thái ở đây. Nếu để máy tự đánh dấu, hai nhánh mở cùng lúc sẽ sửa cùng một dòng
và xung đột.

Thứ tự trong bảng là thứ tự viết. Đọc từ trên xuống là đi từ cấp 1 lên cấp 4.

## Cột

- **cấp / nhánh** — phải khớp một nhánh có thật trong `content/curriculum.json`.
  Cổng nội dung chặn bài khai sai cặp này.
- **scope** — `cross-platform` (mặc định, phải có khối FreeBSD) hoặc `linux-only`
  cho chủ đề không có đối ứng trên FreeBSD.
- **sửa hệ thống** — `có` thì bài bắt buộc có mục *Gỡ / Hoàn tác*, và
  `new-post` cần cờ `--changes-system`.

---

## Cấp 1 — Linux Operator

Làm được việc hằng ngày trên một máy.

| # | slug | Tiêu đề dự kiến | nhánh | scope | sửa hệ thống |
|---|---|---|---|---|---|
| 4 | post-004-doc-file-khong-can-editor | Đọc file mà không cần mở trình soạn thảo | Tập tin | cross-platform | không |
| 5 | post-005-quyen-va-chmod | Quyền tập tin: đọc cho đúng bốn chữ số | Tập tin | cross-platform | có |
| 6 | post-006-hardlink-symlink-inode | Liên kết cứng, liên kết mềm và inode | Tập tin | cross-platform | không |
| 7 | post-007-tim-file-bang-find | Tìm file bằng find, và vì sao không dùng ls | Tập tin | cross-platform | không |
| 8 | post-008-nguoi-dung-va-nhom | Người dùng, nhóm và tập tin passwd | Người dùng | cross-platform | có |
| 9 | post-009-sudo-va-quyen-nang | sudo: cấp quyền mà không phát chìa khoá chủ | Người dùng | cross-platform | có |
| 10 | post-010-cai-go-ghim-goi | Cài, gỡ và ghim phiên bản một gói | Gói phần mềm | cross-platform | có |
| 11 | post-011-kho-goi-va-khoa-gpg | Kho gói và khoá GPG: tin ai, vì sao | Gói phần mềm | cross-platform | có |
| 12 | post-012-ip-route-dns | Địa chỉ IP, route mặc định và DNS đang dùng | Mạng cơ bản | cross-platform | không |
| 13 | post-013-kiem-tra-ket-noi | Kiểm tra kết nối: ping, ss, và đọc cho đúng | Mạng cơ bản | cross-platform | không |
| 14 | post-014-ssh-khoa-va-config | SSH: khoá, agent và file config | Mạng cơ bản | cross-platform | có |
| 15 | post-015-bat-tat-dich-vu | Bật, tắt và đọc trạng thái một dịch vụ | Dịch vụ | cross-platform | có |
| 16 | post-016-doc-log-cua-dich-vu | Đọc log của một dịch vụ đang hỏng | Dịch vụ | cross-platform | không |

## Cấp 2 — Linux Administrator

Chịu trách nhiệm cho một hệ. Sáu nhánh, mỗi nhánh 4–5 bài — cấp này là phần nặng
nhất của lộ trình, và cũng là chỗ người học ở lại lâu nhất.

**Nhánh systemd viết cho systemd 257**, không phải 259.5. Debian 13 dừng ở 257
còn Ubuntu 26.04 và Fedora 44 đã ở 259.5; bài dùng cờ chỉ có từ 258 sẽ chạy đúng
trên hai hệ và chết trên hệ thứ ba. Chi tiết ở `platform-notes.md`.

| # | slug | Tiêu đề dự kiến | nhánh | scope | sửa hệ thống |
|---|---|---|---|---|---|
| 17 | post-017-o-dia-phan-vung-mount | Ổ đĩa, phân vùng và mount | Lưu trữ | cross-platform | có |
| 18 | post-018-fstab | fstab: mount tự động, và cách không hỏng boot | Lưu trữ | cross-platform | có |
| 19 | post-019-lvm-mo-rong | LVM: mở rộng ổ khi máy vẫn đang chạy | Lưu trữ | linux-only | có |
| 20 | post-020-zfs-co-ban | ZFS cơ bản: pool, dataset và snapshot | Lưu trữ | cross-platform | có |
| 21 | post-021-tim-thu-an-dung-luong | Tìm thứ đang ăn hết dung lượng đĩa | Lưu trữ | cross-platform | không |
| 22 | post-022-systemd-unit-co-ban | systemd unit: bật, tắt và đọc trạng thái | systemd | linux-only | có |
| 23 | post-023-viet-systemd-service | Viết một systemd service của riêng bạn | systemd | linux-only | có |
| 24 | post-024-systemd-timer | systemd timer, và khi nào vẫn nên dùng cron | systemd | linux-only | có |
| 25 | post-025-journalctl | journalctl: đọc log mà không lạc trong đó | systemd | linux-only | không |
| 26 | post-026-cau-hinh-mang-tinh | Cấu hình mạng tĩnh và cách không tự khoá mình | Mạng | cross-platform | có |
| 27 | post-027-dns-phia-client | DNS phía client: hỏi ai, và hỏi bằng cách nào | Mạng | cross-platform | có |
| 28 | post-028-dong-bo-thoi-gian | Đồng bộ thời gian và múi giờ | Mạng | cross-platform | có |
| 29 | post-029-ss-va-tcpdump | Nhìn lưu lượng thật bằng ss và tcpdump | Mạng | cross-platform | không |
| 30 | post-030-mo-dong-cong | Mở và đóng cổng: ufw, firewalld, pf | Bảo mật | cross-platform | có |
| 31 | post-031-selinux-apparmor | SELinux và AppArmor: khi nào chúng chặn bạn | Bảo mật | linux-only | có |
| 32 | post-032-cap-nhat-bao-mat-tu-dong | Cập nhật bảo mật tự động, và khi nào không nên | Bảo mật | cross-platform | có |
| 33 | post-033-tls-va-ca-noi-bo | Chứng chỉ TLS và CA nội bộ | Bảo mật | cross-platform | có |
| 34 | post-034-rsync-va-kiem-chung | Sao lưu bằng rsync, và kiểm chứng bản sao | Sao lưu | cross-platform | không |
| 35 | post-035-snapshot-va-khoi-phuc | Snapshot và một lần khôi phục thật | Sao lưu | cross-platform | có |
| 36 | post-036-sao-luu-co-ma-hoa | Sao lưu có mã hoá bằng restic | Sao lưu | cross-platform | không |
| 37 | post-037-sao-luu-dich-vu-dang-chay | Sao lưu dịch vụ đang chạy mà không hỏng dữ liệu | Sao lưu | cross-platform | không |
| 38 | post-038-bien-moi-truong-va-path | Biến môi trường, PATH và file khởi động shell | Scripting | cross-platform | không |
| 39 | post-039-ong-chuyen-huong-ma-thoat | Ống, chuyển hướng và mã thoát | Scripting | cross-platform | không |
| 40 | post-040-grep-sed-awk | Xử lý văn bản: grep, sed và awk | Scripting | cross-platform | không |
| 41 | post-041-script-bash-chiu-loi | Viết script bash chịu được lỗi | Scripting | cross-platform | không |

## Cấp 3 — Senior Linux SysAdmin

Giữ hệ chạy dưới áp lực.

| # | slug | Tiêu đề dự kiến | nhánh | scope | sửa hệ thống |
|---|---|---|---|---|---|
| 42 | post-042-doc-tai-cpu-va-load | Đọc tải CPU và load average cho đúng | Hiệu năng | cross-platform | không |
| 43 | post-043-bo-nho-that-su-con-bao-nhieu | Bộ nhớ thật sự còn bao nhiêu | Hiệu năng | cross-platform | không |
| 44 | post-044-do-io-cua-dia | Đo I/O của đĩa và tìm tiến trình gây nghẽn | Hiệu năng | linux-only | không |
| 45 | post-045-may-khong-boot | Khi máy không boot: dmesg và chế độ cứu hộ | Chẩn đoán sự cố | cross-platform | có |
| 46 | post-046-lan-theo-mot-tien-trinh | Lần theo một tiến trình: strace, lsof, /proc | Chẩn đoán sự cố | linux-only | không |
| 47 | post-047-cron-va-systemd-timer-that-bai | Khi job định kỳ im lặng không chạy | Tự động hoá | linux-only | có |
| 48 | post-048-ansible-ad-hoc | Ansible ad-hoc: chạy một lệnh trên nhiều máy | Tự động hoá | linux-only | có |
| 49 | post-049-keepalived-vip | VIP và failover với keepalived | Sẵn sàng cao | linux-only | có |
| 50 | post-050-node-exporter-va-prometheus | Thu số liệu máy bằng node_exporter | Giám sát | linux-only | có |
| 51 | post-051-canh-bao-dung-nguong | Đặt ngưỡng cảnh báo không làm phiền người trực | Giám sát | linux-only | có |
| 52 | post-052-gia-co-ssh | Gia cố SSH: khoá, cổng, fail2ban | Gia cố | cross-platform | có |
| 53 | post-053-toi-thieu-hoa-be-mat | Tối thiểu hoá bề mặt: gói, cổng, dịch vụ | Gia cố | cross-platform | có |
| 54 | post-054-quan-nhieu-may-bang-ssh | Quản nhiều máy bằng SSH và inventory | Quản lý đội máy | linux-only | không |
| 55 | post-055-vet-cau-hinh-lech | Phát hiện máy lệch khỏi cấu hình chuẩn | Quản lý đội máy | linux-only | không |

## Cấp 4 — Linux Platform / Infrastructure Engineer

Thiết kế nền tảng cho hàng nghìn máy.

| # | slug | Tiêu đề dự kiến | nhánh | scope | sửa hệ thống |
|---|---|---|---|---|---|
| 56 | post-056-tang-hoa-mot-nen-tang | Phân tầng một nền tảng Linux nội bộ | Kiến trúc | linux-only | không |
| 57 | post-057-salt-hay-ansible | Chọn giữa Salt và Ansible cho đội máy của bạn | Quản lý cấu hình | linux-only | không |
| 58 | post-058-viet-state-idempotent | Viết state idempotent, và cách chứng minh nó | Quản lý cấu hình | linux-only | có |
| 59 | post-059-terraform-cho-may-ao | Terraform cho máy ảo nội bộ | Hạ tầng dạng mã | linux-only | có |
| 60 | post-060-log-tap-trung | Gom log tập trung mà không làm ngập đĩa | Observability | linux-only | có |
| 61 | post-061-trace-xuyen-dich-vu | Trace xuyên dịch vụ: khi log không đủ | Observability | linux-only | có |
| 62 | post-062-pxe-boot-tu-dau | PXE boot: từ DHCP tới hệ chạy được | PXE và xưởng ảnh | linux-only | có |
| 63 | post-063-golden-image | Dựng golden image và seal nó cho đúng | PXE và xưởng ảnh | linux-only | có |
| 64 | post-064-ci-cho-cau-hinh | CI cho cấu hình: kiểm trước khi chạm máy thật | CI/CD | linux-only | không |
| 65 | post-065-kubernetes-node-linux | Node Kubernetes nhìn từ phía Linux | Kubernetes | linux-only | có |
| 66 | post-066-cap-nhat-nghin-may | Cập nhật nghìn máy mà không mất một đêm | Quy mô nghìn máy | linux-only | có |
| 67 | post-067-do-luong-doi-may | Đo sức khoẻ đội máy: chỉ số nào đáng theo | Quy mô nghìn máy | linux-only | không |

---

## Sau khi hết danh sách

Lịch tự dừng và báo lại chứ không bịa thêm chủ đề. Thêm dòng mới vào bảng là nó
chạy tiếp.
