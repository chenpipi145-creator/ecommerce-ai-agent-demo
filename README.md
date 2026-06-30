# 电商 AI 智能体 Demo

这是一个用于演示的电商运营 AI Agent MVP，覆盖客服售后、商品上架、推广成交、选品、营销投放和运营复盘。页面和后端都按“可展示、可讲解、可继续扩展”的方向做了升级，不再只是简单问答。

## 当前能演示什么

- 意图理解：自动判断用户是在问客服、售后、物流、订单、商品上架、选品、推广还是运营复盘。
- RAG 知识库：内置上架规范、标题优化、主图视频、SKU 定价、推广投放、售后和物流规则。
- 工具调用：模拟查询商品、订单、物流，生成售后方案、上架体检、上架素材包、推广成交方案、推广计划、运营诊断和选品排序。
- 结构化报告：输出执行摘要、分模块分析、指标卡、行动计划、下一步建议和风险提醒。
- 商家账号：支持注册、登录、退出、角色字段和登录会话。
- 一键体验：支持无需注册进入演示店铺，新注册账号也会自动创建演示店铺。
- 店铺绑定：支持保存淘宝/抖店/拼多多/京东/微信小店的店铺占位信息，并加密保存 API token。
- 数据隔离：Agent 运行记录按登录用户保存，后续真实店铺 API 可继续按 `user_id/shop_id` 隔离。
- 权限和审批：客服、投手、运营有基础 Agent 权限限制；高风险或模拟模式结果会进入待人工复核。
- 真实模型模式：配置 `GROQ_API_KEY` 后，后端会调用 Groq 的 OpenAI 兼容接口；没有 Key 时会自动进入本地演示模式。
- 前端工作台：左侧输入业务问题，中间显示 AI 运营报告，右侧显示 Agent 执行轨迹，下方展示工具调用、RAG 命中和行动清单。

## 核心 Agent 能力

### 客服售后 Agent

- 识别退款、退货、换货、补发、物流催件、投诉、差评和赔付场景
- 输出问题类型、风险等级、需要补充的凭证、客户回复话术和内部处理动作
- 模拟创建售后工单，并判断是否需要转人工复核

### 商品上架 Agent

- 检查资质、品牌授权、运费模板、售后政策、标题、主图、短视频、详情页、属性、SKU、风险词
- 生成标题方向、主图规划、视频脚本、详情页结构和 SKU 价格建议
- 输出发布状态、合规修复任务和发布前检查清单

### 推广成交 Agent

- 根据商品 ID 生成商品卖点、目标人群、推广标题和用户痛点话术
- 输出单品推广落地页结构、抖音/小红书/朋友圈/私域渠道文案
- 生成优惠券策略、广告素材建议、购买/加微信/进店 CTA 和成交风险提醒

### 广告投放/数据优化 Agent

- 分析 ROAS、点击率、转化率、退款率、搜索词、人群包和预算结构
- 输出预算策略、关键词出价动作、人群调整、素材 A/B 测试和止损监控规则
- 可用于演示直通车、引力魔方、淘宝客、万相台的投放决策逻辑

说明：当前版本不接真实店铺、广告账户或物流接口，所有执行动作都是本地样例数据上的模拟结果。

## 启动方式

```powershell
cd D:\Backup\Documents\小程序\ecommerce_agent_demo
python server.py
```

然后打开首页：

```text
http://127.0.0.1:8765
```

智能体工作台地址：

```text
http://127.0.0.1:8765/agent
```

商家登录和工作区：

```text
http://127.0.0.1:8765/login
http://127.0.0.1:8765/dashboard
```

## 配置 Groq API

启动前设置环境变量：

```powershell
$env:GROQ_API_KEY="你的 Groq Key"
$env:GROQ_MODEL="llama-3.3-70b-versatile"
python server.py
```

可选：

```powershell
$env:GROQ_BASE_URL="https://api.groq.com/openai/v1"
```

## 部署到 Render 免费版

项目已经包含 `render.yaml`，可以部署为 Render Web Service。

推荐配置：

- Runtime：Python
- Build Command：`pip install -r requirements.txt`
- Start Command：`python server.py`
- Plan：Free

Render 环境变量：

```text
HOST=0.0.0.0
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=你的 Groq Key
```

注意：不要把 `GROQ_API_KEY` 写进代码或提交到 GitHub，要在 Render 的 Environment 里填写。

## 主要接口

- `GET /`：打开首页 Hero 页面
- `GET /login`：商家登录/注册页
- `GET /dashboard`：商家工作区
- `GET /agent`：打开电商 AI Agent 工作台
- `GET /api/me`：当前登录用户和店铺
- `GET/POST /api/shops`：读取或新增当前用户店铺
- `GET /api/agent-runs`：读取当前用户 Agent 运行记录
- `GET /api/approval-tasks`：读取当前用户待人工复核任务
- `GET /api/system-status`：读取 HTTPS、Groq、OAuth、token、审批等上线状态
- `POST /api/demo-login`：进入演示商家账号
- `GET /api/demo-data`：返回示例商品、订单、物流和知识库
- `POST /api/chat`：运行电商 AI Agent，执行意图识别、RAG 检索、工具调用和模型生成

请求示例：

```json
{
  "message": "帮我给 P2002 做商品上架体检，检查资质、标题、主图视频、详情页、SKU和售后政策，告诉我能不能上架。"
}
```

## 适合展示的场景

- “启动客服售后 Agent，处理订单 E20260601002 的质量售后问题”
- “启动商品上架 Agent，给 P2002 做完整上架处理”
- “启动推广成交 Agent，给 P1001 生成单品推广页、渠道文案、优惠券策略和购买 CTA”
- “启动广告投放/数据优化 Agent，复盘 P1001 并给出投放动作”
- “帮我给 P2002 做商品上架体检”
- “给 P1001 生成标题、主图视频脚本、详情页结构和 SKU 定价建议”
- “P3003 最近 ROAS 和转化偏低，帮我做运营复盘”
- “从现有商品里选一个适合做下周活动的爆款”
- “订单 20260629001 物流延迟，帮我生成客服处理方案”

## 文件结构

```text
ecommerce_agent_demo/
  server.py          后端入口、Agent 编排、RAG、工具调用、Groq 接口
  render.yaml        Render 免费版部署配置
  requirements.txt   Python 依赖文件
  web/
    index.html       首页 Hero 页面
    login.html       登录/注册页面
    dashboard.html   商家工作区
    agent.html       电商 AI Agent 工作台
    styles.css       页面样式
    app.js           页面交互和接口调用
    auth.js          登录/注册交互
    dashboard.js     商家工作区交互
    home.js          首页聚光灯交互
  data/              SQLite 数据库目录，本地生成，不提交 Git
  README.md          使用说明
```
