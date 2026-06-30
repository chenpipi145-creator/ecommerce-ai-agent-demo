const userPill = document.querySelector("#userPill");
const roleMetric = document.querySelector("#roleMetric");
const shopMetric = document.querySelector("#shopMetric");
const runMetric = document.querySelector("#runMetric");
const shopForm = document.querySelector("#shopForm");
const shopList = document.querySelector("#shopList");
const runList = document.querySelector("#runList");
const approvalList = document.querySelector("#approvalList");
const statusGrid = document.querySelector("#statusGrid");
const shopMessage = document.querySelector("#shopMessage");
const logoutBtn = document.querySelector("#logoutBtn");

const roleNames = {
  owner: "老板",
  operator: "运营",
  customer_service: "客服",
  media_buyer: "投手",
  admin: "管理员",
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (response.status === 401) {
    location.href = "/login";
    return data;
  }
  if (!response.ok) throw new Error(data.error || "请求失败");
  return data;
}

function renderShops(shops = []) {
  shopMetric.textContent = shops.length;
  if (!shops.length) {
    shopList.innerHTML = `<div class="empty">还没有绑定店铺。先添加一个店铺，后续真实平台 API 会接到这里。</div>`;
    return;
  }
  shopList.innerHTML = shops
    .map((shop) => `
      <div class="item">
        <strong>${escapeHtml(shop.shop_name)} · ${escapeHtml(shop.platform)}</strong>
        <span>状态：${escapeHtml(shop.status)} · token 数：${escapeHtml(shop.token_count || 0)}</span>
      </div>
    `)
    .join("");
}

function renderRuns(runs = []) {
  runMetric.textContent = runs.length;
  if (!runs.length) {
    runList.innerHTML = `<div class="empty">暂无 Agent 运行记录。进入工作台跑一次后会出现在这里。</div>`;
    return;
  }
  runList.innerHTML = runs
    .map((run) => {
      const date = new Date((run.created_at || 0) * 1000).toLocaleString();
      return `
        <div class="action-row">
          <div class="priority">${escapeHtml(run.mode || "mock")}</div>
          <div>
            <strong>${escapeHtml(run.intent || "电商运营")}</strong>
            <span>${escapeHtml(run.message)} · ${escapeHtml(date)}</span>
          </div>
        </div>
      `;
    })
    .join("");
}

function renderApprovals(tasks = []) {
  if (!tasks.length) {
    approvalList.innerHTML = `<div class="empty">暂无待复核任务。高风险售后、成交动作或模拟模式结果会在这里沉淀。</div>`;
    return;
  }
  approvalList.innerHTML = tasks
    .map((task) => {
      const date = new Date((task.created_at || 0) * 1000).toLocaleString();
      return `
        <div class="action-row">
          <div class="priority">${escapeHtml(task.risk_level || "medium")}</div>
          <div>
            <strong>${escapeHtml(task.title)}</strong>
            <span>${escapeHtml(task.status)} · ${escapeHtml(date)}</span>
          </div>
        </div>
      `;
    })
    .join("");
}

function renderStatus(status) {
  const items = [
    ["HTTPS", status.https ? "已启用" : "未启用", status.https ? "好" : "风险"],
    ["Groq", status.groq_configured ? "已配置" : "未配置", status.groq_configured ? "好" : "风险"],
    ["数据库", status.database || "-", "一般"],
    ["平台 OAuth", status.oauth || "-", "风险"],
    ["Token", status.token_storage || "-", "一般"],
    ["人工复核", status.approval || "-", "好"],
  ];
  statusGrid.innerHTML = items
    .map(([label, value, state]) => `
      <div class="status-card ${state === "风险" ? "danger" : ""}">
        <span>${escapeHtml(label)}</span>
        <strong>${escapeHtml(value)}</strong>
      </div>
    `)
    .join("");
}

async function loadDashboard() {
  const me = await fetchJson("/api/me");
  if (!me.user) {
    location.href = "/login";
    return;
  }
  userPill.textContent = `${me.user.name} · ${roleNames[me.user.role] || me.user.role}`;
  roleMetric.textContent = roleNames[me.user.role] || me.user.role;
  renderShops(me.shops || []);
  const [runs, approvals, status] = await Promise.all([
    fetchJson("/api/agent-runs"),
    fetchJson("/api/approval-tasks"),
    fetchJson("/api/system-status"),
  ]);
  renderRuns(runs.runs || []);
  renderApprovals(approvals.tasks || []);
  renderStatus(status);
}

shopForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  shopMessage.textContent = "正在保存店铺...";
  shopMessage.classList.remove("danger");
  try {
    const payload = Object.fromEntries(new FormData(shopForm).entries());
    const data = await fetchJson("/api/shops", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    renderShops(data.shops || []);
    shopForm.reset();
    shopMessage.textContent = "店铺已保存，token 已加密写入数据库。";
  } catch (error) {
    shopMessage.textContent = error.message;
    shopMessage.classList.add("danger");
  }
});

logoutBtn.addEventListener("click", async () => {
  await fetchJson("/api/logout", { method: "POST" });
  location.href = "/";
});

loadDashboard();
