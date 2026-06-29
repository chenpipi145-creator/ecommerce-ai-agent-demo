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

const defaultTrace = [
  { name: "意图理解", detail: "等待用户输入" },
  { name: "RAG 检索", detail: "等待检索知识库" },
  { name: "工具执行", detail: "等待调用商品/广告/订单工具" },
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
