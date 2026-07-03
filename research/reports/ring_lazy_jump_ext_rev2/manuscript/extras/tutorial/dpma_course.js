"use strict";
/* DPMA 完全教程 — 导航 + 交互实验
   依赖:同目录 dpma_demo_data.js(全局 DPMA);KaTeX 由 HTML 侧加载。 */

/* ================= 章节导航与进度 ================= */
const SECTIONS = Array.from(document.querySelectorAll("section.ch"));
const LS_DONE = "dpma_course_done_v1", LS_LAST = "dpma_course_last_v1";
const doneSet = new Set(JSON.parse(localStorage.getItem(LS_DONE) || "[]"));

function saveDone() { localStorage.setItem(LS_DONE, JSON.stringify([...doneSet])); }

function buildToc() {
  const toc = document.getElementById("toc");
  toc.innerHTML = "";
  for (const s of SECTIONS) {
    const a = document.createElement("a");
    a.className = "nav"; a.href = "#" + s.id;
    a.innerHTML = (doneSet.has(s.id) ? '<span class="done">✓</span>' : "") + s.dataset.title;
    a.onclick = e => { e.preventDefault(); showChapter(s.id); };
    toc.appendChild(a);
  }
  markActive();
}
function markActive() {
  const cur = SECTIONS.find(s => s.classList.contains("show"));
  document.querySelectorAll("#toc a.nav").forEach((a, i) =>
    a.classList.toggle("active", SECTIONS[i] === cur));
}
function showChapter(id) {
  SECTIONS.forEach(s => s.classList.toggle("show", s.id === id));
  localStorage.setItem(LS_LAST, id);
  try { history.replaceState(null, "", "#" + id); } catch (e) { /* file:// 下部分浏览器禁止 */ }
  window.scrollTo(0, 0);
  markActive();
}
function resumeStudy() {
  const firstUndone = SECTIONS.find(s => !doneSet.has(s.id));
  showChapter(localStorage.getItem(LS_LAST) || (firstUndone ? firstUndone.id : SECTIONS[0].id));
}

/* 在每章末尾注入 上一章/完成/下一章 按钮 */
SECTIONS.forEach((s, i) => {
  const bar = document.createElement("div");
  bar.className = "navbtns";
  const prev = document.createElement("button");
  prev.textContent = i ? "← " + SECTIONS[i - 1].dataset.title : "已是第一章";
  prev.disabled = !i;
  prev.onclick = () => showChapter(SECTIONS[i - 1].id);
  const done = document.createElement("button");
  done.className = "donebtn";
  const doneLabel = () => doneSet.has(s.id) ? "✓ 已完成(点击撤销)" : "标记本章完成 ✓";
  done.textContent = doneLabel();
  done.onclick = () => {
    doneSet.has(s.id) ? doneSet.delete(s.id) : doneSet.add(s.id);
    saveDone(); done.textContent = doneLabel(); buildToc();
  };
  const next = document.createElement("button");
  next.textContent = i < SECTIONS.length - 1 ? SECTIONS[i + 1].dataset.title + " →" : "已是最后一章";
  next.disabled = i >= SECTIONS.length - 1;
  next.onclick = () => showChapter(SECTIONS[i + 1].id);
  bar.append(prev, done, next);
  s.appendChild(bar);
});
buildToc();
{ const h = location.hash.replace("#", "");
  showChapter(SECTIONS.some(s => s.id === h) ? h : (localStorage.getItem(LS_LAST) || "ch0")); }

/* ================= 画图小工具 ================= */
function plotFrame(cv, xlo, xhi, ylo, yhi, logx) {
  const c = cv.getContext("2d"); c.clearRect(0, 0, cv.width, cv.height);
  const L = 52, R = 12, T = 12, B = 30;
  const X = x => L + (cv.width - L - R) * ((logx ? Math.log(x / xlo) : x - xlo) /
                (logx ? Math.log(xhi / xlo) : xhi - xlo));
  const Y = y => cv.height - B - (cv.height - T - B) * (y - ylo) / (yhi - ylo);
  c.strokeStyle = "#999"; c.strokeRect(L, T, cv.width - L - R, cv.height - T - B);
  c.fillStyle = "#666"; c.font = "11px sans-serif";
  if (logx) { let d = Math.pow(10, Math.ceil(Math.log10(xlo)));
    for (; d < xhi; d *= 10) { c.strokeStyle = "#eee"; c.beginPath();
      c.moveTo(X(d), T); c.lineTo(X(d), cv.height - B); c.stroke();
      c.fillText(d < 1 ? d.toExponential(0) : d, X(d) - 8, cv.height - 14); } }
  c.fillText(yhi.toPrecision(2), 4, T + 10); c.fillText(ylo.toPrecision(2), 4, cv.height - B);
  if (ylo < 0 && yhi > 0) { c.strokeStyle = "#ccc"; c.beginPath();
    c.moveTo(L, Y(0)); c.lineTo(cv.width - R, Y(0)); c.stroke(); }
  return { c, X, Y };
}
function drawLine(f, xs, ys, color, w, dash) {
  f.c.strokeStyle = color; f.c.lineWidth = w || 1.6;
  if (dash) f.c.setLineDash(dash);
  f.c.beginPath();
  for (let i = 0; i < xs.length; i++) { const px = f.X(xs[i]), py = f.Y(ys[i]);
    i ? f.c.lineTo(px, py) : f.c.moveTo(px, py); }
  f.c.stroke(); f.c.lineWidth = 1; f.c.setLineDash([]);
}

