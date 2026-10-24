"""
enhancement_methods.py

Cài đặt 6 kỹ thuật nâng cao chất lượng ảnh số:
    Histogram Equalization, CLAHE, Gamma Correction,
    Gaussian Filter, Median Filter, Sharpen.

Mỗi hàm nhận ảnh màu BGR (uint8) cùng các tham số, trả về ảnh BGR đã xử lý.
Cuối file có DANH_SACH_PHUONG_PHAP: mô tả tên hàm + các tham số (khoảng giá trị,
giá trị mặc định) để GUI và script đánh giá dùng chung (giống cách làm ở Project 1).
"""

import cv2
import numpy as np


# ---------------------------------------------------------------
# Hàm hỗ trợ
# ---------------------------------------------------------------
def ap_dung_tren_kenh_sang(anh_bgr, ham_xu_ly_kenh):
    """
    Chuyển ảnh sang YCrCb, chỉ xử lý kênh sáng Y rồi ghép lại.
    Cách này giữ nguyên màu sắc (không bị lệch màu như khi xử lý riêng từng kênh B, G, R).
    """
    anh_ycrcb = cv2.cvtColor(anh_bgr, cv2.COLOR_BGR2YCrCb)
    y, cr, cb = cv2.split(anh_ycrcb)
    y_moi = ham_xu_ly_kenh(y)
    anh_moi = cv2.merge([y_moi, cr, cb])
    return cv2.cvtColor(anh_moi, cv2.COLOR_YCrCb2BGR)


# ---------------------------------------------------------------
# 1. Histogram Equalization
# ---------------------------------------------------------------
def can_bang_histogram(anh_bgr, cuong_do=100):
    """
    Cân bằng histogram: dàn đều các mức xám để tăng độ tương phản toàn ảnh.
    cuong_do (0-100): 100 là cân bằng hoàn toàn, nhỏ hơn thì trộn với ảnh gốc.
    """
    anh_can_bang = ap_dung_tren_kenh_sang(anh_bgr, cv2.equalizeHist)
    alpha = cuong_do / 100.0
    return cv2.addWeighted(anh_bgr, 1 - alpha, anh_can_bang, alpha, 0)


# ---------------------------------------------------------------
# 2. CLAHE
# ---------------------------------------------------------------
def clahe(anh_bgr, clip_limit=2.0, tile=8):
    """
    CLAHE: cân bằng histogram cục bộ (chia ảnh thành lưới tile x tile ô nhỏ),
    có giới hạn độ tương phản clip_limit để không khuếch đại nhiễu quá mức.
    """
    bo_clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile, tile))
    return ap_dung_tren_kenh_sang(anh_bgr, bo_clahe.apply)


# ---------------------------------------------------------------
# 3. Gamma Correction
# ---------------------------------------------------------------
def gamma_correction(anh_bgr, gamma=1.0):
    """
    Hiệu chỉnh Gamma: s = 255 * (r / 255) ^ gamma
    gamma < 1: ảnh sáng lên (hợp với ảnh tối); gamma > 1: ảnh tối đi.
    Tính sẵn bảng tra (LUT) 256 giá trị rồi áp dụng cho toàn ảnh cho nhanh.
    """
    bang_tra = np.array([255.0 * ((i / 255.0) ** gamma) for i in range(256)])
    bang_tra = np.clip(np.round(bang_tra), 0, 255).astype(np.uint8)
    return cv2.LUT(anh_bgr, bang_tra)


# ---------------------------------------------------------------
# 4. Gaussian Filter
# ---------------------------------------------------------------
def gaussian_filter(anh_bgr, ksize=5, sigma=1.0):
    """Lọc Gaussian: làm mờ có trọng số theo hình chuông, giảm nhiễu Gaussian."""
    return cv2.GaussianBlur(anh_bgr, (ksize, ksize), sigma)


# ---------------------------------------------------------------
# 5. Median Filter
# ---------------------------------------------------------------
def median_filter(anh_bgr, ksize=5):
    """Lọc trung vị: thay mỗi điểm ảnh bằng giá trị trung vị của vùng lân cận, rất tốt với nhiễu muối tiêu."""
    return cv2.medianBlur(anh_bgr, ksize)


# ---------------------------------------------------------------
# 6. Sharpen (Unsharp Masking)
# ---------------------------------------------------------------
def sharpen(anh_bgr, cuong_do=1.5, ban_kinh=1.0):
    """
    Làm sắc nét bằng Unsharp Masking:
        ảnh_nét = ảnh_gốc + cuong_do * (ảnh_gốc - ảnh_mờ)
    Phần (ảnh_gốc - ảnh_mờ) chính là chi tiết/cạnh, cộng thêm vào ảnh gốc để cạnh nổi hơn.
    ban_kinh là sigma của bộ lọc Gaussian dùng tạo ảnh mờ.
    """
    anh_mo = cv2.GaussianBlur(anh_bgr, (0, 0), ban_kinh)
    return cv2.addWeighted(anh_bgr, 1 + cuong_do, anh_mo, -cuong_do, 0)


# ---------------------------------------------------------------
# Danh sách kỹ thuật + mô tả tham số (GUI tự dựng thanh trượt từ đây)
# kieu: "int" = số nguyên, "float" = số thực, "le" = số nguyên lẻ (kích thước kernel)
# ---------------------------------------------------------------
DANH_SACH_PHUONG_PHAP = {
    "Histogram Equalization": {
        "ham": can_bang_histogram,
        "tham_so": [
            {"ten": "cuong_do", "nhan": "Cường độ (%)", "min": 0, "max": 100, "mac_dinh": 100, "kieu": "int"},
        ],
    },
    "CLAHE": {
        "ham": clahe,
        "tham_so": [
            {"ten": "clip_limit", "nhan": "Clip limit", "min": 1.0, "max": 10.0, "mac_dinh": 2.0, "kieu": "float"},
            {"ten": "tile", "nhan": "Số ô lưới (tile)", "min": 2, "max": 16, "mac_dinh": 8, "kieu": "int"},
        ],
    },
    "Gamma Correction": {
        "ham": gamma_correction,
        "tham_so": [
            {"ten": "gamma", "nhan": "Gamma", "min": 0.2, "max": 3.0, "mac_dinh": 1.0, "kieu": "float"},
        ],
    },
    "Gaussian Filter": {
        "ham": gaussian_filter,
        "tham_so": [
            {"ten": "ksize", "nhan": "Kích thước kernel", "min": 3, "max": 15, "mac_dinh": 5, "kieu": "le"},
            {"ten": "sigma", "nhan": "Sigma", "min": 0.1, "max": 5.0, "mac_dinh": 1.0, "kieu": "float"},
        ],
    },
    "Median Filter": {
        "ham": median_filter,
        "tham_so": [
            {"ten": "ksize", "nhan": "Kích thước kernel", "min": 3, "max": 15, "mac_dinh": 5, "kieu": "le"},
        ],
    },
    "Sharpen": {
        "ham": sharpen,
        "tham_so": [
            {"ten": "cuong_do", "nhan": "Cường độ", "min": 0.0, "max": 5.0, "mac_dinh": 1.5, "kieu": "float"},
            {"ten": "ban_kinh", "nhan": "Bán kính (sigma)", "min": 0.5, "max": 5.0, "mac_dinh": 1.0, "kieu": "float"},
        ],
    },
}
