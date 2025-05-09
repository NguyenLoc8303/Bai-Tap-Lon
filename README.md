# B-i-T-p-L-n
Website Phạt nguộ
Kiểm Tra Phạt Nguội CSGT Tự Động
Tool tự động kiểm tra phạt nguội từ trang web CSGT Việt Nam (https://www.csgt.vn/tra-cuu-phuong-tien-vi-pham.htm) và gửi thông báo qua email nếu có vi phạm.
Tính năng

Tự động kiểm tra phạt nguội cho biển số xe đã đăng ký
Lên lịch chạy tự động vào 6h sáng và 12h trưa hàng ngày
Gửi thông báo qua email khi có kết quả (có hoặc không có vi phạm)
Hỗ trợ cả ô tô và xe máy

Yêu cầu hệ thống

Python 3.7 hoặc cao hơn
Google Chrome đã cài đặt (để WebDriver hoạt động)
Kết nối internet ổn định

Cài đặt
Bước 1: Clone repository
bashgit clone https://github.com/your-username/phat-nguoi-checker.git
cd phat-nguoi-checker
Bước 2: Tạo môi trường ảo (khuyến nghị)
bashpython -m venv venv
Kích hoạt môi trường ảo:
Windows:
bashvenv\Scripts\activate
Bước 3: Cài đặt các thư viện cần thiết
bashpip install -r requirements.txt
Bước 4: Cấu hình thông tin cá nhân
# Thông tin về phương tiện cần kiểm tra
BIEN_SO=51A-12345
LOAI_PHUONG_TIEN=Ô tô  # "Ô tô" hoặc "Xe máy"

# Thông tin email để gửi thông báo
RECEIVER_EMAIL=loc_2151220249@dau.edu.vn
EMAIL_USER=nguyenloc8303@gmail.com
EMAIL_PASS=lpoa eqvo fhct wqsf
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
