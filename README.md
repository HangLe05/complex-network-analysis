<<<<<<< HEAD
Ứng dụng mạng phức hợp trong phân tích cộng đồng và lan truyền thông tin trên YouTube

1. Giới thiệu
Đề tài xây dựng hệ thống phân tích mạng phức hợp trên dữ liệu YouTube, tập trung vào:
- Phân tích đặc trưng mạng.  
- Phát hiện cộng đồng bằng **HIT-Leiden**.  
- Mô phỏng lan truyền thông tin với mô hình **Independent Cascade (IC)** và **Linear Threshold (LT)**.  

Ứng dụng được xây dựng dưới dạng web với **Flask**, kết hợp **Python** và **HTML/CSS/JavaScript**.

---

## 2. Mục tiêu
- Xây dựng và phân tích mạng phức hợp từ dữ liệu YouTube.  
- Tính toán các đặc trưng: số nút, số cạnh, Degree, Clustering Coefficient, Average Shortest Path Length, Diameter, Assortativity, Centrality.  
- Phát hiện và phân tích cấu trúc cộng đồng bằng **HIT-Leiden**.  
- Mô phỏng lan truyền thông tin bằng IC và LT.  
- Trực quan hóa kết quả trên giao diện web.

---

## 3. Thuật toán và mô hình
### Phát hiện cộng đồng
- **HIT-Leiden**: cập nhật cộng đồng trên mạng động qua các giai đoạn Inc-Movement, Inc-Refinement, Inc-Aggregation và Deferred Update.  

### Lan truyền thông tin
- **Independent Cascade (IC)**: mô phỏng lan truyền dựa trên xác suất *p*. Seed là node có Degree cao nhất trong cộng đồng.  
- **Linear Threshold (LT)**: node kích hoạt khi ảnh hưởng từ lân cận đạt ngưỡng *Threshold* (0–1).

---

## 4. Chức năng hệ thống
- **Phân tích mạng**: `GET /analyze-network` → trả về thống kê đặc trưng mạng.  
- **Phân tích cộng đồng**: `GET /analyze-communities` → chạy HIT-Leiden, trả về số lượng cộng đồng, kích thước, modularity.  
- **Mô phỏng IC**: `POST /run-ic` với đầu vào `{ "community_index": 0, "p": 0.1 }`.  
- **Mô phỏng LT**: `POST /run-lt` với đầu vào `{ "community_index": 0, "threshold": 0.5 }`.

---

## 5. Giao diện
- **Mạng phức hợp**: hiển thị đặc trưng mạng.  
- **Cộng đồng HIT-Leiden**: hiển thị thông tin cộng đồng.  
- **Lan truyền IC**: nhập *p*, chạy mô phỏng, xem biểu đồ.  
- **Lan truyền LT**: nhập *Threshold*, chạy mô phỏng, xem biểu đồ.  
- Kết quả gồm biểu đồ số node bị ảnh hưởng, node mới kích hoạt và hình ảnh mạng.

---

## 6. Công nghệ sử dụng
- Python 3.9.13  
- Flask  
- NetworkX, igraph, leidenalg  
- NumPy, Pandas, Matplotlib  
- Bootstrap 5, Chart.js  
- HTML/CSS/JavaScript  

---

## 7. Cấu trúc thư mục

Youtube/
│
├── data/
│   ├── raw_data/              # Dữ liệu thô từ YouTube
│   └── processed_data/        # Dữ liệu đã tiền xử lý
│
├── env/                       # Môi trường ảo Python (venv)
│   ├── Include/
│   ├── Lib/
│   ├── Scripts/
│   └── pyvenv.cfg
│
├── src/                       # Mã nguồn chính cho phân tích mạng
│   ├── analysis_worker.py     # Xử lý phân tích song song
│   ├── community_detection.py # Thuật toán Leiden & HIT-Leiden
│   ├── ic_model.py            # Mô hình lan truyền IC
│   ├── lt_model.py            # Mô hình lan truyền LT
│   ├── network_analysis.py    # Phân tích đặc trưng mạng phức hợp
│   ├── preprocess.py          # Tiền xử lý dữ liệu
│   └── main.py                # Điểm khởi chạy chính
│
├── web/                       # Giao diện web Flask
│   ├── static/
│   │   ├── css/style.css
│   │   ├── js/main.js
│   │   └── img/network.png
│   ├── templates/index.html
│   ├── app.py                 # Flask app
│   ├── network_stats.json     # Thống kê mạng
│   └── requirements.txt       # Thư viện cần thiết
│
├── Youtube.py                 # Script tổng hợp
├── Youtube.pyproj             # Cấu hình dự án Python
└── Youtube.sln                # Cấu hình giải pháp (Visual Studio)

## 8. Cài đặt
Tạo môi trường ảo:
```bash
python -m venv env
Kích hoạt:

bash
.\env\Scripts\activate

Nếu PowerShell chặn script:
bash
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\env\Scripts\activate

Cài đặt thư viện:
bash
pip install flask networkx numpy pandas matplotlib igraph leidenalg scipy

# 9. Chạy hệ thống
bash
python .\web\app.py


# 10. Quy trình sử dụng
Chuẩn bị và tiền xử lý dữ liệu YouTube.

Xây dựng đồ thị và lưu dữ liệu đã xử lý.

Khởi động Flask.

Phân tích đặc trưng mạng.

Phân tích cộng đồng bằng HIT-Leiden.

Chọn cộng đồng cần mô phỏng.

Chạy IC với xác suất p.

Chạy LT với Threshold.

Quan sát và so sánh kết quả lan truyền.

# 11. Kết quả đầu ra
Thống kê đặc trưng mạng.

Số lượng và kích thước cộng đồng.

Modularity.

Seed node.

Số node được kích hoạt.

Timeline lan truyền.

Biểu đồ node bị ảnh hưởng và node mới kích hoạt.

Đồ thị mạng trực quan.
=======
# complex-network-analysis
>>>>>>> 21a2dd185c44371027c62d1faddee1e12bfb7573
