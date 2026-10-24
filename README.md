# Chủ đề 7 - Project 2: Nâng cao chất lượng ảnh số

6 kỹ thuật: Histogram Equalization, CLAHE, Gamma Correction, Gaussian Filter, Median Filter, Sharpen.
Cấu trúc code kế thừa Project 1 (module thuật toán + GUI + script đánh giá hàng loạt).

## File

| File | Vai trò | So với Project 1 |
|---|---|---|
| `enhancement_methods.py` | 6 hàm xử lý + bảng mô tả tham số `DANH_SACH_PHUONG_PHAP` | thay cho `edge_detectors.py` |
| `danh_gia.py` | Chỉ số đánh giá (độ sáng, tương phản, entropy, độ nét, PSNR) + vẽ histogram | mới (tách riêng để dùng chung GUI và batch) |
| `gui_app.py` | GUI Tkinter: mở ảnh/video, chọn kỹ thuật, chỉnh tham số, xem trước/sau + histogram, lưu | giữ nguyên khung, thanh trượt tự đổi theo kỹ thuật |
| `batch_evaluate.py` | Chạy hàng loạt trên thư mục ảnh test, xuất CSV + ảnh so sánh + thử khử nhiễu | giữ nguyên cách chạy, đổi chỉ số đánh giá |

## Cách chạy

```bash
pip install -r requirements.txt
python gui_app.py
python batch_evaluate.py --input ../test_images --output ./eval_results
```

Gợi ý tổ chức thư mục (dùng chung bộ ảnh test giữa 2 project):

```
xu_ly_anh/
├── test_images/          <- bộ ảnh test chung (>=10 ảnh)
├── project1_phat_hien_canh/
└── project2_nang_cao_chat_luong/
```

## Công thức 6 kỹ thuật (dùng cho báo cáo)

| Kỹ thuật | Công thức / ý tưởng | Tham số điều chỉnh |
|---|---|---|
| Histogram Equalization | s = T(r) = (L-1) · CDF(r), dàn đều histogram trên kênh sáng Y | cường độ (%) trộn với ảnh gốc |
| CLAHE | Chia ảnh thành lưới ô nhỏ, cân bằng histogram từng ô, cắt histogram ở mức clip limit rồi nội suy giữa các ô | clip limit, số ô lưới |
| Gamma Correction | s = 255 · (r / 255)^γ ; γ < 1 sáng lên, γ > 1 tối đi | γ |
| Gaussian Filter | Tích chập với kernel G(x,y) = exp(-(x²+y²) / 2σ²) (chuẩn hóa tổng = 1) | kích thước kernel, σ |
| Median Filter | Thay điểm ảnh bằng trung vị của vùng lân cận k×k | kích thước kernel |
| Sharpen (Unsharp Mask) | ảnh_nét = ảnh_gốc + a · (ảnh_gốc − ảnh_mờ) | cường độ a, σ của ảnh mờ |

HE và CLAHE chỉ xử lý kênh sáng (Y trong YCrCb) rồi ghép lại để ảnh màu không bị lệch màu.

## Các chỉ số đánh giá

| Chỉ số | Cách tính | Ý nghĩa |
|---|---|---|
| Độ sáng TB | trung bình mức xám | ảnh tối hay sáng |
| Độ tương phản | độ lệch chuẩn mức xám | càng lớn càng "rõ" |
| Entropy | −Σ p·log2(p) của histogram | lượng thông tin |
| Độ nét | phương sai của Laplacian | nhiều cạnh/chi tiết hay mờ |
| PSNR | 10·log10(255² / MSE) so với ảnh sạch | độ giống ảnh gốc, dùng khi thử khử nhiễu |

Lưu ý khi viết phân tích: "độ nét" tăng mạnh sau HE chưa chắc là tốt, vì HE khuếch đại cả nhiễu.
Hãy đối chiếu với ảnh so sánh bằng mắt trước khi kết luận.

## Phần thử khử nhiễu (so sánh Gaussian và Median)

`batch_evaluate.py` tự thêm nhiễu muối tiêu (3%) và nhiễu Gaussian (độ lệch 20) vào từng ảnh sạch,
lọc bằng Gaussian và Median rồi tính PSNR so với ảnh sạch. Kết quả thường gặp:
Median vượt trội ở nhiễu muối tiêu, còn với nhiễu Gaussian hai bộ lọc xấp xỉ nhau.
Hãy chạy trên bộ ảnh thật của nhóm và dùng số liệu của chính nhóm trong báo cáo.

## Gợi ý chuẩn bị bộ ảnh test

Ngoài bộ ảnh đã dùng cho Project 1, nên có thêm ảnh: chụp thiếu sáng, ảnh bị lóa/quá sáng,
ảnh tương phản thấp (sương mù, ảnh cũ), ảnh có nhiễu (chụp ISO cao). Có đủ các loại này thì
HE, CLAHE, Gamma mới thấy rõ sự khác biệt.

## Đối chiếu tiêu chí chấm

| Tiêu chí (theo cấu trúc Project 1) | Nhóm cần có |
|---|---|
| Đúng thuật toán | Công thức từng kỹ thuật (bảng trên) + giải thích đoạn code tương ứng |
| Chất lượng kết quả | Ảnh so sánh, histogram trước/sau, bảng CSV, bảng PSNR khử nhiễu |
| Giao diện và tính năng | Ảnh chụp GUI, mô tả luồng: mở → chọn kỹ thuật → chỉnh tham số → lưu |
| Báo cáo và demo | Video 5-15 phút: demo từng kỹ thuật trên ảnh phù hợp (HE/CLAHE/Gamma trên ảnh tối, Median trên ảnh nhiễu muối tiêu...) |
