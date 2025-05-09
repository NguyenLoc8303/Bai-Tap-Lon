import os
import time
import logging
import schedule
import smtplib
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("phat_nguoi.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Tải các biến môi trường từ file .env
load_dotenv()

def parse_arguments():
    # Phân tích các đối số dòng lệnh.
    parser = argparse.ArgumentParser(description='Kiểm tra phạt nguội CSGT.')
    parser.add_argument('--bien_so', type=str, help='Biển số xe')
    parser.add_argument('--loai_phuong_tien', type=str, choices=['Ô tô', 'Xe máy'], help='Loại phương tiện')
    parser.add_argument('--email', type=str, help='Email để gửi thông báo')
    return parser.parse_args()

def setup_driver():
    # Thiết lập trình duyệt Chrome không giao diện.
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Chạy ẩn, không hiển thị giao diện
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def send_email(receiver_email, subject, message_body):
    # Gửi email thông báo kết quả.
    try:
        # Lấy thông tin đăng nhập email từ biến môi trường
        sender_email = os.getenv("EMAIL_USER")
        sender_password = os.getenv("EMAIL_PASS")
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        
        if not sender_email or not sender_password:
            logger.error("Thiếu thông tin xác thực email trong file .env")
            return False
            
        # Tạo email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        
        # Thêm nội dung
        msg.attach(MIMEText(message_body, 'html'))
        
        # Kết nối với máy chủ SMTP và gửi email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            
        logger.info(f"Đã gửi email thành công đến {receiver_email}")
        return True
    except Exception as e:
        logger.error(f"Lỗi khi gửi email: {e}")
        return False

def solve_captcha(driver):
 
    # Giải quyết captcha tự động.
    try:
        # Chờ captcha hiển thị
        captcha_img = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "captchaImage"))
        )
        
    # Trong trường hợp thực tế, sẽ cần:
    # 1. Lấy ảnh captcha (screenshot hoặc tải về)
    # 2. Sử dụng dịch vụ giải captcha hoặc OCR
    # 3. Nhập kết quả vào trường nhập
        
        # Yêu cầu người dùng nhập captcha
        captcha_code = input("Vui lòng nhập mã captcha hiển thị: ")
        
        # Nhập mã captcha
        captcha_input = driver.find_element(By.ID, "captchaCode")
        captcha_input.clear()
        captcha_input.send_keys(captcha_code)
        
        return True
    except Exception as e:
        logger.error(f"Lỗi khi giải captcha: {e}")
        return False

