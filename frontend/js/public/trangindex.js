(function () {
  const canvas = document.getElementById("shader-canvas-ANIMATION_10");
  if (canvas) {
    function dongBoKichThuoc() {
      const w = canvas.clientWidth || 1280;
      const h = canvas.clientHeight || 720;
      if (canvas.width !== w || canvas.height !== h) {
        canvas.width = w;
        canvas.height = h;
      }
    }
    if (typeof ResizeObserver !== "undefined") {
      new ResizeObserver(dongBoKichThuoc).observe(canvas);
    }
    dongBoKichThuoc();

    const gl =
      canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
    if (gl) {
      const vs = `attribute vec2 a_position;
varying vec2 v_texCoord;
void main() {
  v_texCoord = a_position * 0.5 + 0.5;
  gl_Position = vec4(a_position, 0.0, 1.0);
}`;
      const fs = `precision highp float;
uniform vec2 u_resolution;
uniform float u_time;
uniform vec2 u_mouse;

vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec2 mod289(vec2 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec3 permute(vec3 x) { return mod289(((x*34.0)+1.0)*x); }

float snoise(vec2 v) {
  const vec4 C = vec4(0.211324865405187, 0.366025403784439, -0.577350269189626, 0.024390243902439);
  vec2 i = floor(v + dot(v, C.yy));
  vec2 x0 = v - i + dot(i, C.xx);
  vec2 i1;
  i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
  vec4 x12 = x0.xyxy + C.xxzz;
  x12.xy -= i1;
  i = mod289(i);
  vec3 p = permute(permute(i.y + vec3(0.0, i1.y, 1.0)) + i.x + vec3(0.0, i1.x, 1.0));
  vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy), dot(x12.zw,x12.zw)), 0.0);
  m = m*m;
  m = m*m;
  vec3 x = 2.0 * fract(p * C.www) - 1.0;
  vec3 h = abs(x) - 0.5;
  vec3 ox = floor(x + 0.5);
  vec3 a0 = x - ox;
  m *= 1.79284291400159 - 0.85373472095314 * (a0*a0 + h*h);
  vec3 g;
  g.x = a0.x * x0.x + h.x * x0.y;
  g.yz = a0.yz * x12.xz + h.yz * x12.yw;
  return 130.0 * dot(m, g);
}

void main() {
  vec2 st = gl_FragCoord.xy / u_resolution.xy;
  vec2 mouse = u_mouse / u_resolution.xy;
  if (mouse.x <= 0.0 && mouse.y <= 0.0) {
    mouse = vec2(0.5, 0.5);
  }
  float aspect = u_resolution.x / u_resolution.y;
  vec2 uv = st;
  uv.x *= aspect;
  float t = u_time * 0.15;
  float n1 = snoise(uv * 1.5 + vec2(t * 0.3, t * 0.2));
  float n2 = snoise(uv * 3.0 - vec2(t * 0.4, -t * 0.3) + n1 * 0.5);
  float n3 = snoise(uv * 6.0 + vec2(n2 * 0.3, t * 0.5));
  float distToMouse = length(st - mouse);
  float mouseWave = sin(distToMouse * 18.0 - u_time * 2.5) * exp(-distToMouse * 3.5) * 0.3;
  float combined = (n1 * 0.5 + n2 * 0.35 + n3 * 0.15) + mouseWave;
  vec3 deepNavy = vec3(0.04, 0.09, 0.20);
  vec3 royalBlue = vec3(0.09, 0.25, 0.65);
  vec3 vibrantCyan = vec3(0.08, 0.58, 0.82);
  vec3 darkBase = vec3(0.02, 0.05, 0.12);
  float factor1 = smoothstep(-0.6, 0.8, combined);
  float factor2 = smoothstep(-0.2, 0.9, n2 + mouseWave);
  vec3 col = mix(darkBase, deepNavy, st.y);
  col = mix(col, royalBlue, factor1 * 0.75);
  col = mix(col, vibrantCyan, factor2 * 0.35);
  float grid = (sin(st.x * 60.0) * sin(st.y * 60.0));
  col += vibrantCyan * max(0.0, grid) * 0.025;
  gl_FragColor = vec4(col, 1.0);
}`;
      function cs(type, src) {
        const s = gl.createShader(type);
        gl.shaderSource(s, src);
        gl.compileShader(s);
        return s;
      }
      const prog = gl.createProgram();
      gl.attachShader(prog, cs(gl.VERTEX_SHADER, vs));
      gl.attachShader(prog, cs(gl.FRAGMENT_SHADER, fs));
      gl.linkProgram(prog);
      gl.useProgram(prog);
      const buf = gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER, buf);
      gl.bufferData(
        gl.ARRAY_BUFFER,
        new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]),
        gl.STATIC_DRAW,
      );
      const pos = gl.getAttribLocation(prog, "a_position");
      gl.enableVertexAttribArray(pos);
      gl.vertexAttribPointer(pos, 2, gl.FLOAT, false, 0, 0);
      const uTime = gl.getUniformLocation(prog, "u_time");
      const uRes = gl.getUniformLocation(prog, "u_resolution");
      const uMouse = gl.getUniformLocation(prog, "u_mouse");

      let mouse = { x: canvas.width / 2, y: canvas.height / 2 };
      window.addEventListener("mousemove", (event) => {
        const rect = canvas.getBoundingClientRect();
        if (rect.width && rect.height) {
          const nx = (event.clientX - rect.left) / rect.width;
          const ny = 1.0 - (event.clientY - rect.top) / rect.height;
          mouse.x = nx * canvas.width;
          mouse.y = ny * canvas.height;
        }
      });

      function render(t) {
        if (typeof ResizeObserver === "undefined") dongBoKichThuoc();
        gl.viewport(0, 0, canvas.width, canvas.height);
        if (uTime) gl.uniform1f(uTime, t * 0.001);
        if (uRes) gl.uniform2f(uRes, canvas.width, canvas.height);
        if (uMouse) gl.uniform2f(uMouse, mouse.x, mouse.y);
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
        requestAnimationFrame(render);
      }
      render(0);
    }
  }
})();

