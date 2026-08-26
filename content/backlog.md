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
| 2 | post-002-duong-dan-va-di-chuyen | Đường dẫn tuyệt đối, tương đối và cách đi lại | Tập tin | cross-platform | không |
| 3 | post-003-doc-file-khong-can-editor | Đọc file mà không cần mở trình soạn thảo | Tập tin | cross-platform | không |
| 4 | post-004-quyen-va-chmod | Quyền tập tin: đọc cho đúng bốn chữ số | Tập tin | cross-platform | có |
| 5 | post-005-hardlink-symlink-inode | Liên kết cứng, liên kết mềm và inode | Tập tin | cross-platform | không |
| 6 | post-006-tim-file-bang-find | Tìm file bằng find, và vì sao không dùng ls | Tập tin | cross-platform | không |
| 7 | post-007-nguoi-dung-va-nhom | Người dùng, nhóm và tập tin passwd | Người dùng | cross-platform | có |
| 8 | post-008-sudo-va-quyen-nang | sudo: cấp quyền mà không phát chìa khoá chủ | Người dùng | cross-platform | có |
| 9 | post-009-cai-go-ghim-goi | Cài, gỡ và ghim phiên bản một gói | Gói phần mềm | cross-platform | có |
| 10 | post-010-kho-goi-va-khoa-gpg | Kho gói và khoá GPG: tin ai, vì sao | Gói phần mềm | cross-platform | có |
| 11 | post-011-ip-route-dns | Địa chỉ IP, route mặc định và DNS đang dùng | Mạng cơ bản | cross-platform | không |
| 12 | post-012-kiem-tra-ket-noi | Kiểm tra kết nối: ping, ss, và đọc cho đúng | Mạng cơ bản | cross-platform | không |
| 13 | post-013-ssh-khoa-va-config | SSH: khoá, agent và file config | Mạng cơ bản | cross-platform | có |
| 14 | post-014-bat-tat-dich-vu | Bật, tắt và đọc trạng thái một dịch vụ | Dịch vụ | cross-platform | có |
| 15 | post-015-doc-log-cua-dich-vu | Đọc log của một dịch vụ đang hỏng | Dịch vụ | cross-platform | không |

## Cấp 2 — Linux Administrator

Chịu trách nhiệm cho một hệ.

| # | slug | Tiêu đề dự kiến | nhánh | scope | sửa hệ thống |
|---|---|---|---|---|---|
| 16 | post-016-o-dia-phan-vung-mount | Ổ đĩa, phân vùng và mount | Lưu trữ | cross-platform | có |
| 17 | post-017-fstab | fstab: mount tự động, và cách không hỏng boot | Lưu trữ | cross-platform | có |
| 18 | post-018-lvm-mo-rong | LVM: mở rộng ổ khi máy vẫn đang chạy | Lưu trữ | linux-only | có |
| 19 | post-019-tim-thu-an-dung-luong | Tìm thứ đang ăn hết dung lượng đĩa | Lưu trữ | cross-platform | không |
| 20 | post-020-systemd-unit-co-ban | systemd unit: bật, tắt và đọc trạng thái | systemd | linux-only | có |
| 21 | post-021-viet-systemd-service | Viết một systemd service của riêng bạn | systemd | linux-only | có |
| 22 | post-022-systemd-timer | systemd timer, và khi nào vẫn nên dùng cron | systemd | linux-only | có |
| 23 | post-023-journalctl | journalctl: đọc log mà không lạc trong đó | systemd | linux-only | không |
| 24 | post-024-netplan-va-cau-hinh-mang | Cấu hình mạng tĩnh và cách không tự khoá mình | Mạng | cross-platform | có |
| 25 | post-025-ss-va-tcpdump | Nhìn lưu lượng thật bằng ss và tcpdump | Mạng | cross-platform | không |
| 26 | post-026-mo-dong-cong | Mở và đóng cổng: ufw, firewalld, pf | Bảo mật | cross-platform | có |
| 27 | post-027-selinux-apparmor | SELinux và AppArmor: khi nào chúng chặn bạn | Bảo mật | linux-only | có |
| 28 | post-028-rsync-va-kiem-chung | Sao lưu bằng rsync, và kiểm chứng bản sao | Sao lưu | cross-platform | không |
| 29 | post-029-snapshot-va-khoi-phuc | Snapshot và một lần khôi phục thật | Sao lưu | cross-platform | có |
| 30 | post-030-bien-moi-truong-va-path | Biến môi trường, PATH và file khởi động shell | Scripting | cross-platform | không |
| 31 | post-031-ong-chuyen-huong-ma-thoat | Ống, chuyển hướng và mã thoát | Scripting | cross-platform | không |
| 32 | post-032-script-bash-chiu-loi | Viết script bash chịu được lỗi | Scripting | cross-platform | không |

