"""
batch_evaluate.py

Chạy 6 kỹ thuật nâng cao chất lượng ảnh trên bộ ảnh test (>=10 ảnh), xuất:
    1. bang_tong_hop.csv      : chỉ số trước/sau (độ sáng, tương phản, entropy, độ nét, thời gian)
    2. anh_so_sanh/           : ảnh ghép gốc + 6 kết quả cho từng ảnh test
    3. histogram/             : ảnh ghép histogram gốc / HE / CLAHE / Gamma
    4. khu_nhieu_psnr.csv     : thử khử nhiễu - PSNR của Gaussian Filter so với Median Filter
    5. khu_nhieu/             : ảnh ghép gốc / ảnh nhiễu / sau Gaussian / sau Median

Cách dùng:
    python batch_evaluate.py --input ./test_images --output ./eval_results
"""

import argparse
import csv
import time
from pathlib import Path

import cv2
import numpy as np

from enhancement_methods import DANH_SACH_PHUONG_PHAP
import danh_gia

DUOI_ANH_HOP_LE = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# Tham số dùng khi chạy hàng loạt (có thể chỉnh cho hợp với bộ ảnh của nhóm)
THAM_SO_MAC_DINH = {
    "Histogram Equalization": dict(cuong_do=100),
    "CLAHE": dict(clip_limit=2.0, tile=8),
    "Gamma Correction": dict(gamma=0.6),          # < 1 để làm sáng ảnh tối
    "Gaussian Filter": dict(ksize=5, sigma=1.0),
    "Median Filter": dict(ksize=5),
    "Sharpen": dict(cuong_do=1.5, ban_kinh=1.0),
}

# cv2.putText không vẽ được chữ có dấu nên nhãn trên ảnh ghép phải viết không dấu
CHU_NHIEU_KHONG_DAU = {"Muối tiêu": "muoi tieu", "Gaussian": "Gaussian"}

bo_sinh_ngau_nhien = np.random.default_rng(0)   # cố định để chạy lại ra cùng kết quả


# ================== NHIỄU DÙNG ĐỂ THỬ NGHIỆM ==================
def them_nhieu_muoi_tieu(anh, ty_le=0.03):
    """Nhiễu muối tiêu: ty_le (3%) điểm ảnh bị đổi thành trắng hoặc đen."""
    anh_nhieu = anh.copy()
    ngau_nhien = bo_sinh_ngau_nhien.random(anh.shape[:2])
    anh_nhieu[ngau_nhien < ty_le / 2] = 0
    anh_nhieu[(ngau_nhien >= ty_le / 2) & (ngau_nhien < ty_le)] = 255
    return anh_nhieu


def them_nhieu_gaussian(anh, do_lech=20):
    """Nhiễu Gaussian: cộng giá trị ngẫu nhiên theo phân phối chuẩn vào mọi điểm ảnh."""
    nhieu = bo_sinh_ngau_nhien.normal(0, do_lech, anh.shape)
    return np.clip(anh.astype(np.float64) + nhieu, 0, 255).astype(np.uint8)


