from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Số thứ tự trang, bắt đầu từ 1")
    page_size: int = Field(default=20, ge=1, le=100, description="Số lượng bản ghi trên mỗi trang")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T] = Field(description="Danh sách dữ liệu của trang hiện tại")
    total: int = Field(description="Tổng số lượng bản ghi thỏa mãn điều kiện lọc")
    page: int = Field(description="Số trang hiện tại")
    page_size: int = Field(description="Số bản ghi mỗi trang")
    total_pages: int = Field(description="Tổng số trang")
