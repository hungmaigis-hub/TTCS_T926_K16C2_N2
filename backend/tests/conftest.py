import os
import pytest

@pytest.fixture(autouse=True)
def setup_test_mail_env(monkeypatch):
    """Mặc định khi chạy test sẽ dùng chế độ giả lập để test chạy nhanh và không gửi mail rác"""
    # Chỉ set nếu test case không tự định nghĩa MAIL_ENABLED riêng
    if "MAIL_ENABLED" not in os.environ or os.environ.get("MAIL_ENABLED") == "true":
        monkeypatch.setenv("MAIL_ENABLED", "false")