## Cấp 3 — Senior Linux SysAdmin

Giữ hệ chạy dưới áp lực.

| # | slug | Tiêu đề dự kiến | nhánh | scope | sửa hệ thống |
|---|---|---|---|---|---|
| 33 | post-033-doc-tai-cpu-va-load | Đọc tải CPU và load average cho đúng | Hiệu năng | cross-platform | không |
| 34 | post-034-bo-nho-that-su-con-bao-nhieu | Bộ nhớ thật sự còn bao nhiêu | Hiệu năng | cross-platform | không |
| 35 | post-035-do-io-cua-dia | Đo I/O của đĩa và tìm tiến trình gây nghẽn | Hiệu năng | linux-only | không |
| 36 | post-036-may-khong-boot | Khi máy không boot: dmesg và chế độ cứu hộ | Chẩn đoán sự cố | cross-platform | có |
| 37 | post-037-lan-theo-mot-tien-trinh | Lần theo một tiến trình: strace, lsof, /proc | Chẩn đoán sự cố | linux-only | không |
| 38 | post-038-cron-va-systemd-timer-that-bai | Khi job định kỳ im lặng không chạy | Tự động hoá | linux-only | có |
| 39 | post-039-ansible-ad-hoc | Ansible ad-hoc: chạy một lệnh trên nhiều máy | Tự động hoá | linux-only | có |
| 40 | post-040-keepalived-vip | VIP và failover với keepalived | Sẵn sàng cao | linux-only | có |
| 41 | post-041-node-exporter-va-prometheus | Thu số liệu máy bằng node_exporter | Giám sát | linux-only | có |
| 42 | post-042-canh-bao-dung-nguong | Đặt ngưỡng cảnh báo không làm phiền người trực | Giám sát | linux-only | có |
| 43 | post-043-gia-co-ssh | Gia cố SSH: khoá, cổng, fail2ban | Gia cố | cross-platform | có |
| 44 | post-044-toi-thieu-hoa-be-mat | Tối thiểu hoá bề mặt: gói, cổng, dịch vụ | Gia cố | cross-platform | có |
| 45 | post-045-quan-nhieu-may-bang-ssh | Quản nhiều máy bằng SSH và inventory | Quản lý đội máy | linux-only | không |
| 46 | post-046-vet-cau-hinh-lech | Phát hiện máy lệch khỏi cấu hình chuẩn | Quản lý đội máy | linux-only | không |

## Cấp 4 — Linux Platform / Infrastructure Engineer

Thiết kế nền tảng cho hàng nghìn máy.

| # | slug | Tiêu đề dự kiến | nhánh | scope | sửa hệ thống |
|---|---|---|---|---|---|
| 47 | post-047-tang-hoa-mot-nen-tang | Phân tầng một nền tảng Linux nội bộ | Kiến trúc | linux-only | không |
| 48 | post-048-salt-hay-ansible | Chọn giữa Salt và Ansible cho đội máy của bạn | Quản lý cấu hình | linux-only | không |
| 49 | post-049-viet-state-idempotent | Viết state idempotent, và cách chứng minh nó | Quản lý cấu hình | linux-only | có |
| 50 | post-050-terraform-cho-may-ao | Terraform cho máy ảo nội bộ | Hạ tầng dạng mã | linux-only | có |
| 51 | post-051-log-tap-trung | Gom log tập trung mà không làm ngập đĩa | Observability | linux-only | có |
| 52 | post-052-trace-xuyen-dich-vu | Trace xuyên dịch vụ: khi log không đủ | Observability | linux-only | có |
| 53 | post-053-pxe-boot-tu-dau | PXE boot: từ DHCP tới hệ chạy được | PXE và xưởng ảnh | linux-only | có |
| 54 | post-054-golden-image | Dựng golden image và seal nó cho đúng | PXE và xưởng ảnh | linux-only | có |
| 55 | post-055-ci-cho-cau-hinh | CI cho cấu hình: kiểm trước khi chạm máy thật | CI/CD | linux-only | không |
| 56 | post-056-kubernetes-node-linux | Node Kubernetes nhìn từ phía Linux | Kubernetes | linux-only | có |
| 57 | post-057-cap-nhat-nghin-may | Cập nhật nghìn máy mà không mất một đêm | Quy mô nghìn máy | linux-only | có |
| 58 | post-058-do-luong-doi-may | Đo sức khoẻ đội máy: chỉ số nào đáng theo | Quy mô nghìn máy | linux-only | không |

---

## Sau khi hết danh sách

Lịch tự dừng và báo lại chứ không bịa thêm chủ đề. Thêm dòng mới vào bảng là nó
chạy tiếp.
