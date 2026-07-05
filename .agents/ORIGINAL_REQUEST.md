# Original User Request

## 2026-06-29T00:26:21Z

Sử dụng trình duyệt web (browser subagent) để đối chiếu, kiểm tra chéo và đảm bảo rằng toàn bộ các tính năng hiện có trên trang web OmiLearn đều đã được tích hợp đầy đủ, hoạt động hoàn hảo trên ứng dụng Local (Workflow). Kiểm tra toàn diện từ UI/UX, Navigation, Settings cho đến các tính năng học tập AI cốt lõi.

Working directory: /Users/nguyenhoangkhoi/Documents/antigravity/hopeful-galileo
Integrity mode: benchmark

## Requirements

### R1. Khảo sát và Đối chiếu toàn diện (Cross-check)
Nhóm Agent phải truy cập trang OmiLearn và ứng dụng Workflow local (http://localhost:5173). Khảo sát từng màn hình, nút bấm, navigation, settings, và flow của các tính năng AI. Lập danh sách các điểm chưa đồng nhất (UI/UX, tính năng thiếu, text không khớp). Cần đặc biệt chú ý đến quy định không được để "OmiLearn" xuất hiện trong UI của "Workflow".

### R2. Đảm bảo Parity tính năng và Giao diện
Dựa trên danh sách đối chiếu ở R1, nhóm Agent phải tự động thiết kế lại UI/UX và viết code để ứng dụng Workflow local sở hữu mọi tính năng như OmiLearn. Mọi tính năng AI (Quiz, Flashcard, Roadmap, Smart Note, Sơ đồ tư duy) phải hoạt động mượt mà.

### R3. Ràng buộc Browser Automation (macOS Workaround)
Để tự động hóa trình duyệt trên macOS, bạn bắt buộc phải dùng tính năng remote debugging của Chrome tại địa chỉ `127.0.0.1:9222`. Bạn phải cung cấp thông tin này cho `browser` subagent.

## Verification Resources
- Project có sẵn bộ test E2E tại thư mục `tests/e2e/`. Các agent có thể chạy `backend/venv/bin/python run_e2e_tests.py` to verify backend API hoạt động bình thường.

## Acceptance Criteria

### Đối chiếu tính năng
- [ ] Báo cáo khảo sát liệt kê rõ ràng ít nhất 5 luồng tính năng (Flows) so sánh giữa OmiLearn và Workflow.

### UI/UX và Code Parity
- [ ] Mọi Modal tính năng trên Workflow (Quiz, Sơ đồ tư duy, v.v) đều hoạt động end-to-end (không bị lỗi API hoặc lỗi UI).
- [ ] Tên "OmiLearn" tuyệt đối không xuất hiện ở bất kỳ màn hình UI nào trong source code (chỉ dùng "Workflow").
- [ ] Các bài test E2E backend đều phải PASS (exit code 0).
