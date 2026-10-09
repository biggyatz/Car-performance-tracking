"use strict";
const el = id => document.getElementById(id);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
function npr(v) {
  if (v >= 1e7) return `Rs ${(v / 1e7).toFixed(2).replace(/\.?0+$/, "")} crore`;
  if (v >= 1e5) return `Rs ${(v / 1e5).toFixed(1).replace(/\.0$/, "")} lakh`;
  return "Rs " + Math.round(v).toLocaleString("en-IN");
}
const short = v => v >= 1e7 ? (v / 1e7).toFixed(2).replace(/\.?0+$/, "") + " Cr" : (v / 1e5).toFixed(1).replace(/\.0$/, "") + " L";

const tip = el("tooltip");
function showTip(e, title, rows) {
  tip.innerHTML = `<b>${esc(title)}</b>` + rows.map(([k, v]) => `<div class="row"><span>${esc(k)}</span><span>${esc(v)}</span></div>`).join("");
  tip.hidden = false;
  const w = tip.offsetWidth, h = tip.offsetHeight;
  let x = e.clientX + 14, y = e.clientY + 14;
  if (x + w > innerWidth - 8) x = e.clientX - w - 14;
  if (y + h > innerHeight - 8) y = e.clientY - h - 14;
  tip.style.left = Math.max(8, x) + "px"; tip.style.top = Math.max(8, y) + "px";
}
function bindTips(svg, lookup) {
  svg.querySelectorAll("[data-tip]").forEach(n => {
    n.addEventListener("pointermove", e => { const t = lookup(n.dataset.tip); showTip(e, t.title, t.rows); });
    n.addEventListener("pointerleave", () => { tip.hidden = true; });
  });
}

let M, L;
const state = { make: "Hyundai", family: "Creta", year: 2019, condition: "Used", km: null };
Promise.all([fetch("model.json").then(r => r.json()), fetch("listings.json").then(r => r.json())]).then(([m, l]) => { M = m; L = l; init(); });

function init() {
  const makes = [...new Set(M.families.map(f => f.make))].sort((a, b) => count(b) - count(a));
  el("make").innerHTML = makes.map(m => `<option>${esc(m)}</option>`).join("");
  if (!makes.includes(state.make)) state.make = makes[0];
  el("make").value = state.make;
  el("make").addEventListener("change", e => { state.make = e.target.value; fillFamilies(); update(); });
  el("family").addEventListener("change", e => { state.family = e.target.value; setupYear(); update(); });
  el("year").addEventListener("input", e => { state.year = +e.target.value; el("year-o").textContent = state.year; update(); });
  el("km").addEventListener("input", e => { const v = parseFloat(e.target.value); state.km = v > 0 ? v : null; update(); });
  fillFamilies(true);
  renderKPIs(); renderDepreciation(); renderAbout();
  document.querySelectorAll("[data-table-toggle]").forEach(btn => btn.addEventListener("click", () => {
    const t = el(btn.dataset.tableToggle + "-table"); t.hidden = !t.hidden; btn.textContent = t.hidden ? "Show table" : "Hide table";
  }));
  update();
  let rt; addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(() => { update(); renderDepreciation(); }, 120); });
}
const count = make => M.families.filter(f => f.make === make).reduce((a, f) => a + f.n, 0);
function fillFamilies(keep) {
  const fams = M.families.filter(f => f.make === state.make).sort((a, b) => b.n - a.n);
  el("family").innerHTML = fams.map(f => `<option value="${esc(f.family)}">${esc(f.family)} (${f.n} listings)</option>`).join("");
  if (!keep || !fams.some(f => f.family === state.family)) state.family = fams[0].family;
  el("family").value = state.family;
  setupYear();
}
const fam = () => M.families.find(f => f.make === state.make && f.family === state.family);
function setupYear() {
  const f = fam(), lo = Math.max(1995, f.year_min - 2), hi = M.now;
  const r = el("year"); r.min = lo; r.max = hi;
  state.year = Math.min(hi, Math.max(lo, state.year));
  r.value = state.year; el("year-o").textContent = state.year;
}

function renderKPIs() {
  el("lead-n").textContent = M.n.toLocaleString("en-IN");
  const keep5 = Math.exp(M.coef.age * 5 + M.coef.age2 * 25 / 10) * 100;
  const tiles = [
    ["Listings analysed", M.n.toLocaleString("en-IN"), "used-car asking prices"],
    ["Models covered", M.families.length, `${M.families.filter(f => f.new).length} matched to new prices`],
    ["Value after 5 years", `${keep5.toFixed(0)}%`, "of a nearly new car, typical"],
    ["Typical error", `±${M.cv.median_abs_pct_err}%`, "median, on held-out listings"],
  ];
  el("kpis").innerHTML = tiles.map(([l, v, n]) => `<div class="kpi"><div class="label">${l}</div><div class="value">${v}</div><div class="note">${n}</div></div>`).join("");
  el("sources").innerHTML = `Data: ${M.n.toLocaleString("en-IN")} used-car listings from <a href="https://hamrobazaar.com">hamrobazaar.com</a> and new-car prices from <a href="https://www.nepaldrives.com">nepaldrives.com</a>, collected October 2026 within each site's robots.txt rules. No personal data is stored.`;
}

