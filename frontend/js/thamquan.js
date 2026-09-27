const boNhoAmThanh = {
  nguCanh: null,
};

function phatAmThanhDiChuyen() {
  try {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;
    if (!boNhoAmThanh.nguCanh) {
      boNhoAmThanh.nguCanh = new AudioCtx();
    }
    const ctx = boNhoAmThanh.nguCanh;
    if (ctx.state === "suspended") {
      ctx.resume();
    }
    const daoDong = ctx.createOscillator();
    const boKhuechDai = ctx.createGain();
    daoDong.type = "sine";
    daoDong.frequency.setValueAtTime(160, ctx.currentTime);
    daoDong.frequency.exponentialRampToValueAtTime(420, ctx.currentTime + 0.16);
    boKhuechDai.gain.setValueAtTime(0.18, ctx.currentTime);
    boKhuechDai.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.22);
    daoDong.connect(boKhuechDai);
    boKhuechDai.connect(ctx.destination);
    daoDong.start();
    daoDong.stop(ctx.currentTime + 0.22);
  } catch (e) {}
}

let danhSachTatCaCanh = [];
let trinhXemKrpano = null;
let dangTuDongQuay = false;
let dangAnGiaoDien = false;
const idCanhToanCanh = "68db993abb4ab400131f4e2d";
const idCanhSanTruong = "6a70c3d584ae020013a84a35";
const idCanhMacDinh = idCanhToanCanh;
let idCanhHienTai = idCanhMacDinh;
const lichSuDiChuyen = [];
let dangChayLittlePlanet = true;
let danhSachHotspotsHienTai = [];

const banDoLoiRaNhom = {
  "Tòa nhà C6": {
    loiRa: "6a7076453bde7c00145b4a06",
    sanh: "6a70776884ae020013a849d0",
    ten: "Tòa C6",
  },
  "Thư viện Phúc Giang": {
    loiRa: "6a70c35984ae020013a84a31",
    sanh: "6a7076453bde7c00145b49ef",
    ten: "Thư viện",
  },
  "Tòa nhà C5": {
    loiRa: "68db993bbb4ab400131f4e53",
    sanh: "68db993bbb4ab400131f4e52",
    ten: "Tòa C5",
  },
  "Tòa nhà C1": {
    loiRa: "68db993bbb4ab400131f4e86",
    sanh: "68db993bbb4ab400131f4e80",
    ten: "Tòa C1",
  },
  C3: {
    loiRa: "68db993bbb4ab400131f4e5e",
    sanh: "68db993bbb4ab400131f4e5e",
    ten: "Tòa C3",
  },
  "Toà nhà C2": {
    loiRa: "68db993bbb4ab400131f4e6e",
    sanh: "68db993bbb4ab400131f4e6e",
    ten: "Tòa C2",
  },
  "Toà nhà C4": {
    loiRa: "68db993bbb4ab400131f4e5c",
    sanh: "68db993bbb4ab400131f4e5c",
    ten: "Tòa C4",
  },
  "Hội trường đa năng": {
    loiRa: "68db993bbb4ab400131f4e66",
    sanh: "68db993bbb4ab400131f4e59",
    ten: "Hội trường",
  },
  "Phim trường số": {
    loiRa: "6a70c5f184ae020013a84a56",
    sanh: "6a70c5f184ae020013a84a56",
    ten: "Phim trường",
  },
};

function capNhatTienTrinhLoading(phanTram, thongBao) {
  const thanh = document.getElementById("thanh-tien-trinh-loading");
  const nhan = document.getElementById("nhan-phan-tram-loading");
  if (thanh) thanh.style.width = `${phanTram}%`;
  if (nhan && thongBao) nhan.textContent = thongBao;
}

function ketThucLoadingVaHienThiGiaoDien() {
  const manHinhLoading = document.getElementById("man-hinh-khoi-tao-tour");
  const tieuDeTren = document.querySelector("header");
  const logoPhai = document.getElementById("lop-logo-ictu-phai");

  if (manHinhLoading) {
    manHinhLoading.classList.add("opacity-0", "pointer-events-none");
    setTimeout(() => {
      manHinhLoading.style.display = "none";
    }, 700);
  }
  if (tieuDeTren) tieuDeTren.classList.remove("opacity-0");
  if (logoPhai) logoPhai.classList.remove("opacity-0");
}

