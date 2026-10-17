# Script đẩy code lên GitHub & tạo Pull Request vào develop
# Phụ trách: Nguyễn Văn Hiếu

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host " ĐẨY CODE LÊN GITHUB & TẠO PULL REQUEST VÀO NHÁNH DEVELOP" -ForegroundColor Green
Write-Host " Repository: https://github.com/hungmaigis-hub/TTCS_T926_K16C2_N2" -ForegroundColor Yellow
Write-Host " Phụ trách: Nguyễn Văn Hiếu" -ForegroundColor Yellow
Write-Host "=====================================================================" -ForegroundColor Cyan

# 1. Khởi tạo Git nếu chưa có
if (-not (Test-Path ".git")) {
    Write-Host "[1/5] Khởi tạo git repository..." -ForegroundColor Yellow
    git init
    git remote add origin https://github.com/hungmaigis-hub/TTCS_T926_K16C2_N2.git
} else {
    Write-Host "[1/5] Git đã được khởi tạo." -ForegroundColor Green
}

git remote set-url origin https://github.com/hungmaigis-hub/TTCS_T926_K16C2_N2.git

# 2. Tạo nhánh tính năng
Write-Host "[2/5] Tạo và chuyển sang nhánh feature/admin-users-hieu..." -ForegroundColor Yellow
git checkout -B feature/admin-users-hieu

# 3. Add và Commit
Write-Host "[3/5] Thêm file và commit code..." -ForegroundColor Yellow
git add .
git commit -m "feat(admin-users): hoàn thiện endpoint POST /api/v1/admin/users tạo tài khoản người dùng - Nguyễn Văn Hiếu"

# 4. Push lên GitHub
Write-Host "[4/5] Đang đẩy (push) code lên GitHub..." -ForegroundColor Yellow
git push -u origin feature/admin-users-hieu

# 5. Link tạo Pull Request
$prUrl = "https://github.com/hungmaigis-hub/TTCS_T926_K16C2_N2/compare/develop...feature/admin-users-hieu?expand=1"
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "[5/5] ĐÃ PUSH THÀNH CÔNG LÊN GITHUB!" -ForegroundColor Green
Write-Host "Bấm vào đường link sau trên trình duyệt để tạo Pull Request vào nhánh develop:" -ForegroundColor Yellow
Write-Host $prUrl -ForegroundColor White
Write-Host "=====================================================================" -ForegroundColor Cyan

# Mở trình duyệt tự động tới link tạo PR
Start-Process $prUrl