function input() { const f = fam(); return { make: state.make, family: state.family, year: state.year, condition: state.condition, km: state.km, ev: f.ev }; }
function update() {
  const f = fam(), p = predictCar(M, input());
  el("price").textContent = npr(p.price);
  let meta = `<span>Likely range <strong>${short(p.low)} – ${short(p.high)}</strong></span>`;
  if (f.new) meta += `<span>New today <strong>${short(f.new.low)}${f.new.high > f.new.low ? "+" : ""}</strong> (${esc(f.new.model)}) · <strong>${Math.round(100 * p.price / f.new.low)}%</strong> of new</span>`;
  if (f.pooled) meta += `<span>Few listings for this model; estimate leans on ${esc(state.make)} overall</span>`;
  el("meta").innerHTML = meta;
  renderRange(p); renderCurve(f); renderComps();
}
function renderRange(p) {
  const host = el("range-chart"), W = Math.max(300, host.clientWidth), H = 64;
  const lo = p.low * 0.85, hi = p.high * 1.1, x = v => 8 + ((v - lo) / (hi - lo)) * (W - 16);
  host.innerHTML = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Likely value range">
    <rect x="${x(p.low)}" y="18" width="${x(p.high) - x(p.low)}" height="14" rx="4" fill="var(--accent-wash)"/>
    <rect x="${x(p.q1)}" y="18" width="${x(p.q3) - x(p.q1)}" height="14" rx="4" fill="var(--accent)" opacity=".35"/>
    <circle cx="${x(p.price)}" cy="25" r="7" fill="var(--accent)" class="dot"/>
    <text class="tick" x="${x(p.low)}" y="50" text-anchor="middle">${short(p.low)}</text><text class="tick" x="${x(p.high)}" y="50" text-anchor="middle">${short(p.high)}</text>
    <text class="tick" x="${x(p.low)}" y="12">Likely range (80%); darker band = middle 50%</text></svg>`;
}
function renderCurve(f) {
  const host = el("curve-chart"), W = Math.max(300, host.clientWidth), H = 220, m = { l: 48, r: 12, t: 12, b: 28 };
  const y0 = Math.max(1995, f.year_min - 2), y1 = M.now;
  const pts = L.filter(r => r.make === state.make && r.family === state.family);
  const curve = []; for (let yr = y0; yr <= y1; yr++) curve.push([yr, predictCar(M, { ...input(), year: yr }).price]);
  const vmax = Math.max(...curve.map(c => c[1]), ...pts.map(p => p.price)) * 1.1;
  const x = v => m.l + ((v - y0) / Math.max(1, y1 - y0)) * (W - m.l - m.r), y = v => H - m.b - (v / vmax) * (H - m.t - m.b);
  const step = vmax > 2e7 ? 5e6 : vmax > 8e6 ? 2e6 : vmax > 3e6 ? 1e6 : 5e5;
  let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Value by year">`;
  for (let t = 0; t <= vmax; t += step) s += `<line class="gridline" x1="${m.l}" x2="${W - m.r}" y1="${y(t)}" y2="${y(t)}"/><text class="tick" x="${m.l - 6}" y="${y(t) + 4}" text-anchor="end">${t ? short(t) : "0"}</text>`;
  const ystep = (y1 - y0) > 16 ? 5 : (y1 - y0) > 8 ? 2 : 1;
  for (let yr = Math.ceil(y0 / ystep) * ystep; yr <= y1; yr += ystep) s += `<text class="tick" x="${x(yr)}" y="${H - 8}" text-anchor="middle">${yr}</text>`;
  s += `<line class="baseline" x1="${m.l}" x2="${W - m.r}" y1="${y(0)}" y2="${y(0)}"/>`;
  s += `<path d="M${curve.map(c => `${x(c[0])},${y(c[1])}`).join("L")}" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>`;
  pts.forEach((p, i) => { s += `<circle class="dot" cx="${x(p.year)}" cy="${y(p.price)}" r="4.5" fill="var(--mid)"/><circle class="hit" data-tip="${i}" cx="${x(p.year)}" cy="${y(p.price)}" r="10"/>`; });
  s += `<circle class="dot" cx="${x(state.year)}" cy="${y(curve.find(c => c[0] === state.year)[1])}" r="7" fill="var(--accent)"/></svg>`;
  host.innerHTML = s;
  bindTips(host.querySelector("svg"), i => ({ title: pts[i].title, rows: [["Asking price", npr(pts[i].price)], ["Year", pts[i].year]] }));
}
function renderComps() {
  const comps = L.filter(r => r.make === state.make && r.family === state.family)
    .sort((a, b) => Math.abs(a.year - state.year) - Math.abs(b.year - state.year)).slice(0, 6);
  el("comps-sub").textContent = comps.length ? `Closest ${state.make} ${state.family} listings by year.` : "No listings for this model yet.";
  el("comps").innerHTML = comps.map(r => `
    <a class="comp" href="${esc(r.url)}" target="_blank" rel="noopener noreferrer">
      <span class="t">${esc(r.title)}</span><span class="p">${short(r.price)}</span>
      <span class="m">${r.year}${r.km ? " · " + Math.round(r.km).toLocaleString("en-IN") + " km" : ""}<span class="badge">hamrobazaar</span></span><span class="m r"></span>
    </a>`).join("");
}
function renderDepreciation() {
  const ages = Array.from({ length: 16 }, (_, i) => i);
  const kept = ev => ages.map(a => 100 * Math.exp(M.coef.age * a + M.coef.age2 * a * a / 10 + (ev ? M.coef.ev_age * a : 0)));
  const series = [{ label: "Petrol / diesel", color: "var(--a)", v: kept(false) }];
  // Only show electric separately when the data shows a real difference (5+ points by year 8).
  const ev = kept(true);
  if (M.families.some(f => f.ev) && Math.abs(ev[8] - series[0].v[8]) >= 5) series.push({ label: "Electric", color: "var(--b)", v: ev });
  el("dep-legend").innerHTML = series.length > 1 ? series.map(s => `<span class="key"><span class="sw" style="background:${s.color}"></span>${s.label}</span>`).join("") : "";
  const host = el("dep-chart"), W = Math.max(300, host.clientWidth), H = 240, m = { l: 40, r: 70, t: 12, b: 28 };
  const x = a => m.l + (a / 15) * (W - m.l - m.r), y = v => H - m.b - (v / 100) * (H - m.t - m.b);
  let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Value kept by age">`;
  for (const t of [0, 25, 50, 75, 100]) s += `<line class="gridline" x1="${m.l}" x2="${W - m.r}" y1="${y(t)}" y2="${y(t)}"/><text class="tick" x="${m.l - 6}" y="${y(t) + 4}" text-anchor="end">${t}%</text>`;
  for (const a of [0, 3, 6, 9, 12, 15]) s += `<text class="tick" x="${x(a)}" y="${H - 8}" text-anchor="middle">${a} yr</text>`;
  series.forEach((se, j) => {
    s += `<path d="M${ages.map(a => `${x(a)},${y(se.v[a])}`).join("L")}" fill="none" stroke="${se.color}" stroke-width="2" stroke-linejoin="round"/>`;
    s += `<circle class="dot" cx="${x(15)}" cy="${y(se.v[15])}" r="4" fill="${se.color}"/><text class="lbl" x="${x(15) + 8}" y="${y(se.v[15]) + 4}">${se.v[15].toFixed(0)}%</text>`;
    ages.forEach(a => { s += `<circle class="hit" data-tip="${j}:${a}" cx="${x(a)}" cy="${y(se.v[a])}" r="9"/>`; });
  });
  s += "</svg>";
  host.innerHTML = s;
  bindTips(host.querySelector("svg"), k => { const [j, a] = k.split(":").map(Number); return { title: series[j].label, rows: [["Age", a + " years"], ["Value kept", series[j].v[a].toFixed(0) + "%"]] }; });
  el("dep-table").innerHTML = `<table><thead><tr><th class="n">Age</th>${series.map(s => `<th class="n">${s.label}</th>`).join("")}</tr></thead><tbody>` +
    ages.map(a => `<tr><td class="n">${a}</td>${series.map(s => `<td class="n">${s.v[a].toFixed(0)}%</td>`).join("")}</tr>`).join("") + "</tbody></table>";
}
function renderAbout() {
  const c = M.cv, g = M.cv_gboost;
  el("about-text").innerHTML = `A regression on the log of asking price with effects for make and model (shrunk toward the make when a model has few listings), age, kilometres where the seller states them, and electric drivetrain. Seller-chosen condition labels are ignored because they are unreliable. ` +
    (c.r2_log >= g.r2_log ? "It beat gradient boosting in 5-fold cross-validation, and every effect is explainable." : "Gradient boosting scored slightly higher in cross-validation, but the regression was kept because it is explainable and extrapolates smoothly across years.") +
    ` Model years written in Bikram Sambat (e.g. 2075) are converted to AD.`;
  const tiles = [
    ["Median error", `${c.median_abs_pct_err}%`, "on held-out listings (5-fold CV)"],
    ["Within ±20%", `${c.within_20pct}%`, "of held-out listings"],
    ["R² (log price)", c.r2_log.toFixed(2), `gradient boosting: ${g.r2_log.toFixed(2)}`],
    ["Training listings", M.n.toLocaleString("en-IN"), "after cleaning and outlier removal"],
  ];
  el("model-stats").innerHTML = tiles.map(([l, v, n]) => `<div class="kpi"><div class="label">${l}</div><div class="value">${v}</div><div class="note">${n}</div></div>`).join("");
}