def check_traffic_violations(bien_so, loai_phuong_tien, receiver_email=None):
   # Kiểm tra thông tin phạt nguội.
    driver = None
    try:
        logger.info(f"Bắt đầu kiểm tra phạt nguội cho biển số {bien_so}")
        driver = setup_driver()
        
        # Truy cập trang web
        driver.get("https://www.csgt.vn/tra-cuu-phuong-tien-vi-pham.htm")
        logger.info("Đã truy cập trang web CSGT")
        
        # Chờ trang tải xong
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "search-plate"))
        )
        
        # Nhập biển số xe
        search_plate = driver.find_element(By.ID, "search-plate")
        search_plate.clear()
        search_plate.send_keys(bien_so)
        
        # Chọn loại phương tiện
        vehicle_type = Select(driver.find_element(By.ID, "search-type"))
        if loai_phuong_tien == "Ô tô":
            vehicle_type.select_by_value("1")  # Giả sử 1 là ô tô
        else:
            vehicle_type.select_by_value("2")  # Giả sử 2 là xe máy
        
        # Giải captcha
        if not solve_captcha(driver):
            logger.error("Không thể giải captcha")
            return False
        
        # Nhấn nút tìm kiếm
        search_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Tìm kiếm')]")
        search_button.click()
        
        # Chờ kết quả
        time.sleep(3)
        
        # Kiểm tra kết quả
        try:
            result_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "search-results"))
            )
            
            # Lấy nội dung kết quả
            result_text = result_element.text
            logger.info(f"Kết quả tìm kiếm: {result_text}")
            
            # Kiểm tra xem có vi phạm hay không
            if "Không tìm thấy thông tin" in result_text:
                message = f"Biển số {bien_so} không có vi phạm giao thông."
                logger.info(message)
                
                if receiver_email:
                    send_email(
                        receiver_email,
                        f"Thông báo kiểm tra phạt nguội - Biển số {bien_so}",
                        f"<p>{message}</p>"
                    )
                    
                return True
            else:
                # Có vi phạm, lấy chi tiết
                violations = driver.find_elements(By.XPATH, "//table[@class='result-table']//tr[position()>1]")
                
                if not violations:
                    logger.warning("Không tìm thấy chi tiết vi phạm mặc dù có kết quả.")
                    return False
                
                # Tạo HTML cho email
                html_content = f"""
                <h2>Thông báo vi phạm giao thông</h2>
                <p>Biển số xe: <strong>{bien_so}</strong></p>
                <p>Loại phương tiện: <strong>{loai_phuong_tien}</strong></p>
                <table border="1" cellpadding="5" cellspacing="0">
                    <tr>
                        <th>STT</th>
                        <th>Ngày vi phạm</th>
                        <th>Địa điểm</th>
                        <th>Hành vi vi phạm</th>
                        <th>Mức phạt</th>
                    </tr>
                """
                
                for i, violation in enumerate(violations, 1):
                    cells = violation.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 5:
                        html_content += f"""
                        <tr>
                            <td>{i}</td>
                            <td>{cells[0].text}</td>
                            <td>{cells[1].text}</td>
                            <td>{cells[2].text}</td>
                            <td>{cells[3].text}</td>
                        </tr>
                        """
                
                html_content += """
                </table>
                <p>Vui lòng kiểm tra và xử lý các vi phạm trên để tránh bị phạt tăng nặng.</p>
                """
                
                logger.info(f"Tìm thấy {len(violations)} vi phạm cho biển số {bien_so}")
                
                if receiver_email:
                    send_email(
                        receiver_email,
                        f"CẢNH BÁO: Phát hiện vi phạm giao thông - Biển số {bien_so}",
                        html_content
                    )
                
                return True
                
        except TimeoutException:
            logger.error("Không thể tìm thấy kết quả trong thời gian chờ")
            return False
        
    except Exception as e:
        logger.error(f"Lỗi khi kiểm tra phạt nguội: {e}")
        return False
    finally:
        if driver:
            driver.quit()
            logger.info("Đã đóng trình duyệt")

def job(bien_so, loai_phuong_tien, receiver_email):
    # Hàm thực thi công việc kiểm tra định kỳ.
    logger.info(f"Thực hiện kiểm tra định kỳ cho biển số {bien_so}")
    check_traffic_violations(bien_so, loai_phuong_tien, receiver_email)

def main():
    # Lấy tham số từ dòng lệnh
    args = parse_arguments()
    
    # Nếu không có đối số dòng lệnh, lấy từ biến môi trường
    bien_so = args.bien_so or os.getenv("BIEN_SO")
    loai_phuong_tien = args.loai_phuong_tien or os.getenv("LOAI_PHUONG_TIEN", "Ô tô")
    receiver_email = args.email or os.getenv("RECEIVER_EMAIL")
    
    if not bien_so:
        logger.error("Vui lòng cung cấp biển số xe (qua đối số --bien_so hoặc biến môi trường BIEN_SO)")
        return
    
    # Kiểm tra ngay lập tức khi chạy chương trình
    check_traffic_violations(bien_so, loai_phuong_tien, receiver_email)
    
    # Lên lịch chạy tự động
    schedule.every().day.at("06:00").do(job, bien_so, loai_phuong_tien, receiver_email)
    schedule.every().day.at("12:00").do(job, bien_so, loai_phuong_tien, receiver_email)
    
    logger.info("Đã lên lịch kiểm tra tự động lúc 6h sáng và 12h trưa hàng ngày")
    
    # Vòng lặp chính để chạy lịch trình
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Chờ 60 giây trước khi kiểm tra lịch trình tiếp theo
    except KeyboardInterrupt:
        logger.info("Chương trình đã bị ngắt bởi người dùng")

if __name__ == "__main__":
    main()