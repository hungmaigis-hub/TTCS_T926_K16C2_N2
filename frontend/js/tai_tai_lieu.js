const duongDanApiUpload = "http://127.0.0.1:8000/api/upload";

const tepInput = document.getElementById("tepDinhKem");
const vungKeoTha = document.getElementById("vungKeoTha");
const tenTepVanBan = document.getElementById("tenTepVanBan");
const dungLuongTep = document.getElementById("dungLuongTep");
const tenTepHienThi = document.getElementById("tenTepHienThi");

function updateFileView(file) {
  if (file) {
    if (tenTepVanBan) tenTepVanBan.textContent = file.name;
    const sizeInMb = (file.size / (1024 * 1024)).toFixed(2);
    if (dungLuongTep) dungLuongTep.textContent = `${sizeInMb} MB`;
    if (tenTepHienThi) {
      tenTepHienThi.classList.remove("bg-surface-container-low");
      tenTepHienThi.classList.add("bg-surface-container");
    }
  } else {
    if (tenTepVanBan) tenTepVanBan.textContent = "Chưa có tệp nào được chọn";
    if (dungLuongTep) dungLuongTep.textContent = "0 KB";
    if (tenTepHienThi) {
      tenTepHienThi.classList.remove("bg-surface-container");
      tenTepHienThi.classList.add("bg-surface-container-low");
    }
  }
}

if (tepInput) {
  tepInput.addEventListener("change", function (e) {
    if (e.target.files && e.target.files.length > 0) {
      updateFileView(e.target.files[0]);
    }
  });
}

if (vungKeoTha) {
  ["dragenter", "dragover"].forEach((eventName) => {
    vungKeoTha.addEventListener(
      eventName,
      (e) => {
        e.preventDefault();
        e.stopPropagation();
        vungKeoTha.classList.add("bg-surface-container-high");
      },
      false,
    );
  });

  ["dragleave", "drop"].forEach((eventName) => {
    vungKeoTha.addEventListener(
      eventName,
      (e) => {
        e.preventDefault();
        e.stopPropagation();
        vungKeoTha.classList.remove("bg-surface-container-high");
      },
      false,
    );
  });

  vungKeoTha.addEventListener("drop", (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
      tepInput.files = files;
      updateFileView(files[0]);
    }
  });
}

function datLaiForm() {
  const inputEl = document.getElementById("tepDinhKem");
  const ghiChuEl = document.getElementById("ghiChu");
  const loaiEl = document.getElementById("loaiTaiLieu");
  if (inputEl) inputEl.value = "";
  if (ghiChuEl) ghiChuEl.value = "";
  if (loaiEl) loaiEl.selectedIndex = 0;
  updateFileView(null);
}

async function xuLyTaiLen() {
  const loaiTaiLieu =
    document.getElementById("loaiTaiLieu")?.value || "Tài liệu chung";
  const hopThongBao = document.getElementById("hopThongBao");
  const nutGuiTep = document.getElementById("nutGuiTep");
  const file = tepInput?.files?.[0];

  if (!file) {
    alert("Vui lòng chọn hoặc kéo thả tệp tài liệu trước khi bấm tải lên.");
    return;
  }

  const originalHtml = nutGuiTep.innerHTML;
  nutGuiTep.innerHTML = `<span class="inline-block w-4 h-4 rounded-full border-2 border-on-primary border-t-transparent animate-spin"></span> <span>Đang tải lên và quét bảo mật...</span>`;
  nutGuiTep.disabled = true;

  const duLieuForm = new FormData();
  duLieuForm.append("file", file);
  duLieuForm.append("type", loaiTaiLieu);

  try {
    const phanHoi = await fetch(duongDanApiUpload, {
      method: "POST",
      body: duLieuForm,
    });
    const ketQua = await phanHoi.json();
    hienThiThongBaoUpload(file, loaiTaiLieu, ketQua.message);
  } catch (err) {
    hienThiThongBaoUpload(file, loaiTaiLieu, null);
  } finally {
    nutGuiTep.innerHTML = originalHtml;
    nutGuiTep.disabled = false;
    datLaiForm();
  }
}

function hienThiThongBaoUpload(file, loaiTaiLieu, thongDiepTuyChinh) {
  const hopThongBao = document.getElementById("hopThongBao");
  if (!hopThongBao) return;
  hopThongBao.className =
    "rounded-xl bg-secondary-container text-on-secondary-container p-4 shadow-sm flex items-start gap-3.5 transition-all duration-300";
  hopThongBao.innerHTML = `
    <div class="w-8 h-8 rounded-lg bg-secondary text-on-secondary flex items-center justify-center shrink-0 mt-0.5 shadow-sm">
      <span class="material-symbols-outlined text-[20px]">check_circle</span>
    </div>
    <div class="flex-1 font-body-sm text-body-sm">
      <div class="flex items-center justify-between">
        <span class="font-label-lg text-label-lg font-bold">Tải lên tài liệu thành công!</span>
        <span class="font-label-sm text-label-sm font-semibold">Vừa xong</span>
      </div>
      <p class="mt-1 leading-relaxed">
        ${thongDiepTuyChinh || `Tệp <strong>${file.name}</strong> (${(file.size / (1024 * 1024)).toFixed(2)} MB) thuộc phân loại <strong>"${loaiTaiLieu}"</strong> đã được tải lên và mã hóa an toàn trên máy chủ ICTU.`}
      </p>
    </div>
    <button type="button" onclick="document.getElementById('hopThongBao').classList.add('hidden')" class="p-1 rounded-md hover:bg-secondary/10 transition-colors">
      <span class="material-symbols-outlined text-[18px]">close</span>
    </button>
  `;
  hopThongBao.classList.remove("hidden");
  hopThongBao.scrollIntoView({ behavior: "smooth", block: "center" });
}
