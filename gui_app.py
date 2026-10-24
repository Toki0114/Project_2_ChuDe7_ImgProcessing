"""
gui_app.py

Giao diện GUI (Tkinter) cho Project 2 - Chủ đề 7: Nâng cao chất lượng ảnh số.
Viết theo kiểu hàm + biến global (giống Project 1) cho dễ đọc, dễ giải thích.

Chức năng:
    - Mở ảnh hoặc video
    - Chọn kỹ thuật (Histogram Equalization, CLAHE, Gamma, Gaussian, Median, Sharpen)
    - Thanh trượt tham số tự đổi theo từng kỹ thuật
    - Hiển thị ảnh trước/sau cùng histogram
    - Hiển thị chỉ số đánh giá (độ sáng, độ tương phản, entropy, độ nét)
    - Lưu kết quả
"""

import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import cv2
from PIL import Image, ImageTk

from enhancement_methods import DANH_SACH_PHUONG_PHAP
import danh_gia

KICH_THUOC_HIEN_THI = 430  # ảnh hiển thị tối đa 430px chiều rộng/cao

# ----- Biến global lưu trạng thái chương trình -----
anh_goc = None            # ảnh màu BGR gốc (đọc từ file hoặc khung hình video)
anh_ket_qua = None        # ảnh đã xử lý (để lưu file)

video_dang_mo = None      # đối tượng cv2.VideoCapture khi đang phát video
video_dang_phat = False   # có đang phát video hay không


# ================== MỞ / LƯU FILE ==================
def mo_anh():
    """Mở hộp thoại chọn ảnh, đọc ảnh và hiển thị kết quả."""
    global anh_goc

    dung_video()

    duong_dan = filedialog.askopenfilename(
        title="Chọn ảnh",
        filetypes=[("Ảnh", "*.jpg *.jpeg *.png *.bmp *.webp")]
    )
    if not duong_dan:
        return

    anh_doc_duoc = cv2.imread(duong_dan)
    if anh_doc_duoc is None:
        messagebox.showerror("Lỗi", "Không đọc được ảnh, kiểm tra lại file.")
        return

    anh_goc = anh_doc_duoc
    xu_ly_va_hien_thi()


def mo_video():
    """Mở hộp thoại chọn video, bắt đầu phát và xử lý từng khung hình."""
    global video_dang_mo, video_dang_phat

    dung_video()

    duong_dan = filedialog.askopenfilename(
        title="Chọn video",
        filetypes=[("Video", "*.mp4 *.avi *.mov *.mkv")]
    )
    if not duong_dan:
        return

    video_dang_mo = cv2.VideoCapture(duong_dan)
    if not video_dang_mo.isOpened():
        messagebox.showerror("Lỗi", "Không mở được video, kiểm tra lại file.")
        video_dang_mo = None
        return

    video_dang_phat = True
    phat_khung_hinh_tiep_theo()


def dung_video():
    """Dừng phát video (nếu đang phát) và giải phóng tài nguyên."""
    global video_dang_mo, video_dang_phat
    video_dang_phat = False
    if video_dang_mo is not None:
        video_dang_mo.release()
        video_dang_mo = None


def phat_khung_hinh_tiep_theo():
    """Đọc 1 khung hình, xử lý như ảnh tĩnh, rồi tự gọi lại sau 30ms (~30 khung hình/giây)."""
    global anh_goc

    if not video_dang_phat or video_dang_mo is None:
        return

    doc_duoc, khung_hinh = video_dang_mo.read()
    if not doc_duoc:
        dung_video()
        nhan_trang_thai.set("Video đã phát xong.")
        return

    anh_goc = khung_hinh
    xu_ly_va_hien_thi()
    cua_so.after(30, phat_khung_hinh_tiep_theo)


def luu_ket_qua():
    """Lưu ảnh kết quả hiện tại ra file."""
    if anh_ket_qua is None:
        messagebox.showwarning("Chú ý", "Chưa có kết quả để lưu.")
        return

    duong_dan = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")]
    )
    if not duong_dan:
        return

    cv2.imwrite(duong_dan, anh_ket_qua)
    messagebox.showinfo("Thành công", f"Đã lưu vào:\n{duong_dan}")


# ================== THAM SỐ ==================
def lay_gia_tri_tham_so(chi_so):
    """Đọc giá trị thanh trượt thứ chi_so và đổi về đúng kiểu (int / float / số lẻ)."""
    ten_phuong_phap = bien_phuong_phap.get()
    mo_ta = DANH_SACH_PHUONG_PHAP[ten_phuong_phap]["tham_so"][chi_so]
    gia_tri = bien_tham_so[chi_so].get()

    if mo_ta["kieu"] == "int":
        return int(round(gia_tri))
    if mo_ta["kieu"] == "le":
        gia_tri = int(round(gia_tri))
        if gia_tri % 2 == 0:      # kích thước kernel bắt buộc là số lẻ
            gia_tri += 1
        return min(gia_tri, mo_ta["max"])
    return round(float(gia_tri), 2)


