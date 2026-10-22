// ⚠️ IMPORTANT: PUT YOUR VERCEL BACKEND URL HERE
const API = "https://jibu-ten.vercel.app"; 

let currentPage = "home";
let adminBypass = localStorage.getItem("jibu_bypass") === "true";
let currentCheckoutItem = null;
let currentModule = null;

// ================= ROUTING =================
function navigate(page) {
  currentPage = page;
  document.querySelectorAll(".bottomnav button").forEach(b => b.classList.toggle("active", b.dataset.page === page));
  render();
}

// ================= API HELPER =================
async function api(path, opts = {}) {
  try {
    const res = await fetch(API + path, { headers: { "Content-Type": "application/json" }, ...opts });
    return await res.json();
  } catch (e) { console.error("API Error:", e); return null; }
}

// ================= UI RENDERER =================
const app = document.getElementById("app");

async function render() {
  // Update Header
  const adminBtn = document.getElementById("adminToggle");
  if (adminBypass) {
    adminBtn.innerText = "Demo: ON";
    adminBtn.classList.add("active");
  } else {
    adminBtn.innerText = "Demo: OFF";
    adminBtn.classList.remove("active");
  }

  // Load User Score
  const user = await api("/users/u1");
  if (user) document.getElementById("userScore").innerText = `Score: ${user.jibu_score}`;

  // Render Pages
  if (currentPage === "home") renderHome();
  else if (currentPage === "safiri") renderSafiri();
  else if (currentPage === "market") renderMarket();
  else if (currentPage === "modules") renderModules();
}

// ================= PAGES =================
async function renderHome() {
  app.innerHTML = `<div style="text-align:center; padding:40px; color:#6b7280;">Loading Dashboard...</div>`;
  const stats = await api("/stats");
  if (!stats) { app.innerHTML = `<div class="card" style="color:red;">⚠️ Backend offline.</div>`; return; }

  app.innerHTML = `
    <h1>Overview</h1>
    <div class="subtitle">Living OS for South Africa</div>
    ${adminBypass ? '<div class="card" style="background:#fef3c7; border-color:#fcd34d;"><strong>Demo Mode Active:</strong> Payment gateways are bypassed.</div>' : ''}
    
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
  app.innerHTML = `<div style="text-align:center; padding:40px; color:#6b7280;">Loading Ads...</div>`;
  const ads = await api("/ads");
  const products = await api("/products");
  
  if (!ads) return;
  app.innerHTML = `<h1>Safiri</h1><div class="subtitle">Smart Ads</div>` +
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
              <button class="buy-btn" onclick="openCheckout('${p.name}', ${p.price})">Buy</button>
            </div>
          </div>
        </div>`;
    }).join("");
}

async function renderMarket() {
  app.innerHTML = `<div style="text-align:center; padding:40px; color:#6b7280;">Loading Market...</div>`;
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
  { id: "mentor", icon: "📚", name: "Mentor (Education)", desc: "AI tutoring & homework help. Connects students with local human tutors." },
  { id: "duka", icon: "🏪", name: "Duka (Retail POS)", desc: "Snap a photo of a shop shelf. AI tracks inventory and predicts stock-outs." },
  { id: "tiba", icon: "🏥", name: "Tiba (Healthcare)", desc: "AI symptom checker that instantly routes high-risk cases to a local nurse." },
  { id: "soko", icon: "🌾", name: "Soko (Farming)", desc: "Connects farmers directly to urban buyers and local delivery riders." },
  { id: "sheria", icon: "⚖️", name: "Sheria (Legal)", desc: "Generates local contracts. Human paralegals review them." },
  { id: "kazi", icon: "💼", name: "Kazi (Gigs)", desc: "Finds local gig work and upskills workers via micro-courses." },
  { id: "pesa", icon: "💰", name: "Pesa (Savings)", desc: "Digital 'Chama' groups. Tracks community savings and micro-loans." },
  { id: "mtaa", icon: "📰", name: "Mtaa (Alerts)", desc: "Hyperlocal alerts for traffic, weather, and security. Verified by locals." }
];

function renderModules() {
  app.innerHTML = `<h1>Modules</h1><div class="subtitle">Tap to test the AI integrations</div>
    <div class="module-list">
      ${MODULES.map(m => `
        <div class="module-card" onclick="openModModal('${m.id}')">
          <div class="module-icon">${m.icon}</div>
          <div class="module-info">
            <h3>${m.name}</h3>
            <p>${m.desc}</p>
          </div>
        </div>
      `).join("")}
    </div>`;
}

// ================= ACTIONS & MODALS =================
function toggleAdminMode() {
  adminBypass = !adminBypass;
  localStorage.setItem("jibu_bypass", adminBypass);
  render();
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
    alert(`[Simulated AI Output]\n\n${res.message}`);
    closeModal();
  };
}

function openCheckout(itemName, price) {
  currentCheckoutItem = { name: itemName, price: price };
  
  if (adminBypass) {
    alert(`✅ [Demo Bypass]\n\nItem: ${itemName}\nAmount: R${price.toFixed(2)}\n\nPayments skipped.`);
    return;
  }

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
      cancel_url: window.location.href,
      notify_url: API + "/webhook"
    })
  });

  if (res && res.payment_url) {
    if (res.payment_url === "TEST_MODE_BYPASS") {
      alert(`✅ Payment Bypassed by Backend!`);
    } else {
      window.location.href = res.payment_url; 
    }
  }
}

function closeModal() {
  document.querySelectorAll('.modal').forEach(m => m.classList.add('hidden'));
}

// Start Application
render();
