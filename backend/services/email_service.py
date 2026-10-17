import os
import sys
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
    content: str,
    html_content: Optional[str] = None
) -> bool:
    """
    Gửi email qua giao thức SMTP chuẩn.
    Hỗ trợ cả văn bản thuần túy (plain text) và định dạng HTML đa phương tiện.
    Nếu MAIL_ENABLED=false hoặc chưa cấu hình tài khoản, sẽ ghi log và lưu vào sent_emails_history.
    """
    settings = get_email_settings()
    
    email_record = {
        "to_email": to_email,
        "subject": subject,
        "content": content,
        "html_content": html_content,
        "status": "pending"
    }

    # Chế độ mô phỏng khi chưa bật gửi email thực tế
    if not settings["mail_enabled"] or not settings["smtp_user"]:
        logger.info(f"📧 [GIẢ LẬP GỬI MAIL] Đến: {to_email} | Tiêu đề: {subject}")
        email_record["status"] = "simulated"
        sent_emails_history.append(email_record)
        return True

    try:
        if html_content:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = Header(subject, "utf-8")
            msg["From"] = formataddr((str(Header(settings["smtp_from_name"], "utf-8")), settings["smtp_from_email"]))
            msg["To"] = to_email
            
            part_plain = MIMEText(content, "plain", "utf-8")
            part_html = MIMEText(html_content, "html", "utf-8")
            msg.attach(part_plain)
            msg.attach(part_html)
        else:
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


def send_contract_confirmed_email(
    to_email: str,
    intern_name: str,
    contract_id: int,
    sign_date: str,
    internship_status: str = "DangThucTap",
    note: Optional[str] = None
) -> bool:
    """
    Gửi email thông báo ký hợp đồng thực tập thành công và kích hoạt trạng thái thực tập (chạy qua BackgroundTasks).
    """
    subject = f"[Xác nhận] Hợp đồng thực tập #{contract_id} đã ký kết thành công"
    status_label = "Đang thực tập (Chính thức)" if internship_status == "DangThucTap" else internship_status

    body_lines = [
        f"Xin chào {intern_name},",
        "",
        f"Hợp đồng thực tập điện tử mã số #{contract_id} của bạn đã được xác nhận ký kết thành công.",
        f"- Ngày ký: {sign_date}",
        f"- Trạng thái thực tập hiện tại: {status_label}",
    ]

    if note and note.strip():
        body_lines.append(f"- Ghi chú / Mã xác thực: {note.strip()}")

    body_lines.extend([
        "",
        "Chúc bạn có một kỳ thực tập hiệu quả, tích lũy được nhiều kinh nghiệm thực tiễn!",
        "Vui lòng đăng nhập hệ thống để xem chi tiết hợp đồng và phân công nhiệm vụ từ Mentor.",
        "",
        "Trân trọng,",
        "Ban Quản lý Chương trình Thực tập"
    ])

    content = "\n".join(body_lines)
    return send_email_smtp(to_email=to_email, subject=subject, content=content)


def _get_support_request_type_label(request_type: str) -> str:
    """Chuyển mã loại yêu cầu hỗ trợ sang tên tiếng Việt dễ hiểu"""
    mapping = {
        "XinChungNhan": "Xin chứng nhận thực tập",
        "GiayXacNhan": "Giấy xác nhận thực tập",
        "Khac": "Yêu cầu hỗ trợ khác",
    }
    return mapping.get(request_type, request_type)


def send_support_request_email(
    to_email: str,
    intern_name: str,
    request_type: str,
    status: str,
    hr_feedback: Optional[str] = None
) -> bool:
    """
    Gửi email thông báo kết quả xử lý yêu cầu hỗ trợ sinh viên (chạy qua BackgroundTasks).
    """
    req_label = _get_support_request_type_label(request_type)

    if status == "DaXuLy":
        status_label = "ĐÃ ĐƯỢC XỬ LÝ"
        subject = f"[Thông báo] Yêu cầu hỗ trợ '{req_label}' của bạn đã được XỬ LÝ"
    elif status == "TuChoi":
        status_label = "BỊ TỪ CHỐI"
        subject = f"[Thông báo] Yêu cầu hỗ trợ '{req_label}' của bạn đã bị TỪ CHỐI"
    else:
        status_label = status
        subject = f"[Thông báo] Cập nhật tiến độ yêu cầu hỗ trợ '{req_label}'"

    body_lines = [
        f"Xin chào {intern_name},",
        "",
        "Hệ thống Quản lý Thực tập sinh xin thông báo kết quả xử lý yêu cầu hỗ trợ của bạn:",
        f"- Loại yêu cầu: {req_label}",
        f"- Kết quả xử lý: {status_label}",
    ]

    if hr_feedback and hr_feedback.strip():
        body_lines.append(f"- Ghi chú / Phản hồi từ HR: {hr_feedback.strip()}")

    body_lines.extend([
        "",
        "Vui lòng đăng nhập hệ thống để kiểm tra chi tiết hoặc liên hệ phòng Nhân sự nếu cần thêm thông tin.",
        "",
        "Trân trọng,",
        "Phòng Nhân sự / Ban Quản lý Chương trình Thực tập"
    ])

    content = "\n".join(body_lines)
    return send_email_smtp(to_email=to_email, subject=subject, content=content)


