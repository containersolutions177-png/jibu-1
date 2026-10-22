const API = window.JIBU_API;
const userId = "u1";
let currentPage = "home";
let userData = null;

// ============ HELPERS ============
async function api(path, opts = {}) {
  try {
    const res = await fetch(API + path, {
      headers: { "Content-Type": "application/json" },
      ...opts,
    });
    if (!res.ok) throw new Error("HTTP " + res.status);
    return await res.json();
  } catch (e) {
    console.error("API error:", e);
    return null;
  }
}

function toast(msg) {
  const t = document.createElement("div");
  t.className = "toast";
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 2200);
}

// ============ ROUTER ============
const app = document.getElementById("app");

function render() {
  if (currentPage === "home") renderHome();
  else if (currentPage === "safiri") renderSafiri();
  else if (currentPage === "market") renderMarket();
  else if (currentPage === "modules") renderModules();
  document.querySelectorAll(".bottomnav button").forEach(b => {
    b.classList.toggle("active", b.dataset.page === currentPage);
  });
}

document.querySelectorAll(".bottomnav button").forEach(b => {
  b.addEventListener("click", () => {
    currentPage = b.dataset.page;
    render();
  });
});

// ============ PAGE: HOME ============
async function renderHome() {
  app.innerHTML = `<div class="loading">Loading dashboard…</div>`;
  const stats = await api("/stats");
  userData = await api("/users/" + userId);
  if (!stats) {
    app.innerHTML = `<div class="card">⚠️ Backend unreachable.<br>Check <code>config.js</code>.</div>`;
    return;
  }
  document.getElementById("userScore").textContent = "Score: " + (userData?.jibu_score ?? "—");
  const s = stats.safiri;
  app.innerHTML = `
    <h1>Welcome, ${userData?.name?.split(" ")[0] ?? "User"} 👋</h1>
    <div class="subtitle">Living OS for emerging markets</div>

    <div class="stat-grid">
      <div class="stat blue"><div class="label">Users</div><div class="value">${stats.users.total}</div></div>
      <div class="stat green"><div class="label">Revenue</div><div class="value">$${stats.commerce.revenue}</div></div>
      <div class="stat orange"><div class="label">Safiri Ads</div><div class="value">${s.ads}</div></div>
      <div class="stat red"><div class="label">Bounce Rate</div><div class="value">${s.bounce_rate}%</div></div>
    </div>

    <div class="card">
      <h2>Safiri Performance</h2>
      <div class="metric-row"><span>Impressions</span><span>${s.impressions}</span></div>
      <div class="metric-row"><span>Clicks</span><span>${s.clicks}</span></div>
      <div class="metric-row"><span>Conversions</span><span>${s.conversions}</span></div>
      <div class="metric-row"><span>Click Rate</span><span>${s.click_rate}%</span></div>
      <div class="metric-row"><span>Conversion Rate</span><span>${s.conversion_rate}%</span></div>
    </div>

    <div class="card">
      <h2>Active Modules</h2>
      <div>${stats.modules.map(m => `<span class="chip">${m}</span>`).join("")}</div>
    </div>
  `;
}

// ============ PAGE: SAFIRI ============
async function renderSafiri() {
  app.innerHTML = `<div class="loading">Loading impulse ads…</div>`;
  const ads = await api("/ads");
  if (!ads) { app.innerHTML = `<div class="card">⚠️ Backend unreachable.</div>`; return; }
  const products = await api("/products");

  app.innerHTML = `<h1>Safiri</h1><div class="subtitle">Mirror ads — no gimmicks, no timers</div>` +
    ads.map(a => {
      const p = products?.find(x => x.id === a.product_id);
      return `
        <div class="ad-card">
          <img src="${a.image_url}" alt="${a.headline}" onerror="this.style.display='none'">
          <div class="ad-body">
            <div class="ad-headline">${a.headline}</div>
            <div class="ad-copy">${a.copy}</div>
            <div class="ad-bottom">
              <div class="ad-price">$${(p?.price ?? 0).toFixed(2)}</div>
              <button class="buy-btn" onclick="buyNow('${a.id}','${a.product_id}',${p?.price ?? 0})">Buy Now</button>
            </div>
          </div>
        </div>
      `;
    }).join("");
}