function taoHotspotsChoCanh(hotspots) {
  const lopHotspots = document.getElementById("lop-hotspot-krpano");
  if (!lopHotspots) return;
  lopHotspots.innerHTML = "";
  danhSachHotspotsHienTai = hotspots || [];

  danhSachHotspotsHienTai.forEach((hs) => {
    const laLoiRa =
      hs.title &&
      (hs.title.toLowerCase().includes("lối ra") ||
        hs.title.toLowerCase().includes("ra sân") ||
        hs.title.toLowerCase().includes("trở lại") ||
        hs.title.toLowerCase().includes("về sân") ||
        hs.title.toLowerCase().includes("lối về"));

    const iconHtml = laLoiRa
      ? `<i class="fa-solid fa-door-open text-emerald-400 text-[10px]"></i>`
      : `<i class="fa-solid fa-location-dot text-amber-500 text-[10px]"></i>`;

    const theHs = document.createElement("div");
    theHs.id = `hotspot-item-${hs.id}`;
    theHs.className = `kr-hotspot-item ${laLoiRa ? "panoee-hotspot-exit" : ""}`;
    theHs.innerHTML = `
      <div class="panoee-hotspot-content">
        <div class="panoee-hotspot-label">
          ${iconHtml}
          <span>${hs.title}</span>
        </div>
        <div class="panoee-hotspot-pin-wrap">
          <div class="panoee-hotspot-pulse"></div>
          <div class="panoee-hotspot-pin">
            <img src="${hs.targetThumb || "../../image/ictu_logo.png"}" alt="${hs.title}">
          </div>
        </div>
      </div>
    `;
    theHs.onclick = (e) => {
      e.stopPropagation();
      diChuyenDenCanh(hs.targetSceneId);
    };
    lopHotspots.appendChild(theHs);
  });
}

function capNhatViTriHotspots() {
  if (
    !trinhXemKrpano ||
    dangChayLittlePlanet ||
    danhSachHotspotsHienTai.length === 0
  )
    return;
  danhSachHotspotsHienTai.forEach((hs) => {
    const p = trinhXemKrpano.spheretoscreen(hs.yaw, hs.pitch);
    const theHs = document.getElementById(`hotspot-item-${hs.id}`);
    if (theHs && p) {
      if (p.z > 0) {
        theHs.style.display = "flex";
        theHs.style.left = `${p.x}px`;
        theHs.style.top = `${p.y}px`;
      } else {
        theHs.style.display = "none";
      }
    }
  });
}

function vongLapCapNhatHotspot() {
  capNhatViTriHotspots();
  requestAnimationFrame(vongLapCapNhatHotspot);
}