/* ================= 第 1 章 · 迷你演示 ================= */
(function () {
  const cv = document.getElementById("ring0Cv"); if (!cv) return;
  const N = 16, ABS = 0, U = 8, START = 10, q = 2 / 3, beta = 0.25, lam = beta * (1 - q);
  let pos = START, timer = null;
  function draw(msg) {
    const c = cv.getContext("2d"); c.clearRect(0, 0, 270, 270);
    for (let i = 0; i < N; i++) {
      const a = Math.PI / 2 - 2 * Math.PI * i / N, x = 135 + 100 * Math.cos(a),
            y = 135 - 100 * Math.sin(a);
      c.beginPath(); c.arc(x, y, (i === ABS || i === U) ? 8 : 4.5, 0, 7);
      c.fillStyle = i === ABS ? "#c33" : (i === U ? "#2a8a2a" : "#c9c9d2"); c.fill();
      if (i === pos) { c.beginPath(); c.arc(x, y, 6, 0, 7); c.fillStyle = "#1656b8"; c.fill(); }
    }
    c.font = "12px sans-serif";
    c.fillStyle = "#c33"; c.fillText("出口", 122, 16);
    c.fillStyle = "#2a8a2a"; c.fillText("传送门", 113, 262);
    if (msg) { c.fillStyle = "#1656b8"; c.font = "13px sans-serif"; c.fillText(msg, 78, 140); }
  }
  function one() {
    const r = Math.random();
    if (pos === U && r < lam) { end("⚡ 被传送到出口!"); return; }
    const rest = pos === U ? r - lam : r;
    if (rest < 1 - q - (pos === U ? lam : 0)) { draw(); return; }   // 发呆
    pos = (Math.random() < 0.5) ? (pos + 1) % N : (pos - 1 + N) % N;
    if (pos === ABS) { end("🚪 自己走进了出口"); return; }
    draw();
  }
  function end(msg) { clearInterval(timer); timer = null; draw(msg);
    document.getElementById("ring0Msg").textContent = "  " + msg + "(按重置再来)"; }
  document.getElementById("ring0Step").onclick = () => {
    if (timer) return; let n = 0;
    document.getElementById("ring0Msg").textContent = "";
    timer = setInterval(() => { one(); if (++n >= 30 && timer) { clearInterval(timer); timer = null; } }, 90);
  };
  document.getElementById("ring0Reset").onclick = () => {
    clearInterval(timer); timer = null; pos = START;
    document.getElementById("ring0Msg").textContent = ""; draw(); };
  draw();
})();

