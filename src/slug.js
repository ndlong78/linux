// Slug tiếng Việt cho URL.
//
// `axis` được tác giả viết bằng tiếng Việt có dấu ("Tiến trình & dịch vụ") còn
// URL thì phải ASCII. Phép biến đổi này chạy ở hai chỗ — lúc sinh link và lúc
// router khớp đường dẫn — nên nó phải là một hàm dùng chung, không phải hai
// đoạn code giống nhau ở hai file.

/**
 * NFD tách dấu thành ký tự tổ hợp rồi bỏ chúng đi. `đ` không tổ hợp được nên
 * phải thay riêng — bỏ sót nó là "tự động hoá" thành "t-ng-ho" thay vì
 * "tu-dong-hoa", một lớp lỗi im lặng chỉ lộ ra khi có bài đầu tiên dùng chữ đó.
 */
export function slugify(value) {
  return String(value)
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/đ/g, "d")
    .replace(/Đ/g, "D")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}