function khoiTaoTour360() {
  const duongDanTourNoiBo = "thamquan.html";
  const nutKichHoat = document.getElementById("nut-kich-hoat-tour");
  const nutAnLopPhu = document.getElementById("nut-an-lop-phu");
  const lopPhuPoster = document.getElementById("lop-phu-poster");
  const nutHienLopPhu = document.getElementById("nut-hien-lop-phu");
  const nutXoay360 = document.getElementById("nut-xoay-360");
  const nutCheDoVr = document.getElementById("nut-che-do-vr");
  const nutToanManHinhBar = document.getElementById("nut-toan-man-hinh-bar");
  const campusImg = document.getElementById("campus-panoramic-image");

  function moTourNoiBo() {
    window.location.href = duongDanTourNoiBo;
  }

  if (nutKichHoat) nutKichHoat.addEventListener("click", moTourNoiBo);
  if (nutCheDoVr) nutCheDoVr.addEventListener("click", moTourNoiBo);
  if (nutToanManHinhBar)
    nutToanManHinhBar.addEventListener("click", moTourNoiBo);

  if (nutAnLopPhu && lopPhuPoster) {
    nutAnLopPhu.addEventListener("click", () => {
      lopPhuPoster.classList.add("hidden");
      if (nutHienLopPhu) nutHienLopPhu.classList.remove("hidden");
    });
  }

  if (nutHienLopPhu && lopPhuPoster) {
    nutHienLopPhu.addEventListener("click", () => {
      lopPhuPoster.classList.remove("hidden");
      nutHienLopPhu.classList.add("hidden");
    });
  }

  const nutChonCanhList = document.querySelectorAll(".btn-preview-scene");
  nutChonCanhList.forEach((btn) => {
    btn.addEventListener("click", () => {
      nutChonCanhList.forEach((b) => {
        b.classList.remove("bg-primary", "text-white");
        b.classList.add("bg-surface-container-lowest", "text-on-surface");
      });
      btn.classList.remove("bg-surface-container-lowest", "text-on-surface");
      btn.classList.add("bg-primary", "text-white");
      const duongDanAnhMoi = btn.getAttribute("data-src");
      if (campusImg && duongDanAnhMoi) {
        campusImg.style.opacity = "0";
        setTimeout(() => {
          campusImg.src = duongDanAnhMoi;
          campusImg.style.opacity = "1";
        }, 180);
      }
    });
  });

  let dangAutoXoay = false;
  let gocQuay = 0;
  let huongQuay = 1;
  let idYeuCauKhungHinh = null;

  function chayAutoXoay() {
    if (!dangAutoXoay || !campusImg) return;
    gocQuay += 0.3 * huongQuay;
    if (gocQuay > 70) huongQuay = -1;
    if (gocQuay < -70) huongQuay = 1;
    campusImg.style.transform = `scale(1.15) translate3d(${gocQuay}px, 0, 0)`;
    idYeuCauKhungHinh = requestAnimationFrame(chayAutoXoay);
  }

  if (nutXoay360) {
    nutXoay360.addEventListener("click", () => {
      dangAutoXoay = !dangAutoXoay;
      if (dangAutoXoay) {
        nutXoay360.classList.add("bg-primary", "text-white");
        if (lopPhuPoster) lopPhuPoster.classList.add("hidden");
        if (nutHienLopPhu) nutHienLopPhu.classList.remove("hidden");
        chayAutoXoay();
      } else {
        nutXoay360.classList.remove("bg-primary", "text-white");
        if (idYeuCauKhungHinh) cancelAnimationFrame(idYeuCauKhungHinh);
      }
    });
  }

  if (campusImg && campusImg.parentElement) {
    let dangTuongTac = false;
    let viTriBatDau = 0;
    let viTriHienTai = 0;

    campusImg.parentElement.addEventListener("mousedown", (e) => {
      dangTuongTac = true;
      if (dangAutoXoay) {
        dangAutoXoay = false;
        if (nutXoay360) nutXoay360.classList.remove("bg-primary", "text-white");
        if (idYeuCauKhungHinh) cancelAnimationFrame(idYeuCauKhungHinh);
      }
      viTriBatDau = e.clientX - viTriHienTai;
    });

    window.addEventListener("mouseup", () => {
      dangTuongTac = false;
    });

    window.addEventListener("mousemove", (e) => {
      if (!dangTuongTac) return;
      viTriHienTai = e.clientX - viTriBatDau;
      const xGioiHan = Math.max(-100, Math.min(100, viTriHienTai * 0.25));
      campusImg.style.transform = `scale(1.15) translate3d(${xGioiHan}px, 0, 0)`;
    });

    campusImg.parentElement.addEventListener(
      "touchstart",
      (e) => {
        if (e.touches.length === 1) {
          dangTuongTac = true;
          viTriBatDau = e.touches[0].clientX - viTriHienTai;
        }
      },
      { passive: true },
    );

    window.addEventListener("touchend", () => {
      dangTuongTac = false;
    });

    window.addEventListener(
      "touchmove",
      (e) => {
        if (!dangTuongTac || e.touches.length !== 1) return;
        viTriHienTai = e.touches[0].clientX - viTriBatDau;
        const xGioiHan = Math.max(-100, Math.min(100, viTriHienTai * 0.25));
        campusImg.style.transform = `scale(1.15) translate3d(${xGioiHan}px, 0, 0)`;
      },
      { passive: true },
    );
  }
}

document.addEventListener("DOMContentLoaded", khoiTaoTour360);
