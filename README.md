# BÁO CÁO & THỐNG KÊ TỶ LỆ HOÀN THÀNH THỰC TẬP (BACKEND FASTAPI)

* **Tác giả:** Nguyễn Văn Hiếu (Backend Developer)
* **Đối tượng tiếp nhận:** Frontend Team
* **Mục tiêu User Story (STT #33):** *"Là HR, tôi muốn xem tỷ lệ hoàn thành chương trình để đánh giá chất lượng thực tập."* (Thuộc Epic: *Báo cáo & thống kê*)

---

## 1. Tổng quan Endpoint

| Thông tin | Chi tiết |
| :--- | :--- |
| **Endpoint** | `GET /api/v1/reports/completion-rate` |
| **Chức năng** | Truy vấn tổng số lượng sinh viên, đếm số lượng theo từng trạng thái (`DangThucTap`, `HoanThanh`, `ThoiHoc`) và tự động tính toán tỷ lệ phần trăm (%) hoàn thành chương trình thực tập. |
| **Định dạng dữ liệu** | `application/json` |
| **CORS** | Đã bật mở cho `*`, hỗ trợ trực tiếp localhost (`3000`, `5173`, v.v.) |
| **Swagger UI** | `http://localhost:8000/docs` |
| **ReDoc UI** | `http://localhost:8000/redoc` |

---

## 2. Tham số truy vấn (Query Parameters)

Tất cả các tham số đều là **tùy chọn (Optional)**. Nếu không truyền, hệ thống sẽ thống kê trên toàn bộ sinh viên trong cơ sở dữ liệu:

| Tham số | Kiểu dữ liệu | Ví dụ | Mô tả |
| :--- | :--- | :--- | :--- |
| `university` | `string` | `ĐH Bách Khoa` | Lọc sinh viên theo tên trường đại học (tìm kiếm tương đối) |
| `department` | `string` | `Backend` | Lọc theo phòng ban thực tập (`Backend`, `Frontend`, `Mobile`...) |
| `start_date` | `date (YYYY-MM-DD)` | `2026-01-01` | Lọc theo ngày bắt đầu thực tập từ ngày |
| `end_date` | `date (YYYY-MM-DD)` | `2026-12-31` | Lọc theo ngày kết thúc thực tập đến ngày |

---

## 3. Cấu trúc Response (API Contract dành cho Frontend)

### Mã phản hồi: `200 OK`

```json
{
  "success": true,
  "message": "Lấy dữ liệu tỷ lệ hoàn thành chương trình thực tập thành công",
  "data": {
    "total_students": 30,
    "status_counts": {
      "DangThucTap": 9,
      "HoanThanh": 18,
      "ThoiHoc": 3
    },
    "completion_rate": 60.0,
    "percentages": {
      "DangThucTap": 30.0,
      "HoanThanh": 60.0,
      "ThoiHoc": 10.0
    },
    "chart_data": [
      {
        "status": "HoanThanh",
        "label": "Đã hoàn thành",
        "count": 18,
        "percentage": 60.0,
        "color": "#10B981"
      },
      {
        "status": "DangThucTap",
        "label": "Đang thực tập",
        "count": 9,
        "percentage": 30.0,
        "color": "#3B82F6"
      },
      {
        "status": "ThoiHoc",
        "label": "Thôi học",
        "count": 3,
        "percentage": 10.0,
        "color": "#EF4444"
      }
    ],
    "summary": "Tổng số 30 sinh viên. Trong đó 18 hoàn thành (60.0%), 9 đang thực tập (30.0%), và 3 thôi học (10.0%).",
    "filters_applied": {
      "university": null,
      "department": null,
      "start_date": null,
      "end_date": null
    }
  }
}
```

### Ý nghĩa các trường:
* **`total_students`**: Tổng số lượng sinh viên trong bộ lọc.
* **`status_counts`**: Đếm số lượng theo 3 trạng thái chuẩn:
  * `DangThucTap`: Số sinh viên đang trong thời gian thực tập.
  * `HoanThanh`: Số sinh viên đã hoàn thành chương trình.
  * `ThoiHoc`: Số sinh viên thôi học hoặc nghỉ thực tập.
* **`completion_rate`**: **Tỷ lệ hoàn thành (%)** = `(HoanThanh / total_students) * 100` (được làm tròn 2 chữ số thập phân, tự động xử lý trả về `0.0` nếu không có sinh viên để tránh lỗi chia cho 0).
* **`percentages`**: Tỷ lệ phần trăm chi tiết của cả 3 trạng thái.
* **`chart_data`**: Dữ liệu đã được chuẩn hóa sẵn kèm **mã màu HEX** và **nhãn tiếng Việt** giúp anh em Frontend render trực tiếp vào các thư viện biểu đồ như **Chart.js**, **Recharts**, **ApexCharts** mà không cần map lại dữ liệu.
* **`summary`**: Câu diễn giải tự nhiên sẵn sàng hiển thị lên Dashboard.

---

## 4. Hướng dẫn cài đặt & khởi chạy Backend

### Bước 1: Tạo môi trường ảo và cài đặt thư viện
```bash
# Tạo môi trường ảo Python
python -m venv venv

# Kích hoạt môi trường (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Hoặc kích hoạt trên Linux/macOS
# source venv/bin/activate

# Cài đặt các gói phụ thuộc
pip install -r requirements.txt
```

### Bước 2: Nạp dữ liệu mẫu (Seed Data)
Backend đã chuẩn bị sẵn 30 bản ghi thực tập sinh với đầy đủ các trạng thái và trường đại học:
```bash
python seed_data.py
```

### Bước 3: Khởi động máy chủ FastAPI
```bash
uvicorn app.main:app --reload --port 8000
```
* Backend API hoạt động tại: `http://localhost:8000`
* Tài liệu Swagger tương tác: `http://localhost:8000/docs`

### Bước 4: Chạy kiểm thử tự động (Unit / Integration Tests)
```bash
pytest tests/ -v
```

---

## 5. Ví dụ mã tích hợp cho Frontend (React / Vue / Axios)

### Ví dụ gọi API bằng Axios / Fetch trong React:

```tsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface CompletionRateData {
  total_students: number;
  status_counts: {
    DangThucTap: number;
    HoanThanh: number;
    ThoiHoc: number;
  };
  completion_rate: number;
  chart_data: Array<{
    status: string;
    label: string;
    count: number;
    percentage: number;
    color: string;
  }>;
  summary: string;
}

export const CompletionRateCard: React.FC = () => {
  const [data, setData] = useState<CompletionRateData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    axios.get('http://localhost:8000/api/v1/reports/completion-rate')
      .then(response => {
        if (response.data.success) {
          setData(response.data.data);
        }
      })
      .catch(error => console.error("Lỗi khi tải báo cáo:", error))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Đang tải dữ liệu báo cáo...</div>;
  if (!data) return <div>Không thể lấy dữ liệu.</div>;

  return (
    <div className="report-card p-6 bg-white rounded-xl shadow-md">
      <h3 className="text-xl font-bold mb-2">Thống Kê Tỷ Lệ Hoàn Thành Thực Tập</h3>
      <p className="text-gray-600 mb-4">{data.summary}</p>
      
      {/* Thẻ hiển thị số liệu chính */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="text-sm text-blue-600">Tổng sinh viên</div>
          <div className="text-2xl font-bold">{data.total_students}</div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="text-sm text-green-600">Đã hoàn thành</div>
          <div className="text-2xl font-bold">{data.status_counts.HoanThanh}</div>
        </div>
        <div className="bg-yellow-50 p-4 rounded-lg">
          <div className="text-sm text-yellow-600">Đang thực tập</div>
          <div className="text-2xl font-bold">{data.status_counts.DangThucTap}</div>
        </div>
        <div className="bg-red-50 p-4 rounded-lg">
          <div className="text-sm text-red-600">Thôi học</div>
          <div className="text-2xl font-bold">{data.status_counts.ThoiHoc}</div>
        </div>
      </div>

      {/* Tỷ lệ hoàn thành nổi bật */}
      <div className="mb-4">
        <div className="flex justify-between font-semibold mb-1">
          <span>Tiến độ hoàn thành chương trình</span>
          <span className="text-green-600 font-bold">{data.completion_rate}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-4">
          <div 
            className="bg-green-500 h-4 rounded-full transition-all duration-500" 
            style={{ width: `${data.completion_rate}%` }}
          />
        </div>
      </div>
    </div>
  );
};
```

---

## 6. Cấu trúc thư mục dự án

```
.
├── app/
│   ├── __init__.py
│   ├── main.py                  # Khởi tạo FastAPI, CORS, Lifespan DB
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Cài đặt hệ thống, biến môi trường, CORS
│   │   └── database.py          # Kết nối SQLAlchemy, engine, get_db
│   ├── models/
│   │   ├── __init__.py
│   │   └── intern.py            # Model Intern & Enum InternStatus
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── report.py            # Pydantic schemas cho báo cáo & biểu đồ
│   ├── services/
│   │   ├── __init__.py
│   │   └── report_service.py    # Business logic: Đếm SQL & tính tỷ lệ %
│   └── api/
│       ├── __init__.py
│       └── v1/
│           ├── __init__.py
│           ├── api.py           # Router tổng API v1
│           └── endpoints/
│               ├── __init__.py
│               └── reports.py   # Endpoint GET /reports/completion-rate
├── tests/
│   ├── __init__.py
│   └── test_reports.py          # Kiểm thử tự động pytest
├── seed_data.py                 # Script tạo dữ liệu mẫu sinh viên thực tập
├── requirements.txt             # Danh sách dependencies
└── README.md                    # Tài liệu hướng dẫn & API Contract
```
