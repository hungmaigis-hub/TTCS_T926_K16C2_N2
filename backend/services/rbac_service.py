"""
Module RBAC Service & Permission Dependency
Xử lý quản lý danh mục quyền hạn, phân quyền theo vai trò (Role-Based Access Control)
và Dependency require_permissions cho FastAPI.
"""
from typing import List, Union, Optional
from fastapi import HTTPException, status, Header, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from database.models.nguoi_dung import NguoiDung
from database.models.quyen_han import QuyenHan, VaiTroQuyenHan

# Danh mục các quyền hạn mặc định trong hệ thống
DEFAULT_PERMISSIONS = [
    # Quản lý Thực tập sinh
    {
        "ma_quyen": "intern:read",
        "ten_quyen": "Xem danh sách và hồ sơ thực tập sinh",
        "mo_ta": "Cho phép truy cập thông tin chi tiết và danh sách sinh viên thực tập",
        "nhom_quyen": "ThucTapSinh",
    },
    {
        "ma_quyen": "intern:create",
        "ten_quyen": "Thêm mới thực tập sinh",
        "mo_ta": "Cho phép tạo mới hoặc import hồ sơ thực tập sinh vào hệ thống",
        "nhom_quyen": "ThucTapSinh",
    },
    {
        "ma_quyen": "intern:update",
        "ten_quyen": "Cập nhật thông tin thực tập sinh",
        "mo_ta": "Cho phép sửa hồ sơ, phân công mentor hoặc đổi trạng thái thực tập",
        "nhom_quyen": "ThucTapSinh",
    },
    {
        "ma_quyen": "intern:delete",
        "ten_quyen": "Xóa hồ sơ thực tập sinh",
        "mo_ta": "Cho phép xóa hoặc đưa hồ sơ vào trạng thái thôi học",
        "nhom_quyen": "ThucTapSinh",
    },
    # Quản lý Nhiệm vụ
    {
        "ma_quyen": "task:read",
        "ten_quyen": "Xem danh sách công việc và nhiệm vụ",
        "mo_ta": "Cho phép tra cứu công việc được giao hoặc danh sách task của nhóm",
        "nhom_quyen": "NhiemVu",
    },
    {
        "ma_quyen": "task:create",
        "ten_quyen": "Giao nhiệm vụ cho thực tập sinh",
        "mo_ta": "Cho phép tạo task mới và phân công người thực hiện",
        "nhom_quyen": "NhiemVu",
    },
    {
        "ma_quyen": "task:update",
        "ten_quyen": "Cập nhật tiến độ nhiệm vụ",
        "mo_ta": "Cho phép đổi trạng thái tiến độ công việc hoặc duyệt hoàn thành",
        "nhom_quyen": "NhiemVu",
    },
    # Quản lý Báo cáo & Đánh giá
    {
        "ma_quyen": "report:read",
        "ten_quyen": "Xem báo cáo thực tập tuần",
        "mo_ta": "Cho phép đọc nội dung báo cáo nộp định kỳ của sinh viên",
        "nhom_quyen": "BaoCao",
    },
    {
        "ma_quyen": "report:feedback",
        "ten_quyen": "Đánh giá và nhận xét báo cáo tuần",
        "mo_ta": "Cho phép gửi phản hồi nhận xét và chấm điểm báo cáo tuần",
        "nhom_quyen": "BaoCao",
    },
    {
        "ma_quyen": "evaluation:create",
        "ten_quyen": "Đánh giá kết quả cuối kỳ thực tập",
        "mo_ta": "Cho phép lập bảng điểm và nhận xét tổng kết cho sinh viên",
        "nhom_quyen": "BaoCao",
    },
    # Quản lý Điểm danh & Nghỉ phép
    {
        "ma_quyen": "attendance:scan",
        "ten_quyen": "Quét mã điểm danh và chấm công",
        "mo_ta": "Cho phép ghi nhận check-in, check-out và điểm danh trực tiếp",
        "nhom_quyen": "ChamCong",
    },
    {
        "ma_quyen": "leave:approve",
        "ten_quyen": "Xét duyệt đơn xin nghỉ phép",
        "mo_ta": "Cho phép phê duyệt hoặc từ chối đơn xin nghỉ phép của thực tập sinh",
        "nhom_quyen": "ChamCong",
    },
    # Quản lý Lịch họp
    {
        "ma_quyen": "meeting:create",
        "ten_quyen": "Tạo và chủ trì lịch họp",
        "mo_ta": "Cho phép lên lịch họp trực tuyến/trực tiếp và mời người tham gia",
        "nhom_quyen": "LichHop",
    },
    # Quản lý Hỗ trợ sinh viên
    {
        "ma_quyen": "support:process",
        "ten_quyen": "Tiếp nhận và xử lý yêu cầu hỗ trợ",
        "mo_ta": "Cho phép phản hồi, xử lý giấy xác nhận, chứng nhận thực tập",
        "nhom_quyen": "HoTro",
    },
    # Quản trị Hệ thống & Phân quyền
    {
        "ma_quyen": "role:manage",
        "ten_quyen": "Quản trị vai trò và phân quyền hệ thống",
        "mo_ta": "Cho phép xem danh mục quyền, phân quyền vai trò cho người dùng",
        "nhom_quyen": "HeThong",
    },
    {
        "ma_quyen": "system:config",
        "ten_quyen": "Cấu hình tham số hệ thống và tích hợp HRM",
        "mo_ta": "Cho phép quản trị thiết lập hệ thống và kết nối ngoại vi",
        "nhom_quyen": "HeThong",
    },
]