def send_meeting_invitation_email(
    to_email: str,
    intern_name: str,
    meeting_title: str,
    start_time: str,
    end_time: str,
    location: str,
    host_name: str,
    note: Optional[str] = None
) -> bool:
    """
    Gửi email HTML tự động mời thực tập sinh tham gia cuộc họp (chạy qua BackgroundTasks).
    """
    subject = f"[Thư mời họp] {meeting_title}"

    # Phiên bản văn bản thuần túy (Plain text)
    plain_lines = [
        f"Xin chào {intern_name},",
        "",
        f"Bạn được mời tham gia cuộc họp: '{meeting_title}'",
        f"- Người chủ trì: {host_name}",
        f"- Thời gian bắt đầu: {start_time}",
        f"- Thời gian kết thúc: {end_time}",
        f"- Địa điểm / Link họp: {location}",
    ]
    if note and note.strip():
        plain_lines.append(f"- Ghi chú / Nội dung: {note.strip()}")
    plain_lines.extend([
        "",
        "Vui lòng sắp xếp thời gian tham gia đúng giờ.",
        "",
        "Trân trọng,",
        "Ban Quản lý Chương trình Thực tập"
    ])
    plain_content = "\n".join(plain_lines)

    # Ghi chú HTML nếu có
    note_html = ""
    if note and note.strip():
        note_html = f"""
        <tr>
            <td style="padding: 10px 14px; font-weight: 600; color: #475569; width: 35%; border-bottom: 1px solid #f1f5f9;">📝 Ghi chú / Nội dung:</td>
            <td style="padding: 10px 14px; color: #1e293b; border-bottom: 1px solid #f1f5f9;">{note.strip()}</td>
        </tr>
        """

    # Template HTML chất lượng cao, responsive và tương thích email client
    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #f8fafc; padding: 30px 10px;">
        <tr>
            <td align="center">
                <table role="presentation" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1); border: 1px solid #e2e8f0;" cellspacing="0" cellpadding="0">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); padding: 32px 24px; text-align: center; color: #ffffff;">
                            <div style="font-size: 32px; margin-bottom: 8px;">📅</div>
                            <h1 style="margin: 0; font-size: 22px; font-weight: 700; letter-spacing: -0.5px;">THƯ MỜI THAM GIA CUỘC HỌP</h1>
                            <p style="margin: 6px 0 0 0; font-size: 14px; opacity: 0.9;">Hệ thống Quản lý Thực tập sinh</p>
                        </td>
                    </tr>
                    <!-- Body Content -->
                    <tr>
                        <td style="padding: 32px 28px;">
                            <p style="margin-top: 0; font-size: 16px; line-height: 1.6; color: #334155;">
                                Xin chào <strong>{intern_name}</strong>,
                            </p>
                            <p style="font-size: 15px; line-height: 1.6; color: #334155;">
                                Bạn vừa nhận được lời mời tham dự cuộc họp từ cán bộ hướng dẫn <strong>{host_name}</strong>. Dưới đây là thông tin chi tiết về buổi họp:
                            </p>
                            
                            <!-- Card chi tiết lịch họp -->
                            <table role="presentation" width="100%" style="background-color: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0; margin: 24px 0; border-collapse: separate; border-spacing: 0;">
                                <tr>
                                    <td colspan="2" style="background-color: #f1f5f9; padding: 12px 14px; font-weight: 700; color: #1e3a8a; border-radius: 8px 8px 0 0; font-size: 15px;">
                                        📌 {meeting_title}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 14px; font-weight: 600; color: #475569; width: 35%; border-bottom: 1px solid #f1f5f9;">👤 Người chủ trì:</td>
                                    <td style="padding: 10px 14px; color: #1e293b; border-bottom: 1px solid #f1f5f9;"><strong>{host_name}</strong></td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 14px; font-weight: 600; color: #475569; border-bottom: 1px solid #f1f5f9;">⏰ Bắt đầu:</td>
                                    <td style="padding: 10px 14px; color: #0284c7; font-weight: 600; border-bottom: 1px solid #f1f5f9;">{start_time}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 14px; font-weight: 600; color: #475569; border-bottom: 1px solid #f1f5f9;">🏁 Kết thúc:</td>
                                    <td style="padding: 10px 14px; color: #0284c7; font-weight: 600; border-bottom: 1px solid #f1f5f9;">{end_time}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 10px 14px; font-weight: 600; color: #475569; border-bottom: 1px solid #f1f5f9;">📍 Địa điểm / Link:</td>
                                    <td style="padding: 10px 14px; color: #1e293b; border-bottom: 1px solid #f1f5f9;"><strong>{location}</strong></td>
                                </tr>
                                {note_html}
                            </table>

                            <div style="background-color: #eff6ff; border-left: 4px solid #3b82f6; padding: 12px 16px; border-radius: 4px; margin-bottom: 24px;">
                                <p style="margin: 0; font-size: 14px; color: #1e40af; line-height: 1.5;">
                                    💡 <em>Vui lòng chuẩn bị tài liệu liên quan và tham gia đúng giờ quy định. Nếu có lịch trùng bất khả kháng, hãy báo lại cho người chủ trì sớm nhất có thể.</em>
                                </p>
                            </div>

                            <p style="font-size: 14px; line-height: 1.6; color: #64748b; margin-bottom: 0;">
                                Trân trọng,<br>
                                <strong style="color: #334155;">Ban Quản lý Chương trình Thực tập</strong>
                            </p>
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f1f5f9; padding: 18px 24px; text-align: center; border-top: 1px solid #e2e8f0; font-size: 12px; color: #64748b;">
                            <p style="margin: 0;">Đây là email tự động gửi từ Hệ thống Quản lý Thực tập sinh. Vui lòng không trả lời trực tiếp email này.</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

    return send_email_smtp(
        to_email=to_email,
        subject=subject,
        content=plain_content,
        html_content=html_content
    )

