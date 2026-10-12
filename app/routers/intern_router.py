"""
Router cho module Intern (thực tập sinh).

Prefix:  /api/v1/interns
Tags:    ["Interns"]

Endpoints hiện tại:
    PATCH /api/v1/interns/{id}/mentor  – Gán / thay đổi / hủy gán Mentor
"""
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.intern import AssignMentorRequest, AssignMentorResponse
from app.services.intern_service import assign_mentor_service

router = APIRouter(
    prefix="/api/v1/interns",
    tags=["Interns"],
)


# ============================================================
# PATCH /api/v1/interns/{id}/mentor
# ============================================================
@router.patch(
    "/{id}/mentor",
    response_model=AssignMentorResponse,
    status_code=status.HTTP_200_OK,
    summary="Gán / Thay đổi Mentor cho thực tập sinh",
    description="""
## Mô tả
Cập nhật trường **`ma_mentor`** trong bảng `ho_so_thuc_tap`.

## Luồng xử lý & Validation

1. **Tìm hồ sơ thực tập** theo `{id}` (tức `ma_ho_so`).  
   → `404` nếu không tồn tại.

2. **Nếu `ma_mentor` ≠ null**, kiểm tra người được gán:  
   - Phải **tồn tại** trong bảng `nguoi_dung`.  
     → `404` nếu không tìm thấy.  
   - Phải có **`vai_tro = 'Mentor'`**.  
     → `422` nếu sai vai trò.  
   - Tài khoản phải đang **kích hoạt** (`kich_hoat = true`).  
     → `403` nếu bị vô hiệu hóa.

3. Cập nhật `ma_mentor` và `ngay_cap_nhat` vào DB.

4. Trả về thông tin hồ sơ và Mentor đã gán.

## Hủy gán Mentor
Truyền `"ma_mentor": null` trong body để **xóa** mentor hiện tại.

## HTTP Status Codes
| Code | Ý nghĩa |
|------|---------|
| 200  | Thành công |
| 404  | Không tìm thấy hồ sơ hoặc mentor |
| 422  | Người dùng không có vai trò Mentor |
| 403  | Tài khoản Mentor bị vô hiệu hóa |
| 500  | Lỗi server |
""",
    responses={
        200: {
            "description": "Gán Mentor thành công",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Gán Mentor 'Nguyễn Thị Lan' cho hồ sơ 'HS001' thành công.",
                        "data": {
                            "ho_so": {
                                "ma_ho_so": "HS001",
                                "ho_ten": "Trần Văn An",
                                "email": "an.tran@university.edu.vn",
                                "vi_tri_thuc_tap": "Backend Developer",
                                "trang_thai": "DaDuyet",
                            },
                            "mentor": {
                                "ma_mentor": "MENTOR01",
                                "ho_ten": "Nguyễn Thị Lan",
                                "email": "lan.nguyen@company.com",
                                "so_dien_thoai": "0901234567",
                            },
                            "ngay_cap_nhat": "2024-10-07T11:39:49",
                        },
                    }
                }
            },
        },
        404: {
            "description": "Hồ sơ thực tập hoặc Mentor không tồn tại",
            "content": {
                "application/json": {
                    "examples": {
                        "intern_not_found": {
                            "summary": "Hồ sơ thực tập không tồn tại",
                            "value": {
                                "detail": {
                                    "error_code": "INTERN_NOT_FOUND",
                                    "message": "Không tìm thấy hồ sơ thực tập với mã 'HS999'.",
                                    "field": "id",
                                }
                            },
                        },
                        "mentor_not_found": {
                            "summary": "Mentor không tồn tại",
                            "value": {
                                "detail": {
                                    "error_code": "MENTOR_NOT_FOUND",
                                    "message": "Không tìm thấy người dùng với mã 'MENTOR99' trong hệ thống.",
                                    "field": "ma_mentor",
                                }
                            },
                        },
                    }
                }
            },
        },
        422: {
            "description": "Người dùng không có vai trò Mentor",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error_code": "INVALID_MENTOR_ROLE",
                            "message": "Người dùng 'HR01' có vai trò 'HR', không phải 'Mentor'.",
                            "field": "ma_mentor",
                        }
                    }
                }
            },
        },
        403: {
            "description": "Tài khoản Mentor bị vô hiệu hóa",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error_code": "MENTOR_INACTIVE",
                            "message": "Tài khoản của Mentor 'MENTOR02' đã bị vô hiệu hóa, không thể gán.",
                            "field": "ma_mentor",
                        }
                    }
                }
            },
        },
    },
)
def assign_mentor(
    id: str = Path(
        ...,
        title="Mã hồ sơ thực tập",
        description="Mã định danh của hồ sơ thực tập (ma_ho_so)",
        examples="HS001",
    ),
    body: AssignMentorRequest = ...,
    db: Session = Depends(get_db),
) -> AssignMentorResponse:
    """
    **PATCH /api/v1/interns/{id}/mentor**

    Gán hoặc thay đổi Mentor cho hồ sơ thực tập có mã `{id}`.

    - Truyền `ma_mentor` hợp lệ để gán Mentor mới.
    - Truyền `ma_mentor: null` để hủy gán Mentor hiện tại.
    """
    return assign_mentor_service(
        intern_id=id,
        ma_mentor=body.ma_mentor,
        db=db,
    )
