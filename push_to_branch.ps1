Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host "  DAY CODE LEN GITHUB CHO NGUYEN VAN HIEU (NHANH RIENG)" -ForegroundColor Green
Write-Host "  Repo: https://github.com/hungmaigis-hub/TTCS_T926_K16C2_N2" -ForegroundColor Yellow
Write-Host "===============================================================" -ForegroundColor Cyan

# 1. Bật longpaths
git config --global core.longpaths true
git config core.longpaths true

# 2. Thêm file và commit
git add app tests requirements.txt README.md .env.example .gitignore
git commit -m "feat(backend): thiet ke model yeu_cau_ho_tro va endpoint POST /api/v1/support-requests - Nguyen Van Hieu"

# 3. Tạo nhánh riêng 'nguyen-van-hieu'
git branch -M nguyen-van-hieu
git remote remove origin 2>$null
git remote add origin https://github.com/hungmaigis-hub/TTCS_T926_K16C2_N2.git

# 4. Đẩy thẳng lên nhánh nguyen-van-hieu
Write-Host "`nĐang đẩy mã nguồn lên nhánh 'nguyen-van-hieu' trên GitHub..." -ForegroundColor Cyan
git push -u origin nguyen-van-hieu --force

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n===============================================================" -ForegroundColor Green
    Write-Host "  THANH CONG 100%! MA NGUON DA DUOC DAY LEN GITHUB!" -ForegroundColor Green
    Write-Host "  Nhanh: nguyen-van-hieu" -ForegroundColor Yellow
    Write-Host "  Link repo: https://github.com/hungmaigis-hub/TTCS_T926_K16C2_N2/tree/nguyen-van-hieu" -ForegroundColor Cyan
    Write-Host "===============================================================" -ForegroundColor Green
} else {
    Write-Host "`nNeu gap loi ve quyen (Permission/Authentication), hay kiem tra tai khoan GitHub cua ban da duoc add Collaborator vao repo nhom chua nhe!" -ForegroundColor Red
}