function capNhatGiaoDienCanh(canh) {
  const nhanNhom = document.getElementById("nhan-nhom-canh-label");
  if (nhanNhom) {
    nhanNhom.textContent = canh.group || "Khuôn viên";
  }

  const nhanTieuDe = document.getElementById("ten-canh-hien-tai-label");
  if (nhanTieuDe) {
    nhanTieuDe.textContent = canh.title;
  }

  const nutQuayLai = document.getElementById("nut-quay-lai-lich-su");
  const nhanQuayLai = document.getElementById("nhan-quay-lai-lich-su");
  if (nutQuayLai) {
    if (lichSuDiChuyen.length > 0) {
      const idCanhTruoc = lichSuDiChuyen[lichSuDiChuyen.length - 1];
      const canhTruoc = danhSachTatCaCanh.find((c) => c.id === idCanhTruoc);
      if (nhanQuayLai) {
        nhanQuayLai.textContent = canhTruoc
          ? `Quay lại: ${canhTruoc.title}`
          : "Quay lại";
      }
      nutQuayLai.classList.remove("hidden");
    } else {
      nutQuayLai.classList.add("hidden");
    }
  }

  const nutRaNgoai = document.getElementById("nut-ra-ngoai-nhanh");
  const nhanRaNgoai = document.getElementById("nhan-ra-ngoai-nhanh");
  const thongTinNhom = banDoLoiRaNhom[canh.group];
  if (nutRaNgoai) {
    if (
      thongTinNhom &&
      canh.id !== idCanhSanTruong &&
      canh.id !== idCanhToanCanh
    ) {
      const laNgoaiTroi = canh.id === thongTinNhom.loiRa;
      if (nhanRaNgoai) {
        nhanRaNgoai.textContent = laNgoaiTroi
          ? "Về Sân trường"
          : `Ra sảnh: ${thongTinNhom.ten}`;
      }
      nutRaNgoai.classList.remove("hidden");
    } else if (canh.id !== idCanhSanTruong && canh.id !== idCanhToanCanh) {
      if (nhanRaNgoai) nhanRaNgoai.textContent = "Về Sân trường";
      nutRaNgoai.classList.remove("hidden");
    } else {
      nutRaNgoai.classList.add("hidden");
    }
  }

  const nhanChuyenFlycam = document.getElementById("nhan-chuyen-nhanh-flycam");
  if (nhanChuyenFlycam) {
    nhanChuyenFlycam.textContent =
      canh.id === idCanhToanCanh ? "Vào Sân trường" : "Góc nhìn Flycam";
  }

  capNhatTrangThaiTheThuVien(canh.id);
}

function chayHieuUngLittlePlanetIntro(canh) {
  dangChayLittlePlanet = true;
  const lopHotspots = document.getElementById("lop-hotspot-krpano");
  const lopDuoi = document.getElementById("lop-dieu-khien-duoi");
  if (lopHotspots) lopHotspots.classList.add("opacity-0");
  if (lopDuoi) lopDuoi.classList.add("opacity-0");

  const maXmlIntro = `
  <krpano>
    ${canh.krpano_xml || `<image><sphere url="${canh.preview}" /></image>`}
    <view hlookat="-60" vlookat="60" fov="150" fisheye="1.0" stereographic="true" fovmin="50" fovmax="150" />
  </krpano>
  `;

  trinhXemKrpano.set("xml_chuoi_intro", maXmlIntro);
  trinhXemKrpano.call("loadxml(get(xml_chuoi_intro));");

  taoHotspotsChoCanh(canh.hotspots || []);
  capNhatGiaoDienCanh(canh);

  capNhatTienTrinhLoading(100, "Khởi tạo thành công...");
  setTimeout(() => {
    ketThucLoadingVaHienThiGiaoDien();
    setTimeout(() => {
      trinhXemKrpano.call(
        "tween(view.hlookat, -4, 4.5, easeInOutCubic); tween(view.vlookat, 0, 4.5, easeInOutCubic); tween(view.fov, 90, 4.5, easeInOutCubic); tween(view.fisheye, 0.0, 4.5, easeInOutCubic);",
      );
      setTimeout(() => {
        dangChayLittlePlanet = false;
        if (lopHotspots) lopHotspots.classList.remove("opacity-0");
        if (lopDuoi) lopDuoi.classList.remove("opacity-0");
      }, 4600);
    }, 700);
  }, 400);
}

