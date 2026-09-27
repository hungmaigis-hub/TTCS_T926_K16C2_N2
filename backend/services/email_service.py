import os
import sys
import smtplib
import logging
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from typing import Optional, List, Dict, Any

from dotenv import load_dotenv
from pathlib import Path

# Cấu hình logging
logger = logging.getLogger("email_service")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [EmailService]: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Lưu lịch sử email đã gửi trong phiên (phục vụ kiểm thử và debug)
sent_emails_history: List[Dict[str, Any]] = []

def get_email_settings() -> Dict[str, Any]:
    """Đọc cấu hình gửi email từ biến môi trường (tự động load từ .env)"""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(dotenv_path=env_path, override=False)

    # Nếu đang chạy pytest tự động, mặc định không gửi email thật ra ngoài
    if "pytest" in sys.modules and os.getenv("TEST_USE_REAL_EMAIL") != "true":
        mail_enabled_val = os.getenv("MAIL_ENABLED", "false").strip().lower()
    else:
        mail_enabled_val = os.getenv("MAIL_ENABLED", "false").strip().lower()

    mail_enabled = mail_enabled_val in ("1", "true", "yes", "on")
    
    return {
        "mail_enabled": mail_enabled,
        "smtp_host": os.getenv("SMTP_HOST", "smtp.gmail.com").strip(),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "smtp_user": os.getenv("SMTP_USER", "").strip(),
        "smtp_password": os.getenv("SMTP_PASSWORD", "").strip(),
        "smtp_from_email": os.getenv("SMTP_FROM_EMAIL", "no-reply@internship.local").strip(),
        "smtp_from_name": os.getenv("SMTP_FROM_NAME", "Hệ thống Quản lý Thực tập sinh").strip(),
    }


def send_email_smtp(
    to_email: str,
    subject: str,
    content: str
) -> bool:
    """
    Gửi email văn bản thuần túy (plain text) qua giao thức SMTP chuẩn.
    Nếu MAIL_ENABLED=false hoặc chưa cấu hình tài khoản, sẽ ghi log và lưu vào sent_emails_history.
    """
    settings = get_email_settings()
    
    email_record = {
        "to_email": to_email,
        "subject": subject,
        "content": content,
        "status": "pending"
    }

    # Chế độ mô phỏng khi chưa bật gửi email thực tế
    if not settings["mail_enabled"] or not settings["smtp_user"]:
        logger.info(f"📧 [GIẢ LẬP GỬI MAIL] Đến: {to_email} | Tiêu đề: {subject}")
        email_record["status"] = "simulated"
        sent_emails_history.append(email_record)
        return True

    try:
        msg = MIMEText(content, "plain", "utf-8")
        msg["Subject"] = Header(subject, "utf-8")
        msg["From"] = formataddr((str(Header(settings["smtp_from_name"], "utf-8")), settings["smtp_from_email"]))
        msg["To"] = to_email

        # Envelope sender phải là tài khoản đăng nhập SMTP để Gmail không từ chối kết nối
        sender_email = settings["smtp_user"] if settings["smtp_user"] else settings["smtp_from_email"]

        with smtplib.SMTP(settings["smtp_host"], settings["smtp_port"], timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(settings["smtp_user"], settings["smtp_password"])
            server.sendmail(sender_email, [to_email], msg.as_string())

        logger.info(f"✅ Gửi email thực tế thành công tới {to_email} | Tiêu đề: {subject}")
        email_record["status"] = "sent"
        sent_emails_history.append(email_record)
        return True

    except Exception as exc:
        logger.error(f"❌ Lỗi gửi email tới {to_email}: {str(exc)}")
        email_record["status"] = "failed"
        email_record["error"] = str(exc)
        sent_emails_history.append(email_record)
        return False


def _get_document_type_label(document_type: str) -> str:
    """Chuyển mã loại tài liệu sang tên tiếng Việt dễ hiểu"""
    mapping = {
        "CV": "Hồ sơ năng lực (CV)",
        "DonXinThucTap": "Đơn xin thực tập",
        "GiayGioiThieu": "Giấy giới thiệu từ nhà trường",
        "BangDiem": "Bảng điểm học tập",
        "ChungChi": "Chứng chỉ / Bằng cấp liên quan"
    }
    return mapping.get(document_type, document_type)


def send_document_approval_email(
    to_email: str,
    intern_name: str,
    document_type: str,
    status: str,
    note: Optional[str] = None
) -> bool:
    """
    Gửi email thông báo kết quả duyệt tài liệu thực tập sinh (chạy qua BackgroundTasks).
    """
    doc_label = _get_document_type_label(document_type)

    if status == "DaDuyet":
        status_label = "ĐÃ PHÊ DUYỆT"
        subject = f"[Thông báo] Tài liệu '{doc_label}' của bạn đã được PHÊ DUYỆT"
    elif status == "TuChoi":
        status_label = "BỊ TỪ CHỐI"
        subject = f"[Thông báo] Kết quả xét duyệt: Tài liệu '{doc_label}' đã bị TỪ CHỐI"
    else:
        status_label = "CHỜ DUYỆT"
        subject = f"[Thông báo] Tài liệu '{doc_label}' chuyển sang trạng thái CHỜ DUYỆT"

    body_lines = [
        f"Xin chào {intern_name},",
        "",
        "Hệ thống Quản lý Thực tập sinh xin thông báo kết quả xét duyệt tài liệu của bạn:",
        f"- Loại tài liệu: {doc_label}",
        f"- Kết quả duyệt: {status_label}",
    ]

    if note and note.strip():
        body_lines.append(f"- Ghi chú / Nhận xét: {note.strip()}")

    body_lines.extend([
        "",
        "Vui lòng đăng nhập hệ thống để xem chi tiết hoặc thực hiện các bước tiếp theo.",
        "",
        "Trân trọng,",
        "Ban Quản lý Chương trình Thực tập"
    ])

    content = "\n".join(body_lines)
    return send_email_smtp(to_email=to_email, subject=subject, content=content)


def send_profile_approval_email(
    to_email: str,
    intern_name: str,
    program_name: Optional[str],
    status: str,
    note: Optional[str] = None
) -> bool:
    """
    Gửi email thông báo kết quả xét duyệt hồ sơ thực tập sinh (chạy qua BackgroundTasks).
    """
    prog_label = program_name if program_name else "Chương trình thực tập"

    if status == "DaDuyet":
        status_label = "ĐÃ PHÊ DUYỆT"
        subject = f"[Chúc mừng] Hồ sơ tham gia '{prog_label}' của bạn đã được PHÊ DUYỆT"
    elif status == "TuChoi":
        status_label = "BỊ TỪ CHỐI"
        subject = f"[Thông báo] Kết quả xét duyệt: Hồ sơ '{prog_label}' chưa đạt yêu cầu"
    else:
        status_label = "CHỜ DUYỆT"
        subject = f"[Thông báo] Hồ sơ '{prog_label}' chuyển sang trạng thái CHỜ DUYỆT"

    body_lines = [
        f"Xin chào {intern_name},",
        "",
        "Hệ thống Quản lý Thực tập sinh xin thông báo kết quả xét duyệt hồ sơ thực tập:",
        f"- Chương trình: {prog_label}",
        f"- Kết quả duyệt: {status_label}",
    ]

    if note and note.strip():
        body_lines.append(f"- Ghi chú / Nhận xét: {note.strip()}")

    body_lines.extend([
        "",
        "Trân trọng,",
        "Ban Quản lý Chương trình Thực tập"
    ])

    content = "\n".join(body_lines)
    return send_email_smtp(to_email=to_email, subject=subject, content=content)
