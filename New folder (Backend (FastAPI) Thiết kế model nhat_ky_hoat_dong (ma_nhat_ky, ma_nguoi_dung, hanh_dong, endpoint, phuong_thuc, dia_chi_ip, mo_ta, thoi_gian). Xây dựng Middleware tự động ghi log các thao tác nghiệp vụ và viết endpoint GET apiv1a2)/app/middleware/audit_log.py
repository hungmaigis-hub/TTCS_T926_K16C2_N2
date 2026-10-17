import logging
from datetime import datetime
from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.models.nguoi_dung import NguoiDung
from app.models.nhat_ky_hoat_dong import NhatKyHoatDong

logger = logging.getLogger("audit_log_middleware")


class AuditLogMiddleware(BaseHTTPMiddleware):
    """
    Middleware tự động ghi log các thao tác nghiệp vụ trong hệ thống
    Tự động trích xuất:
    - dia_chi_ip: Client IP (từ x-forwarded-for hoặc client.host)
    - endpoint: URL path
    - phuong_thuc: HTTP Method (GET, POST, PUT, DELETE, PATCH)
    - ma_nguoi_dung: Trích xuất từ JWT Bearer token nếu có
    - hanh_dong: Suy luận tự động theo nghiệp vụ hoặc lấy từ request.state.audit_action
    - mo_ta: Trạng thái HTTP response và mô tả chi tiết từ request.state.audit_description
    - thoi_gian: Thời điểm thực hiện
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        method = request.method.upper()

        # 1. Bỏ qua các URL tĩnh, swagger docs, health check và OPTIONS preflight
        if method in ["OPTIONS", "HEAD"]:
            return await call_next(request)

        for exclude_path in settings.AUDIT_LOG_EXCLUDE_PATHS:
            if path.startswith(exclude_path):
                return await call_next(request)

        # 2. Xác định người dùng từ Authorization Bearer header nếu có
        user_id: Optional[int] = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = decode_access_token(token)
            if payload:
                # Nếu payload chứa trực tiếp user_id
                user_id = payload.get("user_id")
                # Hoặc tra cứu theo username (sub)
                if not user_id and payload.get("sub"):
                    try:
                        db = SessionLocal()
                        user = db.query(NguoiDung).filter(
                            NguoiDung.ten_dang_nhap == payload.get("sub")
                        ).first()
                        if user:
                            user_id = user.ma_nguoi_dung
                        db.close()
                    except Exception as e:
                        logger.warning(f"Không thể tra cứu user_id từ sub: {e}")

        # Hỗ trợ header test nếu có
        if not user_id:
            test_uid = request.headers.get("X-Test-User-Id")
            if test_uid and test_uid.isdigit():
                user_id = int(test_uid)

        # 3. Lấy địa chỉ IP của Client
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        elif request.client:
            client_ip = request.client.host
        else:
            client_ip = "127.0.0.1"

        # 4. Thực thi endpoint chính
        start_time = datetime.utcnow()
        try:
            response = await call_next(request)
            status_code = response.status_code
            error_message = None
        except Exception as exc:
            status_code = 500
            error_message = str(exc)
            raise exc
        finally:
            # 5. Kiểm tra xem request có cần ghi log hay không
            # Bỏ qua nếu endpoint cố tình gán skip_audit_log
            should_skip = getattr(request.state, "skip_audit_log", False)

            # Quy tắc nghiệp vụ:
            # - Tự động ghi log tất cả các thao tác thay đổi dữ liệu: POST, PUT, DELETE, PATCH
            # - Hoặc các request có gán request.state.audit_action
            # - Hoặc các truy cập nhạy cảm (vd: /api/v1/admin/audit-logs)
            is_modifying_method = method in ["POST", "PUT", "DELETE", "PATCH"]
            is_audit_view = path.startswith("/api/v1/admin/audit-logs") and method == "GET"
            has_explicit_action = hasattr(request.state, "audit_action")

            should_log = (
                not should_skip and (
                    is_modifying_method
                    or is_audit_view
                    or has_explicit_action
                    or settings.AUDIT_LOG_ALL_METHODS
                )
            )

            if should_log:
                try:
                    # Lấy user_id từ state nếu endpoint có gán sau khi decode token
                    if hasattr(request.state, "user_id") and request.state.user_id:
                        user_id = request.state.user_id

                    # Xác định hành động (Action)
                    if hasattr(request.state, "audit_action"):
                        action = request.state.audit_action
                    else:
                        action = self._infer_action(method, path)

                    # Xác định mô tả (Description)
                    custom_desc = getattr(request.state, "audit_description", None)
                    if custom_desc:
                        description = f"[{status_code}] {custom_desc}"
                    elif error_message:
                        description = f"[{status_code}] Lỗi hệ thống: {error_message}"
                    else:
                        description = f"[{status_code}] Thao tác {method} tại {path} ({'Thành công' if status_code < 400 else 'Thất bại'})"

                    # Ghi vào Database
                    self._save_log_to_db(
                        user_id=user_id,
                        action=action,
                        endpoint=path,
                        method=method,
                        ip=client_ip,
                        description=description,
                        timestamp=start_time,
                    )
                except Exception as log_err:
                    # Tuyệt đối không để lỗi ghi log làm gián đoạn response của người dùng
                    logger.error(f"Lỗi khi ghi Audit Log: {log_err}", exc_info=True)

        return response

    def _infer_action(self, method: str, path: str) -> str:
        """
        Tự động suy luận mã hành động chuẩn hóa dựa trên HTTP method và endpoint
        """
        path_lower = path.lower()
        if "login" in path_lower or "dang-nhap" in path_lower:
            return "DANG_NHAP"
        if "logout" in path_lower:
            return "DANG_XUAT"
        if "audit-logs" in path_lower:
            return "XEM_NHAT_KY_HOAT_DONG"
        if "users" in path_lower or "nguoi-dung" in path_lower:
            if method == "POST":
                return "TAO_NGUOI_DUNG"
            elif method in ["PUT", "PATCH"]:
                return "CAP_NHAT_NGUOI_DUNG"
            elif method == "DELETE":
                return "XOA_NGUOI_DUNG"
        if "support-requests" in path_lower or "yeu-cau-ho-tro" in path_lower:
            if method == "POST":
                return "TAO_YEU_CAU_HO_TRO"
            elif method in ["PUT", "PATCH"]:
                return "XU_LY_YEU_CAU_HO_TRO"
        if "notifications" in path_lower or "thong-bao" in path_lower:
            if "read" in path_lower:
                return "DANH_DAU_DOC_THONG_BAO"
            if method == "POST":
                return "GUI_THONG_BAO"
        if "interns" in path_lower or "thuc-tap-sinh" in path_lower:
            if method == "POST":
                return "TAO_HO_SO_THUC_TAP_SINH"
            elif method in ["PUT", "PATCH"]:
                return "CAP_NHAT_HO_SO"
            elif method == "DELETE":
                return "XOA_HO_SO"

        # Fallback tổng quát theo method
        action_map = {
            "POST": "TAO_MOI",
            "PUT": "CAP_NHAT",
            "PATCH": "CHINH_SUA",
            "DELETE": "XOA_DU_LIEU",
            "GET": "TRUY_VAN_DU_LIEU",
        }
        return action_map.get(method, f"THAO_TAC_{method}")

    def _save_log_to_db(
        self,
        user_id: Optional[int],
        action: str,
        endpoint: str,
        method: str,
        ip: str,
        description: str,
        timestamp: datetime,
    ):
        """Lưu bản ghi nhật ký vào database một cách an toàn"""
        db = SessionLocal()
        try:
            log_record = NhatKyHoatDong(
                ma_nguoi_dung=user_id,
                hanh_dong=action,
                endpoint=endpoint,
                phuong_thuc=method,
                dia_chi_ip=ip,
                mo_ta=description,
                thoi_gian=timestamp,
            )
            db.add(log_record)
            db.commit()
        finally:
            db.close()
