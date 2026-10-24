"""
danh_gia.py

Các hàm đánh giá chất lượng ảnh và vẽ histogram, dùng chung cho GUI và batch_evaluate.

Chỉ số không cần ảnh chuẩn (dùng để so sánh ảnh trước/sau):
    - Độ sáng trung bình
    - Độ tương phản (độ lệch chuẩn của mức xám)
    - Entropy (lượng thông tin của histogram)
    - Độ nét (phương sai của Laplacian)
Chỉ số cần ảnh chuẩn:
    - PSNR (dùng khi thử khử nhiễu: so ảnh đã lọc với ảnh sạch ban đầu)
"""

import cv2
import numpy as np


def chuyen_xam(anh):
    """Đổi ảnh BGR sang xám (nếu đã là ảnh xám thì giữ nguyên)."""
    if anh.ndim == 3:
        return cv2.cvtColor(anh, cv2.COLOR_BGR2GRAY)
    return anh


def do_sang_trung_binh(anh):
    """Giá trị mức xám trung bình (0-255): càng lớn ảnh càng sáng."""
    return float(chuyen_xam(anh).mean())


def do_tuong_phan(anh):
    """Độ lệch chuẩn của mức xám: càng lớn ảnh càng tương phản."""
    return float(chuyen_xam(anh).std())


def entropy(anh):
    """Entropy của histogram: H = -tổng(p * log2(p)). Càng lớn ảnh càng nhiều thông tin."""
    hist = cv2.calcHist([chuyen_xam(anh)], [0], None, [256], [0, 256]).ravel()
    p = hist / hist.sum()
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def do_net(anh):
    """Phương sai của Laplacian: càng lớn ảnh càng nét (nhiều cạnh/chi tiết)."""
    return float(cv2.Laplacian(chuyen_xam(anh), cv2.CV_64F).var())


def psnr(anh_chuan, anh_so_sanh):
    """PSNR (dB) giữa ảnh chuẩn và ảnh so sánh: càng lớn càng giống ảnh chuẩn."""
    mse = np.mean((anh_chuan.astype(np.float64) - anh_so_sanh.astype(np.float64)) ** 2)
    if mse == 0:
        return 100.0
    return float(10 * np.log10(255.0 ** 2 / mse))


def ve_histogram(anh, rong=420, cao=110):
    """Vẽ histogram mức xám của ảnh thành một ảnh BGR (nền tối, cột sáng)."""
    hist = cv2.calcHist([chuyen_xam(anh)], [0], None, [256], [0, 256]).ravel()
    hist = hist / hist.max() if hist.max() > 0 else hist

    khung = np.full((cao, rong, 3), 30, dtype=np.uint8)
    for i in range(256):
        x = int(i * (rong - 1) / 255)
        chieu_cao_cot = int(hist[i] * (cao - 20))
        if chieu_cao_cot > 0:
            cv2.line(khung, (x, cao - 15), (x, cao - 15 - chieu_cao_cot), (200, 200, 200), 2)

    cv2.line(khung, (0, cao - 14), (rong - 1, cao - 14), (110, 110, 110), 1)   # trục hoành

    cv2.putText(khung, "0", (2, cao - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
    cv2.putText(khung, "255", (rong - 28, cao - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
    return khung
