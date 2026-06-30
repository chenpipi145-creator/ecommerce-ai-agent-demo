const input = document.querySelector("#messageInput");
const sendBtn = document.querySelector("#sendBtn");
const answerText = document.querySelector("#answerText");
const summaryText = document.querySelector("#summaryText");
const traceList = document.querySelector("#traceList");
const ragList = document.querySelector("#ragList");
const toolList = document.querySelector("#toolList");
const nextList = document.querySelector("#nextList");
const modePill = document.querySelector("#modePill");
const reportSections = document.querySelector("#reportSections");
const scoreList = document.querySelector("#scoreList");
const actionList = document.querySelector("#actionList");

const scenarioPrompts = {
  after_sales: "订单 E20260601002 的客户反馈便携榨汁杯坏了，想退款或补发。请启动客服售后 Agent，判断问题类型、风险等级、需要什么凭证、怎么回复客户、内部怎么处理。",
  listing: "请启动商品上架 Agent，给 P2002 做上架前完整处理：资质审核、标题优化、主图视频规划、详情页结构、SKU价格、合规修复任务和发布检查清单。",
  conversion: "请启动推广成交 Agent，给 P1001 生成一套可直接卖货的单品推广方案：商品卖点、推广标题、落地页结构、抖音/小红书/朋友圈/私域文案、优惠券策略、CTA 按钮和成交风险提醒。",
  ads: "请启动广告投放/数据优化 Agent，复盘 P1001 的直通车、引力魔方、搜索词、人群和转化数据，给出预算、出价、否定词、素材测试和止损监控规则。",
};

const defaultTrace = [
  { name: "意图理解", detail: "等待用户输入" },
  { name: "RAG 检索", detail: "等待检索知识库" },
  { name: "工具执行", detail: "等待调用商品/推广/广告/订单工具" },
  { name: "反馈生成", detail: "等待 Groq 输出运营报告" },
];

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function prettyJson(value) {
  return escapeHtml(JSON.stringify(value, null, 2));
}

function renderTrace(items = defaultTrace) {
  traceList.innerHTML = items
    .map((item, index) => `
      <div class="flow-step">
        <div class="step-index">${index + 1}</div>
        <div>
          <strong>${escapeHtml(item.name)}</strong>
          <span>${escapeHtml(item.detail)}</span>
        </div>
      </div>
    `)
    .join("");
}

function renderDocs(docs = []) {
  if (!docs.length) {
    ragList.innerHTML = `<div class="empty">暂无知识库命中。</div>`;
    return;
  }
  ragList.innerHTML = docs
    .map((doc) => `
      <div class="item">
        <strong>${escapeHtml(doc.title)} · ${escapeHtml(doc.category)}</strong>
        <span>${escapeHtml(doc.content)}</span>
      </div>
    `)
    .join("");
}

function renderTools(calls = []) {
  if (!calls.length) {
    toolList.innerHTML = `<div class="empty">暂无工具调用。</div>`;
    return;
  }
  toolList.innerHTML = calls
    .map((call) => `
      <details class="tool-item" open>
        <summary>${escapeHtml(call.name)}</summary>
        <pre>${prettyJson(call.output)}</pre>
      </details>
    `)
    .join("");
}

function renderNext(actions = [], risks = []) {
  const blocks = [];
  for (const action of actions) {
    blocks.push(`<div class="item"><strong>下一步</strong><span>${escapeHtml(action)}</span></div>`);
  }
  for (const risk of risks) {
    blocks.push(`<div class="item risk"><strong>风险提醒</strong><span>${escapeHtml(risk)}</span></div>`);
  }
  nextList.innerHTML = blocks.join("") || `<div class="empty">暂无额外动作。</div>`;
}

function renderReportSections(sections = []) {
  if (!sections.length) {
    reportSections.innerHTML = `<div class="empty">暂无分模块报告。</div>`;
    return;
  }
  reportSections.innerHTML = sections
    .map((section) => `
      <section class="report-block">
        <h3>${escapeHtml(section.title)}</h3>
        <ul>
          ${(section.items || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
        </ul>
      </section>
    `)
    .join("");
}

function renderScores(scores = []) {
  if (!scores.length) {
    scoreList.innerHTML = `<div class="empty">运行后展示商品、转化、推广等指标。</div>`;
    return;
  }
  scoreList.innerHTML = scores
    .map((score) => `
      <div class="score-card ${/风险|差|低/.test(score.status || "") ? "danger" : ""}">
        <span>${escapeHtml(score.label)}</span>
        <strong>${escapeHtml(score.value)}</strong>
        <em>${escapeHtml(score.status)}</em>
        <p>${escapeHtml(score.note)}</p>
      </div>
    `)
    .join("");
}

function renderActions(actions = []) {
  if (!actions.length) {
    actionList.innerHTML = `<div class="empty">运行后展示 P0/P1/P2 执行动作。</div>`;
    return;
  }
  actionList.innerHTML = actions
    .map((item) => `
      <div class="action-row">
        <div class="priority">${escapeHtml(item.priority || "P1")}</div>
        <div>
          <strong>${escapeHtml(item.action)}</strong>
          <span>${escapeHtml(item.owner || "运营")} · 衡量：${escapeHtml(item.metric || "业务指标")}</span>
        </div>
      </div>
    `)
    .join("");
}

function renderData(data) {
  modePill.textContent = data.mode === "groq" ? "Groq 模式" : "模拟模式";
  summaryText.textContent = data.executive_summary || data.summary || "已生成分析。";
  answerText.textContent = data.reply || "没有生成回复。";
  renderTrace(data.trace || defaultTrace);
  renderDocs(data.retrieved_docs || []);
  renderTools(data.tool_calls || []);
  renderNext(data.next_actions || [], data.risk_notes || []);
  renderReportSections(data.report_sections || []);
  renderScores(data.scorecards || []);
  renderActions(data.action_plan || []);
}

async function runAgent() {
  const message = input.value.trim();
  if (!message) {
    answerText.textContent = "请先输入一个电商业务问题。";
    return;
  }

  sendBtn.disabled = true;
  sendBtn.textContent = "智能体运行中...";
  modePill.textContent = "执行中";
  summaryText.textContent = "正在识别场景、检索知识库、调用业务工具...";
  renderTrace([
    { name: "意图理解", detail: "正在识别..." },
    { name: "RAG 检索", detail: "等待中" },
    { name: "工具执行", detail: "等待中" },
    { name: "反馈生成", detail: "等待中" },
  ]);

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "请求失败");
    renderData(data);
  } catch (error) {
    modePill.textContent = "出错";
    summaryText.textContent = "运行失败";
    answerText.textContent = `运行失败：${error.message}`;
  } finally {
    sendBtn.disabled = false;
    sendBtn.textContent = "运行智能体";
  }
}

document.querySelectorAll("[data-prompt]").forEach((button) => {
  button.addEventListener("click", () => {
    input.value = button.dataset.prompt;
    runAgent();
  });
});

sendBtn.addEventListener("click", runAgent);
renderTrace(defaultTrace);
renderDocs([]);
renderTools([]);
renderNext([], []);
renderReportSections([]);
renderScores([]);
renderActions([]);

const scenario = new URLSearchParams(window.location.search).get("scenario");
if (scenarioPrompts[scenario]) {
  input.value = scenarioPrompts[scenario];
  runAgent();
}