# ================== HÀM CHÍNH ==================
def xu_ly_thu_muc(thu_muc_dau_vao, thu_muc_dau_ra):
    thu_muc_anh_so_sanh = thu_muc_dau_ra / "anh_so_sanh"
    thu_muc_histogram = thu_muc_dau_ra / "histogram"
    thu_muc_khu_nhieu = thu_muc_dau_ra / "khu_nhieu"
    for thu_muc in (thu_muc_anh_so_sanh, thu_muc_histogram, thu_muc_khu_nhieu):
        thu_muc.mkdir(parents=True, exist_ok=True)

    danh_sach_anh = sorted(
        p for p in thu_muc_dau_vao.iterdir() if p.suffix.lower() in DUOI_ANH_HOP_LE
    )
    if len(danh_sach_anh) == 0:
        raise SystemExit(f"Không tìm thấy ảnh nào trong: {thu_muc_dau_vao}")
    print(f"Tìm thấy {len(danh_sach_anh)} ảnh.")

    cac_dong_ket_qua = []
    cac_dong_khu_nhieu = []

    for duong_dan_anh in danh_sach_anh:
        anh = cv2.imread(str(duong_dan_anh))
        if anh is None:
            print(f"  Bỏ qua (không đọc được): {duong_dan_anh.name}")
            continue

        # --- Phần 1: chạy 6 kỹ thuật, tính chỉ số trước/sau ---
        ket_qua_tung_ky_thuat = {}
        for ten, thong_tin in DANH_SACH_PHUONG_PHAP.items():
            tham_so = THAM_SO_MAC_DINH[ten]

            thoi_gian_bat_dau = time.time()
            anh_sau = thong_tin["ham"](anh, **tham_so)
            thoi_gian_ms = (time.time() - thoi_gian_bat_dau) * 1000

            cac_dong_ket_qua.append({
                "ten_anh": duong_dan_anh.name,
                "ky_thuat": ten,
                "thoi_gian_ms": round(thoi_gian_ms, 3),
                "do_sang_truoc": round(danh_gia.do_sang_trung_binh(anh), 2),
                "do_sang_sau": round(danh_gia.do_sang_trung_binh(anh_sau), 2),
                "tuong_phan_truoc": round(danh_gia.do_tuong_phan(anh), 2),
                "tuong_phan_sau": round(danh_gia.do_tuong_phan(anh_sau), 2),
                "entropy_truoc": round(danh_gia.entropy(anh), 3),
                "entropy_sau": round(danh_gia.entropy(anh_sau), 3),
                "do_net_truoc": round(danh_gia.do_net(anh), 2),
                "do_net_sau": round(danh_gia.do_net(anh_sau), 2),
            })
            ket_qua_tung_ky_thuat[ten] = anh_sau

        luu_anh_so_sanh(anh, ket_qua_tung_ky_thuat,
                        thu_muc_anh_so_sanh / f"{duong_dan_anh.stem}_so_sanh.png")
        luu_anh_histogram(anh, ket_qua_tung_ky_thuat,
                          thu_muc_histogram / f"{duong_dan_anh.stem}_histogram.png")

        # --- Phần 2: thử khử nhiễu (Gaussian vs Median) ---
        hang_anh_khu_nhieu = []
        for ten_nhieu, ham_them_nhieu in [("Muối tiêu", them_nhieu_muoi_tieu),
                                          ("Gaussian", them_nhieu_gaussian)]:
            anh_nhieu = ham_them_nhieu(anh)
            sau_gaussian = DANH_SACH_PHUONG_PHAP["Gaussian Filter"]["ham"](
                anh_nhieu, **THAM_SO_MAC_DINH["Gaussian Filter"])
            sau_median = DANH_SACH_PHUONG_PHAP["Median Filter"]["ham"](
                anh_nhieu, **THAM_SO_MAC_DINH["Median Filter"])

            cac_dong_khu_nhieu.append({
                "ten_anh": duong_dan_anh.name,
                "loai_nhieu": ten_nhieu,
                "psnr_anh_nhieu": round(danh_gia.psnr(anh, anh_nhieu), 2),
                "psnr_sau_gaussian": round(danh_gia.psnr(anh, sau_gaussian), 2),
                "psnr_sau_median": round(danh_gia.psnr(anh, sau_median), 2),
            })
            hang_anh_khu_nhieu.append(
                (ten_nhieu, [anh, anh_nhieu, sau_gaussian, sau_median]))

        luu_anh_khu_nhieu(hang_anh_khu_nhieu,
                          thu_muc_khu_nhieu / f"{duong_dan_anh.stem}_khu_nhieu.png")

        print(f"  Đã xử lý: {duong_dan_anh.name}")

    ghi_csv(thu_muc_dau_ra / "bang_tong_hop.csv", cac_dong_ket_qua)
    ghi_csv(thu_muc_dau_ra / "khu_nhieu_psnr.csv", cac_dong_khu_nhieu)

    in_trung_binh_ky_thuat(cac_dong_ket_qua)
    in_trung_binh_khu_nhieu(cac_dong_khu_nhieu)
    print(f"\nĐã lưu kết quả trong thư mục: {thu_muc_dau_ra}")


# ================== GHI FILE / VẼ ẢNH GHÉP ==================
def ghi_csv(duong_dan, cac_dong):
    with open(duong_dan, "w", newline="", encoding="utf-8-sig") as f:   # utf-8-sig để Excel đọc đúng tiếng Việt
        ghi = csv.DictWriter(f, fieldnames=list(cac_dong[0].keys()))
        ghi.writeheader()
        ghi.writerows(cac_dong)


def them_nhan(anh_bgr, chu):
    """Vẽ chữ nhãn lên góc trên bên trái ảnh (có nền đen để dễ đọc)."""
    anh_co_chu = anh_bgr.copy()
    cv2.rectangle(anh_co_chu, (0, 0), (len(chu) * 9 + 10, 22), (0, 0, 0), -1)
    cv2.putText(anh_co_chu, chu, (5, 16), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 255, 0), 1, cv2.LINE_AA)
    return anh_co_chu


def chuan_bi_o(anh_bgr, chieu_rong_o, chieu_cao_o):
    return cv2.resize(anh_bgr, (chieu_rong_o, chieu_cao_o))