async function buyNow(adId, productId, price) {
  const btns = document.querySelectorAll(".buy-btn");
  btns.forEach(b => b.disabled = true);
  await api(`/ads/${adId}/click`, { method: "POST" });
  const result = await api("/orders", {
    method: "POST",
    body: JSON.stringify({ user_id: userId, product_id: productId, amount: price }),
  });
  if (result?.status === "completed") {
    toast("✅ Purchased! $" + price.toFixed(2));
  } else if (result?.status === "failed_insufficient") {
    toast("❌ Insufficient wallet balance");
  } else {
    toast("Something went wrong");
  }
  btns.forEach(b => b.disabled = false);
}

// ============ PAGE: MARKET ============
async function renderMarket() {
  app.innerHTML = `<div class="loading">Loading products…</div>`;
  const products = await api("/products");
  if (!products) { app.innerHTML = `<div class="card">⚠️ Backend unreachable.</div>`; return; }
  app.innerHTML = `<h1>Marketplace</h1><div class="subtitle">Duka + Soko products</div>` +
    products.map(p => `
      <div class="ad-card">
        <img src="${p.image_url}" alt="${p.name}" onerror="this.style.display='none'">
        <div class="ad-body">
          <div class="ad-headline">${p.name}</div>
          <div class="ad-copy">${p.description}</div>
          <div class="ad-bottom">
            <div class="ad-price">$${p.price.toFixed(2)}</div>
            <button class="buy-btn" onclick="buyNow('a1','${p.id}',${p.price})">Buy Now</button>
          </div>
        </div>
      </div>
    `).join("");
}

// ============ PAGE: MODULES ============
async function renderModules() {
  const mods = [
    { icon: "📚", name: "Mentor", key: "mentor" },
    { icon: "🏪", name: "Duka", key: "duka" },
    { icon: "🏥", name: "Tiba", key: "tiba" },
    { icon: "🌾", name: "Soko", key: "soko" },
    { icon: "⚖️", name: "Sheria", key: "sheria" },
    { icon: "💼", name: "Kazi", key: "kazi" },
    { icon: "💰", name: "Pesa", key: "pesa" },
    { icon: "📰", name: "Mtaa", key: "mtaa" },
    { icon: "⚡", name: "Safiri", key: "safiri" },
  ];
  app.innerHTML = `
    <h1>All Modules</h1>
    <div class="subtitle">Tap any module to test it</div>
    <div class="module-grid">
      ${mods.map(m => `<div class="module-card" onclick="openModule('${m.key}')">
        <div class="module-icon">${m.icon}</div>
        <div class="module-name">${m.name}</div>
      </div>`).join("")}
    </div>
    <div id="moduleOutput"></div>
  `;
}

async function openModule(key) {
  const out = document.getElementById("moduleOutput");
  out.innerHTML = `<div class="loading">Calling ${key}…</div>`;
  let data;
  let post = false;
  if (key === "mentor") { data = await api(`/mentor/assess?user_id=${userId}`, { method: "POST" }); }
  else if (key === "duka") { data = await api("/duka/scan", { method: "POST" }); }
  else if (key === "tiba") { data = await api("/tiba/symptoms", { method: "POST", body: JSON.stringify(["fever", "cough"]) }); }
  else if (key === "soko") { data = await api("/soko/match", { method: "POST" }); }
  else if (key === "sheria") { data = await api("/sheria/contract", { method: "POST", body: JSON.stringify({ type: "rental", parties: ["Alice", "Bob"], terms: { rent: "1000", duration: "12 months" } }) }); }
  else if (key === "kazi") { data = await api(`/kazi/gigs/${userId}`); }
  else if (key === "pesa") { data = await api("/pesa/chama", { method: "POST", body: JSON.stringify({ name: "Umoja Chama", members: ["A", "B", "C"], contribution: 20 }) }); }
  else if (key === "mtaa") { data = await api(`/mtaa/alerts/${userData?.location ?? "Nairobi"}`); }
  else if (key === "safiri") { currentPage = "safiri"; render(); return; }

  out.innerHTML = `<div class="card"><h2>${key.toUpperCase()} response</h2><pre style="white-space:pre-wrap;font-size:12px;overflow-x:auto;">${JSON.stringify(data, null, 2)}</pre></div>`;
}

// ============ BOOT ============
render();