# Gán quyền mặc định cho từng vai trò cơ bản
DEFAULT_ROLE_PERMISSIONS_MAPPING = {
    "Admin": [p["ma_quyen"] for p in DEFAULT_PERMISSIONS],
    "HR": [
        "intern:read", "intern:create", "intern:update", "intern:delete",
        "leave:approve", "support:process", "attendance:scan", "meeting:create", "role:manage"
    ],
    "Mentor": [
        "intern:read", "task:read", "task:create", "task:update",
        "report:read", "report:feedback", "evaluation:create", "meeting:create"
    ],
    "ThucTapSinh": [
        "task:read", "task:update", "report:read"
    ],
    "NhaTruong": [
        "intern:read", "report:read"
    ]
}


def seed_default_permissions_and_roles(db: Session) -> None:
    """Khởi tạo danh mục quyền hạn và gán quyền ban đầu cho các vai trò nếu chưa có."""
    try:
        # 1. Đảm bảo tất cả quyền mặc định đã tồn tại
        for item in DEFAULT_PERMISSIONS:
            existing = db.query(QuyenHan).filter(QuyenHan.ma_quyen == item["ma_quyen"]).first()
            if not existing:
                perm = QuyenHan(
                    ma_quyen=item["ma_quyen"],
                    ten_quyen=item["ten_quyen"],
                    mo_ta=item.get("mo_ta"),
                    nhom_quyen=item.get("nhom_quyen", "HeThong")
                )
                db.add(perm)
        db.commit()

        # 2. Gán quyền mặc định cho các vai trò nếu vai trò đó chưa có bất kỳ quyền nào
        for role, perm_codes in DEFAULT_ROLE_PERMISSIONS_MAPPING.items():
            count = db.query(VaiTroQuyenHan).filter(VaiTroQuyenHan.vai_tro == role).count()
            if count == 0:
                perms = db.query(QuyenHan).filter(QuyenHan.ma_quyen.in_(perm_codes)).all()
                for p in perms:
                    mapping = VaiTroQuyenHan(vai_tro=role, ma_quyen_han=p.ma_quyen_han)
                    db.add(mapping)
        db.commit()
    except Exception:
        db.rollback()


def get_all_permissions(db: Session) -> List[QuyenHan]:
    """Lấy danh mục tất cả quyền hạn có trong hệ thống."""
    seed_default_permissions_and_roles(db)
    return db.query(QuyenHan).order_by(QuyenHan.nhom_quyen, QuyenHan.ma_quyen).all()


def get_role_permissions(role: str, db: Session) -> List[QuyenHan]:
    """Lấy danh sách quyền hạn đã được gán cho một vai trò."""
    seed_default_permissions_and_roles(db)
    perms = (
        db.query(QuyenHan)
        .join(VaiTroQuyenHan, VaiTroQuyenHan.ma_quyen_han == QuyenHan.ma_quyen_han)
        .filter(VaiTroQuyenHan.vai_tro == role.strip())
        .order_by(QuyenHan.nhom_quyen, QuyenHan.ma_quyen)
        .all()
    )
    return perms