def luu_anh_so_sanh(anh, ket_qua_tung_ky_thuat, duong_dan_luu):
    """Ghép ảnh gốc + 6 kết quả thành lưới 2x4 (có 1 ô trống)."""
    rong_o = 300
    cao_o = int(anh.shape[0] * rong_o / anh.shape[1])

    cac_o = [them_nhan(chuan_bi_o(anh, rong_o, cao_o), "Goc")]
    for ten, anh_sau in ket_qua_tung_ky_thuat.items():
        cac_o.append(them_nhan(chuan_bi_o(anh_sau, rong_o, cao_o), ten))
    cac_o.append(np.zeros_like(cac_o[0]))   # ô trống cho đủ 8 ô

    luoi = np.vstack([np.hstack(cac_o[0:4]), np.hstack(cac_o[4:8])])
    cv2.imwrite(str(duong_dan_luu), luoi)


def luu_anh_histogram(anh, ket_qua_tung_ky_thuat, duong_dan_luu):
    """Ghép histogram của ảnh gốc, HE, CLAHE, Gamma thành lưới 2x2."""
    cac_anh = [
        ("Goc", anh),
        ("Histogram Equalization", ket_qua_tung_ky_thuat["Histogram Equalization"]),
        ("CLAHE", ket_qua_tung_ky_thuat["CLAHE"]),
        ("Gamma Correction", ket_qua_tung_ky_thuat["Gamma Correction"]),
    ]
    cac_o = [them_nhan(danh_gia.ve_histogram(a, rong=400, cao=140), ten) for ten, a in cac_anh]
    luoi = np.vstack([np.hstack(cac_o[0:2]), np.hstack(cac_o[2:4])])
    cv2.imwrite(str(duong_dan_luu), luoi)


def luu_anh_khu_nhieu(cac_hang, duong_dan_luu):
    """Mỗi hàng là 1 loại nhiễu: [ảnh gốc, ảnh nhiễu, sau Gaussian, sau Median]."""
    nhan_cot = ["Goc", "Co nhieu", "Sau Gaussian", "Sau Median"]
    rong_o = 300
    cao_o = int(cac_hang[0][1][0].shape[0] * rong_o / cac_hang[0][1][0].shape[1])

    cac_hang_anh = []
    for ten_nhieu, cac_anh in cac_hang:
        cac_o = []
        for chi_so, anh in enumerate(cac_anh):
            chu = nhan_cot[chi_so] if chi_so != 1 else "Nhieu " + CHU_NHIEU_KHONG_DAU[ten_nhieu]
            cac_o.append(them_nhan(chuan_bi_o(anh, rong_o, cao_o), chu))
        cac_hang_anh.append(np.hstack(cac_o))
    cv2.imwrite(str(duong_dan_luu), np.vstack(cac_hang_anh))


# ================== IN TRUNG BÌNH ==================
def in_trung_binh_ky_thuat(cac_dong):
    print("\n--- Trung bình theo kỹ thuật (trước → sau) ---")
    theo_ky_thuat = {}
    for dong in cac_dong:
        theo_ky_thuat.setdefault(dong["ky_thuat"], []).append(dong)

    for ten, ds in theo_ky_thuat.items():
        tb = lambda khoa: np.mean([d[khoa] for d in ds])
        print(f"{ten:24s} | {tb('thoi_gian_ms'):6.2f} ms | "
              f"sáng {tb('do_sang_truoc'):6.1f}→{tb('do_sang_sau'):6.1f} | "
              f"tương phản {tb('tuong_phan_truoc'):5.1f}→{tb('tuong_phan_sau'):5.1f} | "
              f"entropy {tb('entropy_truoc'):.2f}→{tb('entropy_sau'):.2f} | "
              f"độ nét {tb('do_net_truoc'):7.1f}→{tb('do_net_sau'):7.1f}")


def in_trung_binh_khu_nhieu(cac_dong):
    print("\n--- Thử khử nhiễu: PSNR trung bình (dB, càng cao càng tốt) ---")
    theo_loai = {}
    for dong in cac_dong:
        theo_loai.setdefault(dong["loai_nhieu"], []).append(dong)

    for ten, ds in theo_loai.items():
        tb = lambda khoa: np.mean([d[khoa] for d in ds])
        print(f"Nhiễu {ten:10s} | ảnh nhiễu {tb('psnr_anh_nhieu'):5.2f} | "
              f"sau Gaussian {tb('psnr_sau_gaussian'):5.2f} | sau Median {tb('psnr_sau_median'):5.2f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Thư mục chứa ảnh test")
    parser.add_argument("--output", type=str, default="./eval_results", help="Thư mục lưu kết quả")
    doi_so = parser.parse_args()
    xu_ly_thu_muc(Path(doi_so.input), Path(doi_so.output))
