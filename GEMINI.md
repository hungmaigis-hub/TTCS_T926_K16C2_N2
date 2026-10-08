# QUY TẮC PHÁT TRIỂN DỰ ÁN TTCS (ICTU)

## 1. XỬ LÝ NGOẠI LỆ TOÀN DIỆN (EXCEPTION HANDLING & EDGE CASES)
Từ nay về sau, mọi chức năng, endpoint API và giao diện được xây dựng hoặc chỉnh sửa BẮT BUỘC phải bắt trọn vẹn các trường hợp ngoại lệ sau:

### A. Ngoại lệ dữ liệu đầu vào (Input & Data Validation)
1. **Kiểm tra trường bắt buộc**: Báo lỗi rõ ràng nếu để trống bất kỳ trường dữ liệu nào có dấu `*` hoặc thuộc tính `required`.
2. **Kiểm tra tính hợp lệ của thời gian**:
   - `ngay_ket_thuc` phải luôn lớn hơn `ngay_bat_dau`.
   - `han_hoan_thanh` của nhiệm vụ không được nằm trong quá khứ so với thời điểm giao việc.
   - `gio_ket_thuc` ca làm việc phải lớn hơn `gio_bat_dau`.
3. **Kiểm tra kiểu dữ liệu và giới hạn**:
   - Số lượng chỉ tiêu sinh viên, mức lương/phụ cấp, điểm số phải là số dương hợp lệ.
   - Tiến độ phần trăm nhiệm vụ phải nằm trong đoạn `[0, 100]`.
   - Email phải đúng cú pháp chuẩn, số điện thoại đúng định dạng Việt Nam.
4. **Kiểm tra định dạng và kích thước tệp tải lên**:
   - Chỉ cho phép các định dạng an toàn được chỉ định (PDF, DOCX, PNG, JPG).
   - Chặn các tệp thực thi độc hại (.exe, .bat, .sh, .js, .zip).
   - Giới hạn kích thước tệp (ví dụ tối đa 10MB) và thông báo nếu vượt ngưỡng.

### B. Ngoại lệ luồng nghiệp vụ & trạng thái (Business Flow & State Edge Cases)
1. **Chống trùng lặp (Double Submission / Duplicate Action)**:
   - Khi người dùng bấm nút gửi dữ liệu (Lưu, Duyệt, Ký, Check-in...), nút phải lập tức hiển thị trạng thái đang xử lý (loading) và bị `disabled` tạm thời để tránh click đúp sinh dữ liệu trùng.
   - Chặn ký hợp đồng nhiều lần nếu hợp đồng đã ở trạng thái "Đã ký".
   - Chặn check-in nhiều lần trong cùng một phiên ca làm việc.
2. **Xác thực quyền hạn và trình tự trạng thái**:
   - Sinh viên chưa được HR duyệt hồ sơ thì không được phép ký hợp đồng hoặc chấm công.
   - Không cho phép cập nhật, duyệt hoặc xóa bản ghi không tồn tại trong hệ thống (HTTP 404).
   - Kiểm tra trùng lặp email/tài khoản trước khi tạo người dùng mới (HTTP 409 hoặc 400).
3. **Chống chiếm chỗ trùng lặp & Giới hạn chỉ tiêu (Slot Occupied / Quota & Concurrency)**:
   - **Quy tắc khóa vị trí/suất thực tập**: Khi một suất thực tập hoặc ca làm việc đã có sinh viên đăng ký hoặc được duyệt thành công, hệ thống phải khóa vị trí đó lại ngay lập tức, sinh viên khác không được phép đăng ký đè (hiển thị trạng thái "Đã kín" hoặc "Hết chỗ").
   - **Giới hạn chỉ tiêu tiếp nhận (Quota Overflow)**: Một chương trình thực tập có chỉ tiêu 50 sinh viên, khi HR duyệt đủ 50/50 thì hệ thống tự động khóa nút duyệt tiếp, báo lỗi: *"Chương trình thực tập đã đủ chỉ tiêu sinh viên (50/50), không thể tiếp nhận thêm"*.
   - **Khóa gán Mentor**: Một sinh viên đã có Mentor hướng dẫn thì không cho phép phân công trùng đè Mentor khác; hoặc một Mentor đã phụ trách đủ chỉ tiêu tối đa (ví dụ 5 sinh viên) thì trong danh sách chọn Mentor phải hiển thị trạng thái "Đã đủ chỉ tiêu hướng dẫn".

### C. Ngoại lệ kết nối mạng & máy chủ (Network & API Exceptions)
1. **Frontend luôn bọc các lời gọi `fetch` trong khối `try...catch`**:
   - Nếu máy chủ sập hoặc mất mạng (`Failed to fetch`): Hiển thị thông báo thân thiện (Alert/Toast/Notification) giải thích rõ ràng cho người dùng, tuyệt đối không để ứng dụng bị treo hoặc màn hình trắng.
2. **Bóc tách lỗi API chuẩn xác**:
   - Khi API trả về mã lỗi (`!response.ok`), Frontend phải đọc dữ liệu lỗi từ response (`data.detail` hoặc `data.message`), hỗ trợ cả trường hợp `detail` là chuỗi hoặc mảng lỗi Pydantic, để hiển thị thông báo lỗi cụ thể cho người dùng.
3. **Backend trả về mã HTTP Status Code và thông điệp chuẩn RESTful**:
   - `400 Bad Request`: Sai logic nghiệp vụ.
   - `404 Not Found`: Không tìm thấy bản ghi.
   - `422 Unprocessable Entity`: Sai kiểu dữ liệu / validation schema.
   - `409 Conflict`: Dữ liệu bị trùng lặp.
   - `500 Internal Server Error`: Lỗi máy chủ không mong muốn kèm ghi log an toàn.

---

## 2. QUY TẮC BẤT DI BẤT DỊCH
1. **TUYỆT ĐỐI KHÔNG ĐƯỢC CÓ COMMENT TRONG CODE FRONTEND**:
   - Mọi file `.html`, `.js`, `.css` không được chứa bất kỳ chú thích nào (`//`, `/* */`, `<!-- -->`).
2. **KHÔNG TỰ TIỆN COMMIT HAY PUSH GIT**:
   - Chỉ chạy lệnh `git commit` hoặc `git push` khi người dùng yêu cầu rõ ràng.
