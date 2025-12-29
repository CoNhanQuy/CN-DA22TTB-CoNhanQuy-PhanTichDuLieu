# 📊 Phân tích Dữ liệu Bán lẻ Trực tuyến
**Đồ án Thực tập Chuyên ngành — Phân tích Dữ liệu**  
**Sinh viên:** Cô Nhân Quý  
**Giảng viên hướng dẫn:** TS. Nguyễn Bảo Ân

---

## 🚀 Mô tả ngắn
Dự án thực hiện quy trình Phân tích Dữ liệu hoàn chỉnh trên bộ dữ liệu **Online Retail (UCI)** nhằm chuyển dữ liệu thô thành insight kinh doanh: phân tích doanh thu, xu hướng và phân khúc khách hàng. Kèm theo một **Dashboard tương tác** được xây dựng bằng **Streamlit** để người dùng khám phá dữ liệu dễ dàng.

## ✨ Tính năng chính
- Tiền xử lý và làm sạch dữ liệu (missing values, outliers, orders canceled)
- Phân tích EDA: doanh thu theo thời gian, top sản phẩm, phân tích theo quốc gia
- Phân khúc khách hàng bằng **RFM** (Recency, Frequency, Monetary)
- Dashboard Streamlit để tương tác trực tiếp

## 📂 Bộ dữ liệu
- **Nguồn:** UCI Machine Learning Repository — Online Retail
- **Kích thước:** ~541,909 dòng (01/12/2010 — 09/12/2011)
- **Thuộc tính chính:** `InvoiceNo`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `UnitPrice`, `CustomerID`, `Country`

## 🧰 Công nghệ
Python 3.x · Pandas · NumPy · Matplotlib · Seaborn · Streamlit

## 🔧 Cài đặt & Cách chạy

Có hai cách phổ biến để chạy mã: **(A) Google Colab (khuyến nghị)** hoặc **(B) Chạy cục bộ (VS Code / Jupyter)**.

### A) Chạy trên Google Colab (khuyến nghị)
- Mở trực tiếp notebook trên Colab: https://colab.research.google.com/github/CoNhanQuy/CN-DA22TTB-CoNhanQuy-PhanTichDuLieu/blob/main/CN-DA22TTB-CoNhanQuy-PTDL-python.ipynb
- Ví dụ các bước trong 1 cell Colab:
```python
# Cài thư viện cần thiết (chỉ cần cài trong Colab 1 lần)
!pip install ucimlrepo pandas numpy matplotlib seaborn scikit-learn graphviz joblib scipy statsmodels

# (tuỳ chọn) clone repo nếu cần
!git clone https://github.com/CoNhanQuy/CN-DA22TTB-CoNhanQuy-PhanTichDuLieu.git
%cd CN-DA22TTB-CoNhanQuy-PhanTichDuLieu

# (tuỳ chọn) mount Google Drive nếu dữ liệu nằm trên Drive
from google.colab import drive
drive.mount('/content/drive')
```
- Mở notebook trên giao diện Colab và chạy từng cell.

### B) Chạy cục bộ (Windows / VS Code / Jupyter)
```powershell
git clone https://github.com/CoNhanQuy/CN-DA22TTB-CoNhanQuy-PhanTichDuLieu.git
cd CN-DA22TTB-CoNhanQuy-PhanTichDuLieu
python -m venv venv
venv\Scripts\Activate.ps1
# Cài đặt thư viện từ file cấu hình
pip install -r setup/requirements.txt
# Chạy ứng dụng
streamlit run scr/app.py
```
- Mở notebook `CN-DA22TTB-CoNhanQuy-PTDL-python.ipynb` bằng VS Code hoặc Jupyter và chạy các cell.


```
## 📈 Hướng dẫn sử dụng ngắn
- Mở trang Streamlit sau khi chạy (mặc định http://localhost:8501)
- Tải dữ liệu hoặc dùng dataset mẫu có sẵn
- Khám phá các tab: Tổng quan, Xu hướng, RFM — xuất báo cáo khi cần

## 🗂 Cấu trúc thư mục (tổng quan)
- `setup/` — script cài đặt
- `thesis/` — nội dung luận văn
- `progress-report/` — báo cáo tiến độ
- `CN-DA22TTB-CoNhanQuy-PTDL-python.ipynb` — main analysis notebook (Colab / Jupyter)
- `README.md` — file này

## 📌 Kết quả chính & Hướng phát triển
- Phát hiện nhóm **"At Risk"** có giá trị cao cần chăm sóc đặc biệt
- Hướng tiếp theo: tích hợp **KMeans clustering**, mô hình dự báo (**Prophet**/ARIMA), hệ thống gợi ý sản phẩm