function taiCanh(id, coHieuUngIntro = false) {
  const canh =
    danhSachTatCaCanh.find((c) => c.id === id) || danhSachTatCaCanh[0];
  if (!canh || !trinhXemKrpano) return;

  idCanhHienTai = canh.id;

  if (coHieuUngIntro) {
    chayHieuUngLittlePlanetIntro(canh);
    return;
  }

  dangChayLittlePlanet = false;
  const lopHotspots = document.getElementById("lop-hotspot-krpano");
  const lopDuoi = document.getElementById("lop-dieu-khien-duoi");
  if (lopHotspots) lopHotspots.classList.add("opacity-0");

  const gocPitch =
    canh.id === idCanhSanTruong ? 2 : canh.id === idCanhToanCanh ? -2 : 0;
  const gocYaw =
    canh.id === idCanhSanTruong ? -18 : canh.id === idCanhToanCanh ? -4 : 0;
  const gocFov = canh.id === idCanhToanCanh ? 90 : 100;

  const maXmlCanh = `
  <krpano>
    ${canh.krpano_xml || `<image><sphere url="${canh.preview}" /></image>`}
    <view hlookat="${gocYaw}" vlookat="${gocPitch}" fov="${gocFov}" fisheye="0.0" stereographic="false" fovmin="45" fovmax="135" />
  </krpano>
  `;

  trinhXemKrpano.set("xml_chuoi_canh", maXmlCanh);
  trinhXemKrpano.call("loadxml(get(xml_chuoi_canh));");

  taoHotspotsChoCanh(canh.hotspots || []);
  capNhatGiaoDienCanh(canh);

  setTimeout(() => {
    if (lopHotspots) lopHotspots.classList.remove("opacity-0");
    if (lopDuoi) lopDuoi.classList.remove("opacity-0");
  }, 300);
}

function diChuyenDenCanh(targetId, khongLuuLichSu = false) {
  if (!targetId || targetId === idCanhHienTai) return;

  if (!khongLuuLichSu && idCanhHienTai) {
    lichSuDiChuyen.push(idCanhHienTai);
  }

  phatAmThanhDiChuyen();

  const lopPhu = document.getElementById("hieu-ung-di-chuyen");
  if (lopPhu) {
    lopPhu.classList.remove("opacity-0", "pointer-events-none");
    lopPhu.classList.add("opacity-100");
  }

  if (trinhXemKrpano) {
    trinhXemKrpano.call("tween(view.fov, 65, 0.28, easeInQuad);");
  }

  setTimeout(() => {
    taiCanh(targetId);
    setTimeout(() => {
      if (lopPhu) {
        lopPhu.classList.remove("opacity-100");
        lopPhu.classList.add("opacity-0", "pointer-events-none");
      }
    }, 280);
  }, 300);
}

function quayLaiCanhTruoc() {
  if (lichSuDiChuyen.length === 0) {
    diChuyenDenCanh(idCanhSanTruong, true);
    return;
  }
  const idTruoc = lichSuDiChuyen.pop();
  diChuyenDenCanh(idTruoc, true);
}

function raNgoaiPhanKhuHienTai() {
  const canhHienTai = danhSachTatCaCanh.find((c) => c.id === idCanhHienTai);
  if (!canhHienTai) {
    diChuyenDenCanh(idCanhSanTruong);
    return;
  }
  const thongTinNhom = banDoLoiRaNhom[canhHienTai.group];
  if (thongTinNhom) {
    if (
      idCanhHienTai !== thongTinNhom.sanh &&
      idCanhHienTai !== thongTinNhom.loiRa
    ) {
      diChuyenDenCanh(thongTinNhom.sanh || thongTinNhom.loiRa);
    } else if (idCanhHienTai !== thongTinNhom.loiRa) {
      diChuyenDenCanh(thongTinNhom.loiRa);
    } else {
      diChuyenDenCanh(idCanhSanTruong);
    }
  } else {
    diChuyenDenCanh(idCanhSanTruong);
  }
}

function chuyenCanhTiep() {
  const viTri = danhSachTatCaCanh.findIndex((c) => c.id === idCanhHienTai);
  if (viTri !== -1) {
    const viTriMoi = (viTri + 1) % danhSachTatCaCanh.length;
    diChuyenDenCanh(danhSachTatCaCanh[viTriMoi].id);
  }
}

function chuyenCanhTruoc() {
  const viTri = danhSachTatCaCanh.findIndex((c) => c.id === idCanhHienTai);
  if (viTri !== -1) {
    const viTriMoi =
      (viTri - 1 + danhSachTatCaCanh.length) % danhSachTatCaCanh.length;
    diChuyenDenCanh(danhSachTatCaCanh[viTriMoi].id);
  }
}

