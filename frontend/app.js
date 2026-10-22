// ⚠️ IMPORTANT: CHANGE THIS TO YOUR ACTUAL VERCEL BACKEND URL
const API = "https://jibu-ten.vercel.app"; 

let currentPage = "home";
let currentCheckoutItem = null;
let adminBypass = localStorage.getItem("jibu_admin_bypass") === "true";

async function api(path, opts = {}) {
  try {
    const res = await fetch(API + path, { headers: { "Content-Type": "application/json" }, ...opts });
    return await res.json();
  } catch (e) { console.error(e); return null; }
}

const app = document.getElementById("app");

function render() {
  document.querySelectorAll(".bottomnav button").forEach(b => b.classList.toggle("active", b.dataset.page === currentPage));
  
  // Update Admin Button UI
  const adminBtn = document.getElementById("adminToggle");
  if (adminBypass) {
    adminBtn.innerText = "Test Mode: ON";
    adminBtn.classList.add("active");
  } else {
    adminBtn.innerText = "Test Mode: OFF";
    adminBtn.classList.remove("active");
  }

  if (currentPage === "home") renderHome();
  else if (currentPage === "safiri") renderSafiri();
  else if (currentPage === "market") renderMarket();
  else if (currentPage === "modules") renderModules();
}

document.querySelectorAll(".bottomnav button").forEach(b => {
  b.addEventListener("click", () => { currentPage = b.dataset.page; render(); });
});

// ================= ADMIN TOGGLE =================
function toggleAdminMode() {
  adminBypass = !adminBypass;
  localStorage.setItem("jibu_admin_bypass", adminBypass);
  render();
}

async function renderHome() {
  app.innerHTML = `<div style="text-align:center; padding:40px;">Loading...</div>`;
  const user = await api("/users/u1");
  if (user && user.jibu_score) document.getElementById("userScore").innerText = `Score: ${user.jibu_score}`;
  
  const stats = await api("/stats");
  if (!stats) { app.innerHTML = `<div class="card">⚠️ Backend offline. Check API URL.</div>`; return; }
  
  app.innerHTML = `
    <h1>Welcome, ${user ? user.name.split(' ')[0] : 'User'} 👋</h1>
    <div class="subtitle">Living OS for South Africa</div>
    ${adminBypass ? '<div class="card" style="background:#fef3c7; color:#92400e;"><strong>Admin Mode Active:</strong> Payments bypassed for testing.</div>' : ''}
    
    <div class="stat-grid">
      <div class="stat blue"><div class="label">Users</div><div class="value">${stats.users.total}</div></div>
      <div class="stat green"><div class="label">Revenue</div><div class="value">R${stats.commerce.revenue}</div></div>
      <div class="stat orange"><div class="label">Safiri Ads</div><div class="value">${stats.safiri.ads}</div></div>
      <div class="stat red"><div class="label">Bounce Rate</div><div class="value">${stats.safiri.bounce_rate}%</div></div>
    </div>
    <div class="card">
      <h2>Safiri Ad Engine</h2>
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
  
  app.innerHTML = `<h1>Safiri (Ads)</h1><div class="subtitle">Mirror ads — no gimmicks</div>` +
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

const MODULES = [
  { id: "mentor", icon: "📚", name: "Mentor (Education)", desc: "AI tutoring & homework help. Connects students with local human tutors." },
  { id: "duka", icon: "🏪", name: "Duka (Retail POS)", desc: "Snap a photo of a shop shelf. AI tracks inventory and predicts stock-outs." },
  { id: "tiba", icon: "🏥", name: "Tiba (Healthcare)", desc: "AI symptom checker that instantly routes high-risk cases to a local nurse." },
  { id: "soko", icon: "🌾", name: "Soko (Marketplace)", desc: "Connects farmers directly to urban buyers and local delivery riders." },
  { id: "sheria", icon: "⚖️", name: "Sheria (Legal)", desc: "Generates local contracts (rentals, loans) with AI. Human paralegals review them." },
  { id: "kazi", icon: "💼", name: "Kazi (Gigs)", desc: "Finds local gig work (plumbing, cleaning) and upskills workers via micro-courses." },
  { id: "pesa", icon: "💰", name: "Pesa (Savings)", desc: "Digital 'Chama' groups. Tracks community savings and micro-loans." },
  { id: "mtaa", icon: "📰", name: "Mtaa (Community)", desc: "Hyperlocal alerts for traffic, weather, and security. Verified by locals." }
];

function renderModules() {
  app.innerHTML = `<h1>Jibu Modules</h1><div class="subtitle">Tap any module to see what it does</div>
    <div class="module-list">
      ${MODULES.map(m => `
        <div class="module-card" onclick="openModModal('${m.id}')">
          <div class="module-icon">${m.icon}</div>
          <div class="module-info">
            <h3>${m.name}</h3>
            <p>${m.desc.substring(0, 45)}...</p>
          </div>
        </div>
      `).join("")}
    </div>`;
}

let currentModule = null;
function openModModal(id) {
  currentModule = MODULES.find(m => m.id === id);
  document.getElementById("modTitle").innerText = `${currentModule.icon} ${currentModule.name}`;
  document.getElementById("modDesc").innerText = currentModule.desc;
  document.getElementById("moduleModal").classList.remove("hidden");
  
  const btn = document.getElementById("modTestBtn");
  btn.onclick = async () => {
    btn.innerText = "Testing...";
    const res = await api(`/module/${currentModule.id}`, { method: "POST" });
    btn.innerText = "Test Module";
    alert(`AI Response: \n\n${res.message}`);
    closeModModal();
  };
}

function closeModModal() { document.getElementById("moduleModal").classList.add("hidden"); }

// ================= PAYMENT & ADMIN BYPASS =================
function openCheckout(itemName, price) {
  currentCheckoutItem = { name: itemName, price: price };
  
  // GOD MODE: BYPASS PAYMENTS
  if (adminBypass) {
    alert(`✅ Test Purchase Successful!\n\nItem: ${itemName}\nAmount: R${price.toFixed(2)}\n\n(Payments bypassed via Admin Mode)`);
    return;
  }

  // NORMAL MODE: SHOW GATEWAY
  document.getElementById("payAmount").innerText = `Amount: R${price.toFixed(2)}`;
  document.getElementById("paymentModal").classList.remove("hidden");
}

function closeModal() { document.getElementById("paymentModal").classList.add("hidden"); }

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
      alert(`✅ Payment Bypassed by Backend!\n\nItem: ${currentCheckoutItem.name}`);
    } else {
      window.location.href = res.payment_url; 
    }
  } else {
    alert("Payment setup failed. Check backend.");
  }
}

// BOOT
render();