def cap_nhat_giao_dien_tham_so():
    """Khi đổi kỹ thuật: đặt lại nhãn, khoảng giá trị, giá trị mặc định cho các thanh trượt."""
    ten_phuong_phap = bien_phuong_phap.get()
    danh_sach_tham_so = DANH_SACH_PHUONG_PHAP[ten_phuong_phap]["tham_so"]

    for i in range(2):
        if i < len(danh_sach_tham_so):
            mo_ta = danh_sach_tham_so[i]
            nhan_tham_so[i].config(text=mo_ta["nhan"] + ":")
            thanh_truot[i].config(from_=mo_ta["min"], to=mo_ta["max"])
            bien_tham_so[i].set(mo_ta["mac_dinh"])
            nhan_gia_tri[i].config(text=str(mo_ta["mac_dinh"]))
            for widget in (nhan_tham_so[i], thanh_truot[i], nhan_gia_tri[i]):
                widget.grid()          # hiện lại
        else:
            for widget in (nhan_tham_so[i], thanh_truot[i], nhan_gia_tri[i]):
                widget.grid_remove()   # ẩn thanh trượt không dùng


def doi_ky_thuat(*_):
    cap_nhat_giao_dien_tham_so()
    xu_ly_va_hien_thi()


def doi_tham_so(*_):
    """Khi kéo thanh trượt: cập nhật số hiển thị rồi xử lý lại."""
    ten_phuong_phap = bien_phuong_phap.get()
    so_tham_so = len(DANH_SACH_PHUONG_PHAP[ten_phuong_phap]["tham_so"])
    for i in range(so_tham_so):
        nhan_gia_tri[i].config(text=str(lay_gia_tri_tham_so(i)))
    xu_ly_va_hien_thi()


# ================== XỬ LÝ VÀ HIỂN THỊ ==================
def xu_ly_va_hien_thi(*_):
    """Hàm chính: lấy kỹ thuật + tham số hiện tại, xử lý ảnh, cập nhật giao diện."""
    global anh_ket_qua

    if anh_goc is None:
        return

    ten_phuong_phap = bien_phuong_phap.get()
    ham_xu_ly = DANH_SACH_PHUONG_PHAP[ten_phuong_phap]["ham"]
    danh_sach_tham_so = DANH_SACH_PHUONG_PHAP[ten_phuong_phap]["tham_so"]

    tham_so = {}
    for i, mo_ta in enumerate(danh_sach_tham_so):
        tham_so[mo_ta["ten"]] = lay_gia_tri_tham_so(i)

    thoi_gian_bat_dau = time.time()
    anh_ket_qua = ham_xu_ly(anh_goc, **tham_so)
    thoi_gian_xu_ly = (time.time() - thoi_gian_bat_dau) * 1000

    nhan_trang_thai.set(
        f"{ten_phuong_phap} | {thoi_gian_xu_ly:.1f} ms | "
        f"Độ sáng: {danh_gia.do_sang_trung_binh(anh_goc):.1f} → {danh_gia.do_sang_trung_binh(anh_ket_qua):.1f} | "
        f"Tương phản: {danh_gia.do_tuong_phan(anh_goc):.1f} → {danh_gia.do_tuong_phan(anh_ket_qua):.1f} | "
        f"Entropy: {danh_gia.entropy(anh_goc):.2f} → {danh_gia.entropy(anh_ket_qua):.2f} | "
        f"Độ nét: {danh_gia.do_net(anh_goc):.0f} → {danh_gia.do_net(anh_ket_qua):.0f}"
    )

    hien_thi_anh(anh_goc, anh_ket_qua)


def hien_thi_anh(anh_truoc, anh_sau):
    """Hiển thị ảnh trước/sau và histogram tương ứng."""
    cap_hinh = [
        (nhan_anh_trai, anh_truoc),
        (nhan_anh_phai, anh_sau),
    ]
    cap_histogram = [
        (nhan_hist_trai, anh_truoc),
        (nhan_hist_phai, anh_sau),
    ]

    for nhan, anh in cap_hinh:
        anh_tk = doi_sang_anh_tkinter(cv2.cvtColor(anh, cv2.COLOR_BGR2RGB))
        nhan.configure(image=anh_tk)
        nhan.image = anh_tk  # giữ tham chiếu để ảnh không bị xóa

    for nhan, anh in cap_histogram:
        hist_tk = doi_sang_anh_tkinter(cv2.cvtColor(danh_gia.ve_histogram(anh), cv2.COLOR_BGR2RGB))
        nhan.configure(image=hist_tk)
        nhan.image = hist_tk