function veCanhMacDinh() {
  if (idCanhHienTai === idCanhSanTruong) {
    diChuyenDenCanh(idCanhToanCanh);
  } else {
    diChuyenDenCanh(idCanhSanTruong);
  }
}

function chuyenNhanhFlycamHoacSanTruong() {
  if (idCanhHienTai === idCanhToanCanh) {
    diChuyenDenCanh(idCanhSanTruong);
  } else {
    taiCanh(idCanhToanCanh, true);
  }
}

function dongManHinhIntro() {
  ketThucLoadingVaHienThiGiaoDien();
}

function boQuaIntroVaVaoSanTruong() {
  ketThucLoadingVaHienThiGiaoDien();
  diChuyenDenCanh(idCanhSanTruong);
}

function chayLaiIntroFlycam() {
  taiCanh(idCanhToanCanh, true);
}

function chuyenCheDoTuQuay() {
  dangTuDongQuay = !dangTuDongQuay;
  const nut = document.getElementById("nut-tu-dong-quay");
  if (trinhXemKrpano) {
    if (dangTuDongQuay) {
      trinhXemKrpano.call(
        "set(autorotate.enabled, true); set(autorotate.speed, -2.5); set(autorotate.waittime, 0.1);",
      );
      if (nut) nut.classList.add("text-sky-300", "bg-white/20");
    } else {
      trinhXemKrpano.call("set(autorotate.enabled, false);");
      if (nut) nut.classList.remove("text-sky-300", "bg-white/20");
    }
  }
}

function anHienGiaoDien() {
  dangAnGiaoDien = !dangAnGiaoDien;
  const lopDieuKhien = document.getElementById("lop-dieu-khien-duoi");
  const nutHienLai = document.getElementById("nut-hien-lai-thanh-dieu-khien");
  if (dangAnGiaoDien) {
    if (lopDieuKhien)
      lopDieuKhien.classList.add("opacity-0", "pointer-events-none");
    if (nutHienLai) nutHienLai.classList.remove("hidden");
  } else {
    if (lopDieuKhien)
      lopDieuKhien.classList.remove("opacity-0", "pointer-events-none");
    if (nutHienLai) nutHienLai.classList.add("hidden");
  }
}

function thuGonThanhDieuKhien() {
  anHienGiaoDien();
}

function hienLaiThanhDieuKhien() {
  anHienGiaoDien();
}

function chuyenCheDoVR() {
  chuyenToanManHinh();
}

function chuyenToanManHinh() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(() => {});
  } else {
    document.exitFullscreen().catch(() => {});
  }
}

function moThuVienCanh() {
  const modal = document.getElementById("modal-danh-sach-canh");
  const hopModal = document.getElementById("hop-modal-danh-sach");
  if (modal && hopModal) {
    modal.classList.remove("opacity-0", "pointer-events-none");
    hopModal.classList.remove("scale-95");
    hopModal.classList.add("scale-100");
  }
}

function dongThuVienCanh() {
  const modal = document.getElementById("modal-danh-sach-canh");
  const hopModal = document.getElementById("hop-modal-danh-sach");
  if (modal && hopModal) {
    modal.classList.add("opacity-0", "pointer-events-none");
    hopModal.classList.remove("scale-100");
    hopModal.classList.add("scale-95");
  }
}

function taoLuoiThuVienCanh(danhSach) {
  const container = document.getElementById("luoi-canh-container");
  if (!container) return;
  container.innerHTML = "";

  danhSach.forEach((canh) => {
    const the = document.createElement("button");
    the.id = `the-canh-${canh.id}`;
    the.className = `the-phong-thu-nho p-2 rounded-xl bg-slate-800/80 border border-slate-700/80 hover:border-sky-400 hover:bg-slate-700/80 transition text-left group flex flex-col ${
      canh.id === idCanhHienTai ? "dang-chon" : ""
    }`;
    the.onclick = () => {
      dongThuVienCanh();
      diChuyenDenCanh(canh.id);
    };

    the.innerHTML = `
      <div class="relative w-full aspect-video rounded-lg overflow-hidden border border-slate-700/60 mb-2">
        <img src="${canh.thumb}" alt="${canh.title}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300">
        <span class="absolute bottom-1 right-1 px-1.5 py-0.5 rounded bg-black/70 text-[9px] font-mono text-sky-300">360°</span>
      </div>
      <p class="text-xs font-bold text-slate-100 truncate group-hover:text-sky-300 transition w-full">${canh.title}</p>
      <span class="text-[10px] text-slate-400 truncate mt-0.5">${canh.hotspots?.length || 0} điểm kết nối</span>
    `;
    container.appendChild(the);
  });
}

