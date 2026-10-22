const API = "https://jibu-ten.vercel.app"; // ⚠️ CHANGE THIS TO YOUR ACTUAL VERCEL BACKEND URL
let currentPage = "home";
let userData = null;
let currentCheckoutItem = null;

async function api(path, opts = {}) {
  try {
    const res = await fetch(API + path, { headers: { "Content-Type": "application/json" }, ...opts });
    return await res.json();
  } catch (e) { return null; }
}

const app = document.getElementById("app");

function render() {
  document.querySelectorAll(".bottomnav button").forEach(b => b.classList.toggle("active", b.dataset.page === currentPage));
  if (currentPage === "home") renderHome();
  else if (currentPage === "safiri") renderSafiri();
  else if (currentPage === "market") renderMarket();
  else if (currentPage === "modules") renderModules();
}

document.querySelectorAll(".bottomnav button").forEach(b => {
  b.addEventListener("click", () => { currentPage = b.dataset.page; render(); });
});

async function renderHome() {
  app.innerHTML = `<div style="text-align:center; padding:40px;">Loading...</div>`;
  const stats = await api("/stats");
  const users = await api("/users");
  if (!stats) { app.innerHTML = `<div class="card">⚠️ Backend offline. Check API URL.</div>`; return; }
  
  app.innerHTML = `
    <h1>Welcome, Grace 👋</h1>
    <div class="subtitle">Living OS for South Africa</div>
    <div class="stat-grid">
      <div class="stat blue"><div class="label">Users</div><div class="value">${stats.users.total}</div></div>
      <div class="stat green"><div class="label">Revenue</div><div class="value">R${stats.commerce.revenue}</div></div>
      <div class="stat orange"><div class="label">Safiri Ads</div><div class="value">${stats.safiri.ads}</div></div>
      <div class="stat red"><div class="label">Bounce Rate</div><div class="value">${stats.safiri.bounce_rate}%</div></div>
    </div>
    <div class="card">
      <h2>Safiri Performance</h2>
      <div class="metric-row"><span>Impressions</span><span>${stats.safiri.impressions}</span></div>
      <div class="metric-row"><span>Clicks</span><span>${stats.safiri.clicks}</span></div>
      <div class="metric-row"><span>Conversion Rate</span><span>${stats.safiri.conversion_rate}%</span></div>
    </div>
  `;
}

async function renderSafiri() {
  app.innerHTML = `<div style="text-align:center; padding:40px;">Loading ads...</div>`;
  const ads = await api("/ads");
  const products = await api("/products");
  
  app.innerHTML = `<h1>Safiri</h1><div class="subtitle">Mirror ads — no gimmicks</div>` +
    ads.map(a => {
      const p = products.find(x => x.id === a.product_id);
      return `
        <div class="ad-card">
          <img src="${a.image_url}">
          <div class="ad-body">
            <div class="ad-headline">${a.headline}</div>
            <div class="ad-copy">${a.copy}</div>
            <div class="ad-bottom">
              <div class="ad-price">R${p.price.toFixed(2)}</div>
              <button class="buy-btn" onclick="openCheckout('${p.name}', ${p.price})">Buy Now</button>
            </div>
          </div>
        </div>`;
    }).join("");
}

async function renderMarket() {
  app.innerHTML = `<div style="text-align:center; padding:40px;">Loading market...</div>`;
  const products = await api("/products");
  app.innerHTML = `<h1>Marketplace</h1><div class="subtitle">Duka + Soko</div>` +
    products.map(p => `
      <div class="ad-card">
        <img src="${p.image_url}">
        <div class="ad-body">
          <div class="ad-headline">${p.name}</div>
          <div class="ad-copy">${p.description}</div>
          <div class="ad-bottom">
            <div class="ad-price">R${p.price.toFixed(2)}</div>
            <button class="buy-btn" onclick="openCheckout('${p.name}', ${p.price})">Buy Now</button>
          </div>
        </div>
      </div>
    `).join("");
}

function renderModules() {
  const mods = ["Mentor", "Duka", "Tiba", "Soko", "Sheria", "Kazi", "Pesa", "Mtaa", "Safiri"];
  app.innerHTML = `<h1>All Modules</h1><div class="subtitle">Tap to test</div>
    <div class="stat-grid">
      ${mods.map(m => `<div class="stat" style="text-align:center;"><div class="value" style="font-size:16px; color:#16a34a;">${m}</div></div>`).join("")}
    </div>`;
}

// ================= PAYMENT LOGIC =================
function openCheckout(itemName, price) {
  currentCheckoutItem = { name: itemName, price: price };
  document.getElementById("payAmount").innerText = `Amount: R${price.toFixed(2)}`;
  document.getElementById("paymentModal").classList.remove("hidden");
}

function closeModal() {
  document.getElementById("paymentModal").classList.add("hidden");
}

async function processPayment(provider) {
  if (!currentCheckoutItem) return;
  closeModal();
  
  const res = await api("/checkout", {
    method: "POST",
    body: JSON.stringify({
      provider: provider,
      amount: currentCheckoutItem.price,
      currency: "ZAR",
      item_name: currentCheckoutItem.name,
      email: "test@jibu.app",
      return_url: window.location.href,
      cancel_url: window.location.href,
      notify_url: API + "/webhook"
    })
  });

  if (res && res.payment_url) {
    window.location.href = res.payment_url; // Redirect to PayFast, Ozow, Stripe, etc.
  } else {
    alert("Payment setup failed. Check backend console.");
  }
}

render();