def doi_sang_anh_tkinter(anh_rgb):
    """Resize ảnh cho vừa khung hiển thị và đổi sang định dạng PhotoImage của Tkinter."""
    cao, rong = anh_rgb.shape[:2]
    ty_le = KICH_THUOC_HIEN_THI / max(rong, cao)
    if ty_le < 1:
        anh_rgb = cv2.resize(anh_rgb, (int(rong * ty_le), int(cao * ty_le)))
    return ImageTk.PhotoImage(Image.fromarray(anh_rgb))


# ================== XÂY DỰNG GIAO DIỆN ==================
cua_so = tk.Tk()
cua_so.title("Chủ đề 7 - Project 2: Nâng cao chất lượng ảnh số")
cua_so.geometry("960x760")

# --- Thanh công cụ trên cùng ---
khung_tren = ttk.Frame(cua_so, padding=8)
khung_tren.pack(side=tk.TOP, fill=tk.X)

ttk.Button(khung_tren, text="Mở ảnh...", command=mo_anh).pack(side=tk.LEFT, padx=4)
ttk.Button(khung_tren, text="Mở video...", command=mo_video).pack(side=tk.LEFT, padx=4)
ttk.Button(khung_tren, text="Dừng video", command=dung_video).pack(side=tk.LEFT, padx=4)
ttk.Button(khung_tren, text="Lưu kết quả...", command=luu_ket_qua).pack(side=tk.LEFT, padx=4)

ttk.Label(khung_tren, text="Kỹ thuật:").pack(side=tk.LEFT, padx=(20, 4))
bien_phuong_phap = tk.StringVar(value="Histogram Equalization")
combo_phuong_phap = ttk.Combobox(
    khung_tren, textvariable=bien_phuong_phap, state="readonly",
    values=list(DANH_SACH_PHUONG_PHAP.keys()), width=22
)
combo_phuong_phap.pack(side=tk.LEFT)
combo_phuong_phap.bind("<<ComboboxSelected>>", doi_ky_thuat)

# --- Khung tham số (2 hàng thanh trượt, kỹ thuật nào ít tham số thì ẩn bớt) ---
khung_tham_so = ttk.LabelFrame(cua_so, text="Tham số", padding=8)
khung_tham_so.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)

bien_tham_so = [tk.DoubleVar(value=0), tk.DoubleVar(value=0)]
nhan_tham_so = []
thanh_truot = []
nhan_gia_tri = []
for i in range(2):
    nhan_tham_so.append(ttk.Label(khung_tham_so, text="", width=20))
    nhan_tham_so[i].grid(row=i, column=0, sticky="w")

    thanh_truot.append(ttk.Scale(khung_tham_so, from_=0, to=1, orient=tk.HORIZONTAL,
                                 variable=bien_tham_so[i], command=doi_tham_so))
    thanh_truot[i].grid(row=i, column=1, sticky="ew", padx=8)

    nhan_gia_tri.append(ttk.Label(khung_tham_so, text="", width=6))
    nhan_gia_tri[i].grid(row=i, column=2)

khung_tham_so.columnconfigure(1, weight=1)

# --- Khung hiển thị: mỗi bên gồm ảnh + histogram ---
khung_hien_thi = ttk.Frame(cua_so)
khung_hien_thi.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=4)

khung_trai = ttk.LabelFrame(khung_hien_thi, text="Ảnh gốc")
khung_trai.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
nhan_anh_trai = ttk.Label(khung_trai)
nhan_anh_trai.pack()
nhan_hist_trai = ttk.Label(khung_trai)
nhan_hist_trai.pack(pady=(6, 0))

khung_phai = ttk.LabelFrame(khung_hien_thi, text="Ảnh sau xử lý")
khung_phai.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
nhan_anh_phai = ttk.Label(khung_phai)
nhan_anh_phai.pack()
nhan_hist_phai = ttk.Label(khung_phai)
nhan_hist_phai.pack(pady=(6, 0))

# --- Thanh trạng thái ---
nhan_trang_thai = tk.StringVar(value="Chưa có ảnh. Hãy nhấn 'Mở ảnh...' để bắt đầu.")
ttk.Label(cua_so, textvariable=nhan_trang_thai, padding=8, wraplength=930).pack(side=tk.BOTTOM, fill=tk.X)


def khi_dong_cua_so():
    """Giải phóng video trước khi thoát chương trình."""
    dung_video()
    cua_so.destroy()


cua_so.protocol("WM_DELETE_WINDOW", khi_dong_cua_so)
cap_nhat_giao_dien_tham_so()  # dựng thanh trượt cho kỹ thuật mặc định

if __name__ == "__main__":
    cua_so.mainloop()