function capNhatTrangThaiTheThuVien(idMoi) {
  document.querySelectorAll(".the-phong-thu-nho").forEach((the) => {
    the.classList.remove("dang-chon");
  });
  const theDangChon = document.getElementById(`the-canh-${idMoi}`);
  if (theDangChon) {
    theDangChon.classList.add("dang-chon");
  }
}

function timKiemCanh(tuKhoa) {
  const tuKhoaKhongDau = tuKhoa.toLowerCase().trim();
  if (!tuKhoaKhongDau) {
    taoLuoiThuVienCanh(danhSachTatCaCanh);
    return;
  }
  const ketQua = danhSachTatCaCanh.filter((c) =>
    c.title.toLowerCase().includes(tuKhoaKhongDau),
  );
  taoLuoiThuVienCanh(ketQua);
}

function caiDatPhimTat() {
  window.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") {
      chuyenCanhTiep();
    } else if (e.key === "ArrowLeft") {
      chuyenCanhTruoc();
    } else if (e.key === "ArrowUp" || e.key === "w" || e.key === "W") {
      const canh = danhSachTatCaCanh.find((c) => c.id === idCanhHienTai);
      if (canh && canh.hotspots && canh.hotspots.length > 0) {
        diChuyenDenCanh(canh.hotspots[0].targetSceneId);
      }
    } else if (e.key === "Escape") {
      dongThuVienCanh();
    }
  });
}

async function khoiTaoDuLieuTour() {
  capNhatTienTrinhLoading(15, "Đang tải dữ liệu 74 phân khu ICTU...");

  if (
    window.duLieuTour74 &&
    Array.isArray(window.duLieuTour74) &&
    window.duLieuTour74.length > 0
  ) {
    danhSachTatCaCanh = window.duLieuTour74;
  } else {
    try {
      const phanHoi = await fetch("../../image/tour/du_lieu_tour_74.json");
      if (!phanHoi.ok) throw new Error("Khong the tai du lieu");
      danhSachTatCaCanh = await phanHoi.json();
    } catch (loi) {
      danhSachTatCaCanh = [];
    }
  }

  danhSachTatCaCanh.forEach((canh) => {
    if (canh.preview && canh.preview.startsWith("../image/")) {
      canh.preview = "../" + canh.preview;
    }
    if (canh.thumb && canh.thumb.startsWith("../image/")) {
      canh.thumb = "../" + canh.thumb;
    }
    if (canh.hotspots) {
      canh.hotspots.forEach((hs) => {
        if (hs.targetThumb && hs.targetThumb.startsWith("../image/")) {
          hs.targetThumb = "../" + hs.targetThumb;
        }
      });
    }
  });

  capNhatTienTrinhLoading(60, "Đang khởi tạo không gian Little Planet...");
  const canhDauTien =
    danhSachTatCaCanh.find((c) => c.id === idCanhMacDinh) ||
    danhSachTatCaCanh[0];

  taoLuoiThuVienCanh(danhSachTatCaCanh);
  caiDatPhimTat();
  vongLapCapNhatHotspot();

  embedpano({
    id: "krpanoTourInstance",
    target: "khung-toan-canh-360",
    xml: null,
    html5: "only",
    mobilescale: 1.0,
    passQueryParameters: false,
    onready: function (kr) {
      trinhXemKrpano = kr;
      if (canhDauTien) {
        taiCanh(canhDauTien.id, true);
      }
    },
  });
}

window.addEventListener("DOMContentLoaded", () => {
  khoiTaoDuLieuTour();
});