/* ================= 第 2 章 · 实验一:走子直方图 ================= */
(function () {
  const ringCv = document.getElementById("ringCv"); if (!ringCv) return;
  const N1 = 40, ABS = 0, U = 20, START = 24, q1 = 2 / 3;
  let beta1 = 0.10, running = false, pos = START, steps = 0;
  let histC = new Array(400).fill(0), histD = new Array(400).fill(0), nDone = 0, nCap = 0;
  const histCv = document.getElementById("histCv");
  function drawRing() {
    const c = ringCv.getContext("2d"); c.clearRect(0, 0, 300, 300);
    for (let i = 0; i < N1; i++) {
      const a = Math.PI / 2 - 2 * Math.PI * i / N1, x = 150 + 118 * Math.cos(a),
            y = 150 - 118 * Math.sin(a);
      c.beginPath(); c.arc(x, y, i === ABS ? 7 : (i === U ? 7 : 3.4), 0, 7);
      c.fillStyle = i === ABS ? "#c33" : (i === U ? "#2a8a2a" : "#bbb"); c.fill();
      if (i === pos) { c.beginPath(); c.arc(x, y, 5, 0, 7); c.fillStyle = "#1656b8"; c.fill(); }
    }
    c.fillStyle = "#c33"; c.font = "12px sans-serif"; c.fillText("出口", 138, 18);
    c.fillStyle = "#2a8a2a"; c.fillText("传送门 λ=β(1−q)", 100, 292);
  }
  function drawHist() {
    const nb = 60, lo = 1, hi = 3000;
    const bc = new Array(nb).fill(0), bd = new Array(nb).fill(0);
    const bin = t => Math.min(nb - 1, Math.max(0, Math.floor(nb * Math.log(t / lo) / Math.log(hi / lo))));
    for (let t = 1; t < histC.length; t++) { if (histC[t]) bc[bin(t * 8)] += histC[t];
                                             if (histD[t]) bd[bin(t * 8)] += histD[t]; }
    const m = Math.max(1, ...bc.map((v, i) => v + bd[i]));
    const f = plotFrame(histCv, lo, hi, 0, m * 1.08, true);
    for (let i = 0; i < nb; i++) {
      const x0 = lo * Math.pow(hi / lo, i / nb), x1 = lo * Math.pow(hi / lo, (i + 1) / nb);
      const px0 = f.X(x0), px1 = f.X(x1);
      f.c.fillStyle = "#bbb"; f.c.fillRect(px0, f.Y(bd[i]), px1 - px0 - 1, f.Y(0) - f.Y(bd[i]));
      f.c.fillStyle = "rgba(42,138,42,.75)";
      f.c.fillRect(px0, f.Y(bd[i] + bc[i]), px1 - px0 - 1, f.Y(bd[i]) - f.Y(bd[i] + bc[i]));
    }
    f.c.fillStyle = "#333"; f.c.font = "12px sans-serif";
    f.c.fillText("到达步数(对数轴)— 绿 = 被抓走,灰 = 绕路到达", 60, 20);
  }
  function microStep() {
    steps++;
    const r = Math.random();
    if (pos === U) {
      const lam = beta1 * (1 - q1);
      if (r < lam) { nCap++; nDone++; histC[Math.min(399, Math.round(steps / 8))]++;
        pos = START; steps = 0; return; }
      if (r < 1 - q1) return;
      pos = (r < 1 - q1 / 2) ? (pos + 1) % N1 : (pos - 1 + N1) % N1;
    } else {
      if (r < 1 - q1) return;
      pos = (r < 1 - q1 / 2) ? (pos + 1) % N1 : (pos - 1 + N1) % N1;
    }
    if (pos === ABS) { nDone++; histD[Math.min(399, Math.round(steps / 8))]++;
      pos = START; steps = 0; }
  }
  function stepMany() {
    if (!running) return;
    for (let k = 0; k < 400; k++) microStep();
    drawRing(); drawHist();
    document.getElementById("tally").textContent =
      `  已完成 ${nDone} 趟 · 被抓走 ${(100 * nCap / Math.max(1, nDone)).toFixed(1)}%`;
    requestAnimationFrame(stepMany);
  }
  document.getElementById("runBtn").onclick = () => { running = !running; if (running) stepMany(); };
  document.getElementById("resetBtn").onclick = () => {
    histC.fill(0); histD.fill(0); nDone = nCap = 0; pos = START; steps = 0; drawRing(); drawHist(); };
  document.getElementById("betaSl").oninput = e => {
    beta1 = +e.target.value; document.getElementById("betaVal").textContent = beta1.toFixed(2); };
  drawRing(); drawHist();
})();

