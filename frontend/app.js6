const API = "https://jibu-ten.vercel.app"; // ⚠️ CHECK THIS URL

let currentPage = "home";
let appMode = localStorage.getItem("jibu_mode") || "demo"; 
let currentCheckoutItem = null;
let currentModule = null;

async function api(path, opts = {}) {
  const headers = { 
    "Content-Type": "application/json",
    "x-jibu-mode": appMode 
  };
  try {
    const res = await fetch(API + path, { headers, ...opts });
    return await res.json();
  } catch (e) { console.error(e); return null; }
}

function toggleMode() {
  appMode = appMode === "demo" ? "real" : "demo";
  localStorage.setItem("jibu_mode", appMode);
  render();
}

function navigate(page) {
  currentPage = page;
  document.querySelectorAll(".bottomnav button").forEach(b => b.classList.toggle("active", b.dataset.page === page));
  render();
}

const app = document.getElementById("app");

async function render() {
  const toggleBtn = document.getElementById("modeToggle");
  if (appMode === "demo") {
    toggleBtn.innerText = "DEMO";
    toggleBtn.classList.remove("real-mode");
  } else {
    toggleBtn.innerText = "REAL PRODUCTION";
    toggleBtn.classList.add("real-mode");
  }

  const user = await api("/users/u1");
  if (user && user.jibu_score) document.getElementById("userScore").innerText = `Score: ${user.jibu_score}`;

  if (currentPage === "home") renderHome();
  else if (currentPage === "safiri") renderSafiri();
  else if (currentPage === "market") renderMarket();
  else if (currentPage === "modules") renderModules();
}

async function renderHome() {
  app.innerHTML = `<div style="text-align:center; padding:40px;">Loading...</div>`;
  const stats = await api("/stats");
  if (!stats) { app.innerHTML = `<div class="card" style="color:red;">⚠️ Backend offline.</div>`; return; }

  const warningHTML = appMode === "real" 
    ? `<div class="card" style="background:#fee2e2; border-color:#fca5a5; color:#991b1b;"><strong>⚠️ REAL MODE ACTIVE:</strong> Connecting to production APIs.</div>`
    : `<div class="card" style="background:#fef3c7; border-color:#fcd34d; color:#92400e;"><strong>Demo Mode:</strong> Safe to test. Payments bypassed.</div>`;

  app.innerHTML = `
    <h1>Overview</h1>
    <div class="subtitle">Living OS for South Africa</div>
    ${warningHTML}
    <div class="stat-grid">
      <div class="stat blue"><div class="label">Users</div><div class="value">${stats.users.total}</div></div>
      <div class="stat green"><div class="label">Products</div><div class="value">${stats.commerce.products}</div></div>
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
  const ads = await api("/ads");
  const products = await api("/products");
  if (!ads || !products) return;
  
  app.innerHTML = `<h1>Safiri</h1><div class="subtitle">Smart Ads</div>` +
    ads.map(a => {
      const p = products.find(x => x.id === a.product_id);
      if(!p) return '';
      return `
        <div class="ad-card">
          <img src="${a.image_url}">
          <div class="ad-body">
            <div class="ad-headline">${a.headline}</div>
            <div class="ad-copy">${a.copy}</div>
            <div class="ad-bottom">
              <div class="ad-price">R${p.price.toFixed(2)}</div>
              <button class="buy-btn" onclick="openCheckout('${p.name}', ${p.price})">Buy</button>
            </div>
          </div>
        </div>`;
    }).join("");
}

async function renderMarket() {
  const products = await api("/products");
  if (!products) return;
  app.innerHTML = `<h1>Marketplace</h1><div class="subtitle">Direct from local sellers</div>` +
    products.map(p => `
      <div class="ad-card">
        <img src="${p.image_url}">
        <div class="ad-body">
          <div class="ad-headline">${p.name}</div>
          <div class="ad-copy">${p.description}</div>
          <div class="ad-bottom">
            <div class="ad-price">R${p.price.toFixed(2)}</div>
            <button class="buy-btn" onclick="openCheckout('${p.name}', ${p.price})">Buy</button>
          </div>
        </div>
      </div>
    `).join("");
}

const MODULES = [
  { id: "mentor", icon: "📚", name: "Mentor (Education)", desc: "AI tutoring & homework help." },
  { id: "duka", icon: "🏪", name: "Duka (Retail POS)", desc: "AI tracks inventory." },
  { id: "tiba", icon: "🏥", name: "Tiba (Healthcare)", desc: "AI symptom checker." },
  { id: "soko", icon: "🌾", name: "Soko (Farming)", desc: "Connects farmers to buyers." },
  { id: "sheria", icon: "⚖️", name: "Sheria (Legal)", desc: "Generates contracts." },
  { id: "kazi", icon: "💼", name: "Kazi (Gigs)", desc: "Finds local gig work." },
  { id: "pesa", icon: "💰", name: "Pesa (Savings)", desc: "Digital savings groups." },
  { id: "mtaa", icon: "📰", name: "Mtaa (Alerts)", desc: "Hyperlocal alerts." }
];

function renderModules() {
  app.innerHTML = `<h1>Modules</h1><div class="subtitle">Tap to test AI integrations</div>
    <div class="module-list">
      ${MODULES.map(m => `
        <div class="module-card" onclick="openModModal('${m.id}')">
          <div class="module-icon">${m.icon}</div>
          <div class="module-info"><h3>${m.name}</h3><p>${m.desc}</p></div>
        </div>
      `).join("")}
    </div>`;
}

function openModModal(id) {
  currentModule = MODULES.find(m => m.id === id);
  document.getElementById("modTitle").innerText = `${currentModule.icon} ${currentModule.name}`;
  document.getElementById("modDesc").innerText = currentModule.desc;
  document.getElementById("moduleModal").classList.remove("hidden");
  
  const btn = document.getElementById("modTestBtn");
  btn.innerText = "Run Simulation";
  btn.onclick = async () => {
    btn.innerText = "Processing...";
    const res = await api(`/module/${currentModule.id}`, { method: "POST" });
    btn.innerText = "Run Simulation";
    alert(`[Simulation Output]\n\n${res ? res.message : "Error"}`);
    closeModal();
  };
}

function openCheckout(itemName, price) {
  currentCheckoutItem = { name: itemName, price: price };
  document.getElementById("payAmount").innerText = `R${price.toFixed(2)}`;
  document.getElementById("paymentModal").classList.remove("hidden");
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
      cancel_url: window.location.href
    })
  });

  if (res && res.payment_url) {
    if (res.payment_url === "DEMO_BYPASS") {
      alert(`✅ Demo Purchase Successful!\n\nItem: ${currentCheckoutItem.name}\nAmount: R${currentCheckoutItem.price}\n\n(No real money charged)`);
    } else {
      window.location.href = res.payment_url; 
    }
  } else {
    alert("Checkout failed.");
  }
}

function closeModal() {
  document.querySelectorAll('.modal').forEach(m => m.classList.add('hidden'));
}

render();