def update_role_permissions(
    role: str,
    permissions_input: List[Union[str, int]],
    db: Session
) -> List[QuyenHan]:
    """
    Cập nhật toàn diện danh sách quyền hạn cho vai trò.
    Hỗ trợ nhận danh sách mã quyền dạng string (VD: 'intern:read') hoặc integer ID (VD: 1, 2).
    """
    clean_role = role.strip()
    if not clean_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên vai trò không được để trống"
        )

    # Đảm bảo danh mục quyền đã có
    seed_default_permissions_and_roles(db)

    # Tách chuỗi và số nguyên
    code_inputs = [str(p).strip() for p in permissions_input if isinstance(p, str)]
    id_inputs = [int(p) for p in permissions_input if isinstance(p, int) or (isinstance(p, str) and p.strip().isdigit())]

    # Tìm các quyền khớp
    matched_perms: List[QuyenHan] = []
    if code_inputs or id_inputs:
        matched_perms = db.query(QuyenHan).filter(
            (QuyenHan.ma_quyen.in_(code_inputs)) | (QuyenHan.ma_quyen_han.in_(id_inputs))
        ).all()

    # Kiểm tra xem có quyền nào không hợp lệ / không tìm thấy không
    found_codes = {p.ma_quyen for p in matched_perms}
    found_ids = {p.ma_quyen_han for p in matched_perms}

    invalid_items = []
    for p in permissions_input:
        if isinstance(p, int) and p not in found_ids:
            invalid_items.append(str(p))
        elif isinstance(p, str):
            p_str = p.strip()
            if p_str.isdigit() and int(p_str) in found_ids:
                continue
            if p_str not in found_codes:
                invalid_items.append(p_str)

    if invalid_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Các quyền hạn sau không tồn tại trong hệ thống: {', '.join(invalid_items)}"
        )

    # Xóa các quyền hiện tại của vai trò này
    db.query(VaiTroQuyenHan).filter(VaiTroQuyenHan.vai_tro == clean_role).delete()

    # Chèn danh sách quyền mới (loại bỏ trùng lặp nếu có)
    seen_ids = set()
    for q in matched_perms:
        if q.ma_quyen_han not in seen_ids:
            mapping = VaiTroQuyenHan(vai_tro=clean_role, ma_quyen_han=q.ma_quyen_han)
            db.add(mapping)
            seen_ids.add(q.ma_quyen_han)

    db.commit()

    # Lấy lại danh sách quyền vừa cập nhật
    return (
        db.query(QuyenHan)
        .join(VaiTroQuyenHan, VaiTroQuyenHan.ma_quyen_han == QuyenHan.ma_quyen_han)
        .filter(VaiTroQuyenHan.vai_tro == clean_role)
        .order_by(QuyenHan.nhom_quyen, QuyenHan.ma_quyen)
        .all()
    )


from fastapi import Request

def require_permissions(*required_perms: str):
    """
    FastAPI Dependency Factory kiểm tra quyền truy cập dựa trên RBAC.
    - Xác thực người dùng qua header X-User-Email, X-User-Id hoặc Bearer Token.
    - Kiểm tra trạng thái tài khoản (chặn tài khoản Khoa).
    - Superadmin: vai trò Admin được bypass toàn bộ quyền hạn.
    - Kiểm tra vai trò của người dùng có đầy đủ các quyền yêu cầu trong required_perms hay không.
    """
    def permission_checker(
        request: Request,
        db: Session = Depends(get_db)
    ) -> NguoiDung:
        # Đảm bảo bảng phân quyền đã có dữ liệu mẫu
        seed_default_permissions_and_roles(db)

        # 1. Trích xuất thông tin định danh từ headers (hỗ trợ case-insensitive)
        headers = request.headers
        x_user_email = headers.get("x-user-email") or headers.get("X-User-Email")
        x_user_id_raw = headers.get("x-user-id") or headers.get("X-User-Id")
        authorization = headers.get("authorization") or headers.get("Authorization")

        user = None
        if x_user_id_raw and str(x_user_id_raw).strip().isdigit():
            user = db.query(NguoiDung).filter(NguoiDung.ma_nguoi_dung == int(str(x_user_id_raw).strip())).first()
        elif x_user_email and x_user_email.strip():
            user = db.query(NguoiDung).filter(NguoiDung.email == x_user_email.strip().lower()).first()
        elif authorization and authorization.strip():
            token_val = authorization.replace("Bearer ", "").replace("bearer ", "").strip()
            if "@" in token_val:
                user = db.query(NguoiDung).filter(NguoiDung.email == token_val.lower()).first()
            elif token_val.isdigit():
                user = db.query(NguoiDung).filter(NguoiDung.ma_nguoi_dung == int(token_val)).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Yêu cầu đăng nhập hoặc cung cấp thông tin xác thực (X-User-Email hoặc X-User-Id)"
            )

        # 2. Kiểm tra trạng thái tài khoản
        if user.trang_thai and user.trang_thai.lower() in ["khoa", "locked", "disabled", "inactive"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản của bạn đã bị khóa. Vui lòng liên hệ quản trị viên."
            )

        # 3. Superadmin bypass: vai trò Admin có toàn bộ quyền hạn
        if user.vai_tro and user.vai_tro.strip().lower() == "admin":
            return user

        # 4. Nếu endpoint không yêu cầu quyền cụ thể nào
        if not required_perms:
            return user

        # 5. Tra cứu danh sách quyền mà vai trò này sở hữu
        user_role = user.vai_tro.strip() if user.vai_tro else ""
        role_perms = (
            db.query(QuyenHan.ma_quyen)
            .join(VaiTroQuyenHan, VaiTroQuyenHan.ma_quyen_han == QuyenHan.ma_quyen_han)
            .filter(VaiTroQuyenHan.vai_tro == user_role)
            .all()
        )
        granted_codes = {p[0] for p in role_perms}

        missing = [p for p in required_perms if p not in granted_codes]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Quyền truy cập bị từ chối. Vai trò '{user_role}' thiếu quyền: {', '.join(missing)}"
            )

        return user

    return permission_checker