/* ================= 第 4 章 · 实验二:双指数调音台 ================= */
(function () {
  const cv = document.getElementById("twoExpCv"); if (!cv) return;
  const B1 = 0.02, s1 = 0.98;
  const ts = []; for (let t = 1; t <= 420; t += 2) ts.push(t);
  function draw() {
    const B2 = +document.getElementById("tw_B2").value, s2 = +document.getElementById("tw_s2").value;
    document.getElementById("tw_B2v").textContent = (B2 < 0 ? "−" : "") + Math.abs(B2).toFixed(3);
    document.getElementById("tw_s2v").textContent = s2.toFixed(3);
    const y1 = ts.map(t => B1 * Math.pow(s1, t - 1));
    const y2 = ts.map(t => B2 * Math.pow(s2, t - 1));
    const yt = ts.map((t, i) => y1[i] + y2[i]);
    const ylo = Math.min(0, ...y2) * 1.1 - 1e-4, yhi = Math.max(...y1) * 1.15;
    const f = plotFrame(cv, 1, 420, ylo, yhi, false);
    drawLine(f, ts, y1, "#c33", 1.3, [5, 4]);
    drawLine(f, ts, y2, "#1656b8", 1.3, [5, 4]);
    drawLine(f, ts, yt, "#111", 2.6);
    f.c.font = "12px sans-serif";
    f.c.fillStyle = "#c33"; f.c.fillText("B₁s₁ᵗ⁻¹(慢,正)", 90, 34);
    f.c.fillStyle = "#1656b8"; f.c.fillText("B₂s₂ᵗ⁻¹(快," + (B2 < 0 ? "负" : "正") + ")", 90, 50);
    f.c.fillStyle = "#111"; f.c.fillText("和 f(t)" + peakNote(yt), 90, 66);
  }
  function peakNote(y) {
    let k = 1; for (let i = 1; i < y.length - 1; i++) if (y[i] > y[k]) k = i;
    return (k > 1 && y[k] > y[0] && y[k] > y[y.length - 1]) ? ` — 有峰!位置 t≈${ts[k]}` : " — 单调,无峰";
  }
  document.getElementById("tw_B2").oninput = draw;
  document.getElementById("tw_s2").oninput = draw;
  draw();
})();

/* ================= 第 5 章 · 实验三:模开关(真实精确解) ================= */
(function () {
  const cv = document.getElementById("modeCv"); if (!cv || typeof DPMA === "undefined") return;
  const M = DPMA.modes;
  function drawModes() {
    const ymin = Math.min(...M.full) * 1.6 - 1e-4, ymax = Math.max(...M.full) * 1.55;
    const f = plotFrame(cv, M.t[0], M.t[M.t.length - 1], ymin, ymax, true);
    const sel = [["mFull", M.full, "#111", 2.4], ["m1", M.parts["1"], "#c33", 1.6],
                 ["m3", M.parts["3"], "#e08a00", 1.6], ["m9", M.parts["9"], "#1656b8", 1.6],
                 ["m31", M.parts["31"], "#2a8a2a", 1.6]];
    for (const [id, ys, col, w] of sel)
      if (document.getElementById(id).checked)
        drawLine(f, M.t, ys.map(v => Math.max(ymin, Math.min(ymax, v))), col, w);
    for (const [tm, lab] of [[M.marks.t1, "首峰"], [M.marks.tv, "谷"], [M.marks.t2, "第二峰"]]) {
      f.c.strokeStyle = "#aaa"; f.c.setLineDash([3, 3]); f.c.beginPath();
      f.c.moveTo(f.X(tm), 12); f.c.lineTo(f.X(tm), cv.height - 30); f.c.stroke(); f.c.setLineDash([]);
      f.c.fillStyle = "#555"; f.c.fillText(lab, f.X(tm) + 4, 24);
    }
  }
  for (const id of ["mFull", "m1", "m3", "m9", "m31"])
    document.getElementById(id).onchange = drawModes;
  drawModes();
})();

/* ================= 第 6 章 · 实验四:b 滑条穿过鞍结 ================= */
(function () {
  const cv = document.getElementById("foldCv"); if (!cv || typeof DPMA === "undefined") return;
  const FD = DPMA.fold; let zoom = false;
  function drawFold() {
    const i = +document.getElementById("bSl").value, b = FD.bs[i];
    document.getElementById("bVal").textContent =
      b.toFixed(3) + (Math.abs(b - FD.bc) < 5e-4 ? "  ← 就是 b_c!" : "");
    const ylo = zoom ? 2.0 : 0, yhi = zoom ? 3.4 : 40;
    const xlo = zoom ? 0.012 : FD.tau[0], xhi = zoom ? 0.12 : FD.tau[FD.tau.length - 1];
    const f = plotFrame(cv, xlo, xhi, ylo, yhi, true);
    for (let j = 0; j < FD.bs.length; j++)
      if (j !== i) drawLine(f, FD.tau, FD.curves[j].map(v => Math.max(ylo, Math.min(yhi, v))), "#e6e6e6", 1);
    drawLine(f, FD.tau, FD.curves[i].map(v => Math.max(ylo, Math.min(yhi, v))), "#1656b8", 2.4);
    f.c.fillStyle = "#333"; f.c.font = "13px sans-serif";
    f.c.fillText(`Φ(τ; b=${b}) — ${b < FD.bc ? "谷–峰对存在(双时间尺度)" :
      b > FD.bc ? "谷与峰已湮灭(单尺度)" : "恰在鞍结分岔点"}`, 64, 26);
  }
  document.getElementById("bSl").oninput = drawFold;
  document.getElementById("zoomBtn").onclick = () => { zoom = !zoom; drawFold(); };
  drawFold();
})();
