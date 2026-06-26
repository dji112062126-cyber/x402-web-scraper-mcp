#!/usr/bin/env python3
"""Generate an HTML AI report that opens in any browser."""

import os

HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>2026年6月 AI行业最新资讯报告</title>
<style>
:root {
  --bg: #0D111A;
  --card: #121824;
  --accent: #6C5CFF;
  --accent2: #00BFA5;
  --accent3: #FF6B6B;
  --accent4: #FFD93D;
  --white: #FFFFFF;
  --gray: #B0B8C4;
  --dim: #6B7280;
  --line: #1E2633;
}
* { margin:0; padding:0; box-sizing:border-box; }
body { background:var(--bg); color:var(--white); font-family:'Segoe UI','Microsoft YaHei',sans-serif; line-height:1.6; }

/* ── sections ── */
.section { min-height:100vh; padding:60px 80px; display:flex; flex-direction:column; justify-content:center; border-bottom:1px solid var(--line); }
.section-header { margin-bottom:50px; }
.section-header h2 { font-size:32px; margin-bottom:6px; }
.section-header .sub { color:var(--dim); font-size:14px; }
.accent-bar { width:60px; height:4px; background:var(--accent); border-radius:2px; margin-bottom:20px; }

/* ── title page ── */
.title-page { text-align:center; }
.title-page .year { color:var(--dim); font-size:20px; margin-bottom:10px; }
.title-page h1 { font-size:52px; font-weight:800; margin-bottom:20px; background:linear-gradient(135deg, var(--accent), var(--accent2)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.title-page .subtitle { color:var(--accent2); font-size:18px; margin-bottom:60px; }
.title-page .source { color:var(--dim); font-size:12px; }

/* ── toc ── */
.toc-item { display:flex; align-items:flex-start; padding:18px 0; border-bottom:1px solid var(--line); }
.toc-num { font-size:28px; font-weight:800; color:var(--accent); min-width:60px; }
.toc-title { font-size:22px; font-weight:700; }
.toc-desc { font-size:13px; color:var(--dim); margin-top:4px; }

/* ── cards ── */
.card-row { display:flex; gap:20px; margin-bottom:20px; }
.card { background:var(--card); border-radius:12px; padding:24px; flex:1; position:relative; overflow:hidden; }
.card::before { content:''; position:absolute; left:0; top:12px; bottom:12px; width:4px; border-radius:2px; }
.card.accent::before { background:var(--accent); }
.card.accent2::before { background:var(--accent2); }
.card.accent3::before { background:var(--accent3); }
.card.accent4::before { background:var(--accent4); }
.card h4 { font-size:16px; margin-bottom:12px; color:var(--white); }
.card ul { list-style:none; font-size:13px; color:var(--gray); }
.card li { padding:3px 0; }
.card li::before { content:'▸ '; color:var(--accent2); font-size:10px; }

/* ── table ── */
table { width:100%; border-collapse:collapse; font-size:13px; margin:10px 0; }
th { background:var(--accent); color:var(--white); padding:10px 14px; text-align:left; font-weight:600; }
td { padding:10px 14px; border-bottom:1px solid var(--line); color:var(--gray); }
tr:nth-child(even) td { background:var(--card); }

/* ── insight box ── */
.insight { background:var(--card); border-radius:12px; padding:24px; margin:20px 0; border-left:4px solid var(--accent4); }
.insight h4 { color:var(--accent4); font-size:16px; margin-bottom:10px; }
.insight p, .insight li { font-size:13px; color:var(--gray); }

/* ── stats grid ── */
.stats { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; }
.stat-box { background:var(--card); border-radius:10px; padding:20px; text-align:center; }
.stat-label { font-size:12px; color:var(--dim); margin-bottom:6px; }
.stat-value { font-size:20px; font-weight:800; color:var(--accent2); margin-bottom:6px; }
.stat-note { font-size:11px; color:var(--gray); }

/* ── trends ── */
.trend { background:var(--card); border-radius:10px; padding:20px 24px; margin-bottom:16px; display:flex; gap:20px; align-items:flex-start; }
.trend-num { font-size:13px; font-weight:800; min-width:80px; padding:4px 12px; border-radius:20px; text-align:center; }
.trend-body h4 { font-size:18px; margin-bottom:4px; }
.trend-body p { font-size:13px; color:var(--gray); }

/* ── highlight bar ── */
.highlight { background:var(--card); border-radius:10px; padding:16px 24px; font-size:15px; font-weight:700; color:var(--accent4); }

/* ── picks grid ── */
.picks-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:12px; }
.pick { background:var(--card); border-radius:8px; padding:14px 18px; }
.pick .scene { color:var(--gray); font-size:12px; }
.pick .model { color:var(--accent4); font-size:14px; font-weight:700; margin:4px 0; }
.pick .why { color:var(--dim); font-size:11px; }

/* ── comparison dims ── */
.dim-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-top:10px; }
.dim-item { background:var(--card); border-radius:8px; padding:14px; text-align:center; }
.dim-item .label { font-size:12px; color:var(--gray); margin-bottom:4px; }
.dim-item .winner { font-size:13px; font-weight:700; }

/* ── footer ── */
.page-num { text-align:right; color:var(--dim); font-size:12px; margin-top:40px; }
.summary { font-size:14px; color:var(--gray); line-height:2; }
.summary li::marker { color:var(--accent2); }
</style>
</head>
<body>

<!-- ═══════════════ SLIDE 1 — TITLE ═══════════════ -->
<div class="section title-page">
  <div class="accent-bar" style="margin:0 auto 30px"></div>
  <div class="year">2026 年 6 月</div>
  <h1>AI 行业最新资讯报告</h1>
  <div class="subtitle">智能体时代全面到来 · 模型格局深度解析 · 行业风口成功案例</div>
  <div style="margin-top:80px">
    <div class="stats">
      <div class="stat-box"><div class="stat-value">10,000+</div><div class="stat-label">MCP 服务器</div></div>
      <div class="stat-box"><div class="stat-value">$3056亿</div><div class="stat-label">AI 50 总融资</div></div>
      <div class="stat-box"><div class="stat-value">&gt;50%</div><div class="stat-label">Agent 流量占比</div></div>
      <div class="stat-box"><div class="stat-value">6000+</div><div class="stat-label">中国 AI 企业</div></div>
    </div>
  </div>
  <div class="source" style="margin-top:80px">来源: Computex 2026 · Microsoft Build · Snowflake Summit · Forbes AI 50 · Artificial Analysis · LiveBench</div>
</div>

<!-- ═══════════════ SLIDE 2 — 目录 ═══════════════ -->
<div class="section">
  <div class="section-header"><div class="accent-bar"></div><h2>目  录</h2><div class="sub">CONTENTS</div></div>
  <div>
    <div class="toc-item"><span class="toc-num">01</span><div><div class="toc-title">AI Agent 最新动态</div><div class="toc-desc">从 Computex 到 Microsoft Build，Agent 全面接管数字生活</div></div></div>
    <div class="toc-item"><span class="toc-num">02</span><div><div class="toc-title">Agent 框架全景</div><div class="toc-desc">LangChain · CrewAI · AutoGPT · AutoGen … 7 大主流框架对比与选型</div></div></div>
    <div class="toc-item"><span class="toc-num">03</span><div><div class="toc-title">Agent 协议标准化</div><div class="toc-desc">MCP vs A2A — AI Agent 生态的 TCP/IP 时刻</div></div></div>
    <div class="toc-item"><span class="toc-num">04</span><div><div class="toc-title">大模型强弱对比</div><div class="toc-desc">Opus 4.8 vs GPT-5.5 vs Gemini 3.1 全方位 Benchmark 对比</div></div></div>
    <div class="toc-item"><span class="toc-num">05</span><div><div class="toc-title">AI 风口行业 & 成功案例</div><div class="toc-desc">金融 · 医疗 · 教育 · 情感AI · 机器人 · 出海</div></div></div>
    <div class="toc-item"><span class="toc-num">06</span><div><div class="toc-title">行业趋势 & 未来展望</div><div class="toc-desc">2026 关键判断与战略建议</div></div></div>
  </div>
</div>

<!-- ═══════════════ SLIDE 3 — AI Agent 最新动态 ═══════════════ -->
<div class="section">
  <div class="section-header"><div class="accent-bar"></div><h2>01  AI Agent 最新动态</h2><div class="sub">2026 年 6 月 — 智能体时代全面到来</div></div>

  <div class="highlight" style="margin-bottom:24px">🔥 2026 被定义为 "Agent 元年" — NVIDIA CEO 黄仁勋: AI 已从生成式 AI 全面进入 Agentic AI 时代</div>

  <div class="card-row">
    <div class="card accent"><h4>🖥️ Computex 2026 台北</h4><ul>
      <li>NVIDIA RTX Spark: Arm+Blackwell+128GB 统一内存</li>
      <li>Vera Rubin: 首个专为 Agent 设计的架构投产</li>
      <li>Nemotron 3 Ultra: 推理速度 5×↑ 成本降 30%</li>
      <li>高通: 2026 是 Agent 之年，Agent 成数字生活中心</li>
      <li>Intel Arc G3 + OpenVINO 物理 AI 开源机器人库</li></ul></div>
    <div class="card accent2"><h4>☁️ Microsoft Build 2026</h4><ul>
      <li>MAI-Thinking-1: 微软首个推理模型，企业级</li>
      <li>Copilot Super App 确认开发中，夏末预览</li>
      <li>Agent Mode 成为 M365 Copilot 默认模式</li>
      <li>Azure AI Foundry 深度支持多模型部署</li>
      <li>GitHub Copilot 覆盖完整开发工作流</li></ul></div>
    <div class="card accent3"><h4>🏢 更多巨头动态</h4><ul>
      <li>Meta 发布 Business Agent，100 万+企业入驻</li>
      <li>Snowflake 推 Cortex Code + Intelligence 平台</li>
      <li>Anthropic Claude Code 支持数百子 Agent 动态编排</li>
      <li>Google 发布 Omni(any-to-any)，推 Antigravity 平台</li>
      <li>Cloudflare: Agentic 流量首次超过人类流量</li></ul></div>
  </div>

  <div class="stats">
    <div class="stat-box"><div class="stat-label">Agent 流量占比</div><div class="stat-value">超 50%</div><div class="stat-note">Agent 流量首次超过人类网页流量</div></div>
    <div class="stat-box"><div class="stat-label">MCP 生态</div><div class="stat-value">10,000+ 服务器</div><div class="stat-note">9700 万月 SDK 下载</div></div>
    <div class="stat-box"><div class="stat-label">AI Agent 框架</div><div class="stat-value">400+ 预置工具</div><div class="stat-note">LangChain 生态最大</div></div>
    <div class="stat-box"><div class="stat-label">企业 AI 支出</div><div class="stat-value">$3056 亿</div><div class="stat-note">AI 50 合计融资额</div></div>
  </div>
</div>

<!-- ═══════════════ SLIDE 4 — Agent 框架全景 ═══════════════ -->
<div class="section">
  <div class="section-header"><div class="accent-bar"></div><h2>02  Agent 框架全景</h2><div class="sub">2026 主流框架对比 · 从链式到图式 · 多 Agent 协作成熟</div></div>

  <table>
    <tr><th>框架</th><th>核心优势</th><th>最佳场景</th><th>许可证</th><th>参考价格</th></tr>
    <tr><td style="color:white;font-weight:700">LangChain / LangGraph</td><td>最大生态 (400+ 工具)；图式工作流引擎</td><td>RAG / 聊天机器人 / 企业工作流</td><td>开源</td><td>免费</td></tr>
    <tr><td style="color:white;font-weight:700">CrewAI</td><td>多 Agent 角色协作；任务编排四阶段模型</td><td>内容生产 / 多步骤业务流程</td><td>开源 + 付费</td><td>$99/月起</td></tr>
    <tr><td style="color:white;font-weight:700">Microsoft AutoGen</td><td>对话驱动多 Agent；递归反思；并行执行</td><td>研究报告 / 代码生成 / 复杂分析</td><td>MIT 开源</td><td>免费</td></tr>
    <tr><td style="color:white;font-weight:700">Semantic Kernel</td><td>企业治理；Azure 集成；.NET+Python</td><td>金融 / 医疗受监管行业</td><td>开源</td><td>免费 + Azure</td></tr>
    <tr><td style="color:white;font-weight:700">OpenAI Agents SDK</td><td>原生 OpenAI 生态；工具调用最轻量</td><td>GPT 原生应用 / 快速原型</td><td>按 Token</td><td>按量计费</td></tr>
    <tr><td style="color:white;font-weight:700">AutoGPT</td><td>首个自主目标驱动 Agent；社区庞大</td><td>自主实验 / 兴趣探索</td><td>开源</td><td>免费</td></tr>
    <tr><td style="color:white;font-weight:700">LlamaIndex / Mastra / Pydantic</td><td>数据密集 RAG / TS 优先 / 强类型</td><td>文档问答 / JS 团队 / Pydantic 用户</td><td>开源</td><td>免费</td></tr>
  </table>

  <div class="insight"><h4>2026 关键架构趋势</h4>
    <p>链式执行 → 动态执行图 (分支/循环/合并)；工具自动发现与自适应调用成为标配；多 Agent 协作从"任务接力"升级为组织级协同模式；可观测性+评测层成为生产级部署标配 (LangSmith / Langfuse)。</p>
    <p style="margin-top:8px;color:var(--accent3)">⚠ 挑战: 复杂任务端到端成功率 ≤85%；自主规划型 Agent 单任务平均 50 次调用，成本控制仍是瓶颈</p>
  </div>
</div>

<!-- ═══════════════ SLIDE 5 — Agent 协议标准化 ═══════════════ -->
<div class="section">
  <div class="section-header"><div class="accent-bar"></div><h2>03  Agent 协议标准化</h2><div class="sub">MCP vs A2A — AI 世界的 TCP/IP 时刻</div></div>

  <div class="card-row">
    <div class="card accent"><h4>🔌 MCP (Model Context Protocol)</h4><ul>
      <li>创建方: Anthropic (2024.11)，捐赠 Linux Foundation AAIF</li>
      <li>定位: AI 模型的「USB-C 接口」— 任何模型接入任何工具</li>
      <li>架构: Client → Server (JSON-RPC 2.0 over stdio/HTTP)</li>
      <li>生态: 10,000+ MCP 服务器，9700 万月 SDK 下载</li>
      <li>支持: Claude / ChatGPT / Gemini / VS Code / Cursor</li>
      <li>最新: 2025-06-18 版，新增 OAuth 2.0 资源指示器</li></ul></div>
    <div class="card accent2"><h4>🤝 A2A (Agent-to-Agent Protocol)</h4><ul>
      <li>创建方: Google (2025.04)，捐赠 Linux Foundation</li>
      <li>定位: Agent 之间的「HTTP」— 跨厂商 Agent 发现与协作</li>
      <li>架构: Peer → Peer (HTTP + JSON-RPC + SSE; Agent Card 发现)</li>
      <li>生态: 100+ 公司支持 (Google/AWS/MS/Cisco/SAP/Salesforce)</li>
      <li>里程碑: v1.0 达成，合并 IBM ACP 协议</li>
      <li>特性: 任务状态机 (SUBMITTED→WORKING→COMPLETED/FAILED)</li></ul></div>
  </div>

  <div class="insight">
    <h4>✅ 行业共识: 互补而非竞争 — 两者并用</h4>
    <ul style="list-style:none">
      <li>MCP: 解决「我的 Agent 如何调用工具/数据？」 — 单 Agent 工具接入标准</li>
      <li>A2A: 解决「我的 Agent 如何与另一个 Agent 对话？」 — 多 Agent 跨厂商协作标准</li>
      <li>典型架构: 工具调用 → MCP，跨团队/跨厂商 Agent 协作 → A2A，统一网关做安全管控</li>
    </ul>
  </div>
</div>

<!-- ═══════════════ SLIDE 6 — 大模型对比 (一) ═══════════════ -->
<div class="section">
  <div class="section-header"><div class="accent-bar"></div><h2>04  大模型强弱对比 (一)</h2><div class="sub">Claude Opus 4.8 vs GPT-5.5 vs Gemini 3.1 Pro — 全方位 Benchmark 对比</div></div>

  <div class="card-row">
    <div class="card" style="--c:#D47B3A"><h4 style="color:#D47B3A">🟠 Claude Opus 4.8</h4><ul>
      <li>💻 SWE-bench Pro: 69.2% 🥇 (领先 GPT 10.6%)</li>
      <li>🧠 推理 (LiveBench): 89.71 🥇</li>
      <li>🤖 Agent (ARC-AGI-3): 1.5% 🥇 (4× 对手)</li>
      <li>🌐 实时网页: 84% 🥇</li>
      <li>🎯 可靠性: 幻觉率 35.9% 🥇 (最诚实)</li>
      <li>💰 $5 / $25 每百万 token</li>
    </ul></div>
    <div class="card" style="--c:#10A37F"><h4 style="color:#10A37F">🟢 GPT-5.5</h4><ul>
      <li>📐 数学 (LiveBench): 96.32 🥇</li>
      <li>💻 Terminal-Bench: 82.7% 🥇</li>
      <li>🧠 GPQA Diamond: ~93.6%</li>
      <li>🏆 LiveBench 全科: 80.71 🥇</li>
      <li>👁️ 多模态/视觉: 领先 Claude</li>
      <li>💰 $5 / $30 每百万 token</li>
    </ul></div>
    <div class="card" style="--c:#4285F4"><h4 style="color:#4285F4">🔵 Gemini 3.1 Pro</h4><ul>
      <li>📋 指令遵循 (IF): 79.10 🥇</li>
      <li>👁️ ScienceQA Vision: 61.86% 🥇</li>
      <li>🏆 LiveCodeBench Elo: 2887 🥇</li>
      <li>💻 SWE-bench Verified: 80.6% (Top 3)</li>
      <li>💰 性价比最优: $2 / $12 每百万 token</li>
      <li>📏 1M 上下文窗口</li>
    </ul></div>
  </div>

  <div class="insight"><h4>📊 核心维度雷达对比</h4>
    <div class="dim-grid" style="margin-top:12px">
      <div class="dim-item"><div class="label">Agent/自主工作</div><div class="winner" style="color:#D47B3A">🏆 Claude</div></div>
      <div class="dim-item"><div class="label">编码/修Bug</div><div class="winner" style="color:#D47B3A">🏆 Claude</div></div>
      <div class="dim-item"><div class="label">数学</div><div class="winner" style="color:#10A37F">🏆 GPT-5.5</div></div>
      <div class="dim-item"><div class="label">通用全科</div><div class="winner" style="color:#10A37F">🏆 GPT-5.5</div></div>
      <div class="dim-item"><div class="label">指令遵循</div><div class="winner" style="color:#4285F4">🏆 Gemini</div></div>
      <div class="dim-item"><div class="label">视觉/多模态</div><div class="winner" style="color:#4285F4">🏆 Gemini</div></div>
      <div class="dim-item"><div class="label">性价比</div><div class="winner" style="color:#4285F4">🏆 Gemini</div></div>
      <div class="dim-item"><div class="label">可靠性/诚实</div><div class="winner" style="color:#D47B3A">🏆 Claude</div></div>
    </div>
  </div>
</div>

<!-- ═══════════════ SLIDE 7 — 大模型对比 (二) ═══════════════ -->
<div class="section">
  <div class="section-header"><div class="accent-bar"></div><h2>04  大模型强弱对比 (二)</h2><div class="sub">开源模型 · 定价对比 · 选型建议</div></div>

  <div style="display:flex; gap:40px">
    <div style="flex:1">
      <h4 style="margin-bottom:14px;color:var(--accent2)">💰 定价对比 (每百万 Token)</h4>
      <table>
        <tr><th>模型</th><th>输入</th><th>输出</th><th>类型</th></tr>
        <tr><td style="color:white">DeepSeek V4-Flash</td><td>$0.04</td><td>C</td><td>开源 / MIT</td></tr>
        <tr><td style="color:white">Gemini 3.1 Flash</td><td>$0.30</td><td>$2.50</td><td>商业</td></tr>
        <tr><td style="color:white">DeepSeek V4-Pro</td><td>$0.44</td><td>$0.87</td><td>开源 / MIT</td></tr>
        <tr><td style="color:white">Gemini 3.1 Pro</td><td>$2.00</td><td>$12.00</td><td>商业</td></tr>
        <tr><td style="color:white">GPT-5.4</td><td>$2.50</td><td>$15.00</td><td>商业</td></tr>
        <tr><td style="color:white">Claude Sonnet 4.6</td><td>$3.00</td><td>$15.00</td><td>商业</td></tr>
        <tr><td style="color:white;font-weight:700">Claude Opus 4.8</td><td>$5.00</td><td>$25.00</td><td>商业</td></tr>
        <tr><td style="color:white;font-weight:700">GPT-5.5</td><td>$5.00</td><td>$30.00</td><td>商业</td></tr>
      </table>
    </div>
    <div style="flex:1">
      <h4 style="margin-bottom:14px;color:var(--accent2)">🔓 开源/开放权重模型 Top 5</h4>
      <div class="card accent2" style="margin-bottom:10px"><h4>MiniMax M2.5</h4><p style="color:var(--gray);font-size:13px">SWE-bench 80.2% · $0.30/$1.20</p></div>
      <div class="card accent2" style="margin-bottom:10px"><h4>Kimi K2.6</h4><p style="color:var(--gray);font-size:13px">AA Intelligence 开源 #1 · ~$2 hosted</p></div>
      <div class="card accent2" style="margin-bottom:10px"><h4>DeepSeek V4-Pro</h4><p style="color:var(--gray);font-size:13px">SWE-bench 80.6% · MIT 许可</p></div>
      <div class="card accent2" style="margin-bottom:10px"><h4>Qwen 3.6-72B</h4><p style="color:var(--gray);font-size:13px">68.2% · Apache 2.0 · 可自部署</p></div>
      <div class="card accent2"><h4>GLM-5</h4><p style="color:var(--gray);font-size:13px">SWE-bench Pro 62.8% · MIT · 免费</p></div>
    </div>
  </div>

  <div class="insight" style="margin-top:24px">
    <h4>🎯 按场景最佳选择</h4>
    <div class="picks-grid">
      <div class="pick"><div class="scene">多文件编码 / Agent 工作流</div><div class="model">→ Claude Opus 4.8</div><div class="why">最佳意图理解 + SWE-bench Pro 冠军</div></div>
      <div class="pick"><div class="scene">Agent 终端操作 / DevOps</div><div class="model">→ GPT-5.5</div><div class="why">82.7% Terminal-Bench 冠军</div></div>
      <div class="pick"><div class="scene">性价比首选 / 全科均衡</div><div class="model">→ Gemini 3.1 Pro</div><div class="why">80.6% SWE 得分 + 仅 $2/$12</div></div>
      <div class="pick"><div class="scene">最低成本 (前沿品质)</div><div class="model">→ DeepSeek V4-Flash</div><div class="why">$0.07 / 百万输出，仅需对手 1/350</div></div>
      <div class="pick"><div class="scene">自部署 / MIT 许可 / 隐私优先</div><div class="model">→ DeepSeek V4-Pro / GLM-5</div><div class="why">可下载权重，无数据泄露风险</div></div>
    </div>
  </div>
</div>

<!-- ═══════════════ SLIDE 8 — AI 风口行业 & 成功案例 ═══════════════ -->
<div class="section">
  <div class="section-header"><div class="accent-bar"></div><h2>05  AI 风口行业 & 成功案例</h2><div class="sub">金融 · 医疗 · 教育 — AI 落地进入实干期</div></div>

  <div class="card-row">
    <div class="card accent"><h4>🏦 金融: 招商银行「AI First」</h4><ul>
      <li>模式:「人+Agent」协同，AI 辅助非替代</li>
      <li>2025 年实现 1556 万小时人工替代</li>
      <li>入选 2026 全国智能体十大典型案例</li>
      <li>平安保险: 7 万+智能体协同 理赔效率 ↑80%</li>
      <li>工商银行: AI 数字员工承担超 5.5 万人年工作</li>
      <li>信用卡欺诈检出率 82%→97% 误报率 ↓60%</li>
    </ul></div>
    <div class="card accent2"><h4>🏥 医疗:「天医智联」国产大模型</h4><ul>
      <li>成就: CheXpert 国际评测全球第一</li>
      <li>覆盖 200+ 疾病 胸片准确率 92.7%</li>
      <li>300+ 基层医院部署 诊断准确率 ↑40%</li>
      <li>清华 AI 医生: MedQA 准确率 96% 8 家医院公测</li>
      <li>AI 药物研发: 周期从 5 年缩至 18 个月</li>
      <li>肺结节检出 98.7% 诊断从 15 分缩至 3 秒</li>
    </ul></div>
    <div class="card accent3"><h4>🎓 教育: AI 教育出海「智启教育」</h4><ul>
      <li>融资: 红杉中国领投 1.2 亿美元 B 轮</li>
      <li>目标: 东南亚 K12 2.5 亿学生 英语教师缺口超千万</li>
      <li>用户: 500 万+ 印尼/越南市场前三</li>
      <li>社会价值: 60% 用户来自农村 月费仅 10 元</li>
      <li>K12 自适应: 数学成绩平均提升 22 分</li>
      <li>高校 AI 批改: 教师批改效率提升 5×</li>
    </ul></div>
  </div>

  <div class="insight">
    <h4>📌 更多风口赛道</h4>
    <div class="picks-grid">
      <div class="pick"><div class="scene" style="color:var(--accent2);font-weight:700">🤖 具身智能/机器人</div><div class="why">工匠行签下上亿订单；宇树科技 IPO 过会 Q1 营收 ↑68.5%；特斯拉人形机器人 V3；比亚迪确认开发</div></div>
      <div class="pick"><div class="scene" style="color:var(--accent2);font-weight:700">🐾 情感 AI / 宠物经济</div><div class="why">Traini 获 NVIDIA+OpenAI 高管投资 750 万美元；情绪识别准确率 75-96%；美国市场 1520 亿美元</div></div>
      <div class="pick"><div class="scene" style="color:var(--accent2);font-weight:700">📸 AI 消费硬件</div><div class="why">像素跃动 AI 写真相机，利润率 50-60%，10 人团队 5 个月从创意到产品</div></div>
      <div class="pick"><div class="scene" style="color:var(--accent2);font-weight:700">🏢 政企 AI To B</div><div class="why">零一万物订单突破 15 亿元 2027 港股 IPO；海底捞 AI 打通全业务；元气森林 AI 驱动口味测试</div></div>
    </div>
  </div>
</div>

<!-- ═══════════════ SLIDE 9 — 行业趋势 & 未来展望 ═══════════════ -->
<div class="section">
  <div class="section-header"><div class="accent-bar"></div><h2>06  行业趋势 & 未来展望</h2><div class="sub">2026 关键判断与战略建议</div></div>

  <div class="trend"><span class="trend-num" style="background:var(--accent);color:white">趋势一</span><div class="trend-body"><h4>从生成式 AI → 智能体 AI</h4><p>Agent 成数字生活中心，可能替代 App 生态。2026 年 Agentic 流量首次超过人类网页流量。</p></div></div>
  <div class="trend"><span class="trend-num" style="background:var(--accent2);color:#0D111A">趋势二</span><div class="trend-body"><h4>多智能体协同进入成熟期</h4><p>单一模型无法满足复杂场景需求，组织级 Agent 协作成标配。平安保险 7 万+智能体协同、理想汽车全链条 Agent 是典型案例。</p></div></div>
  <div class="trend"><span class="trend-num" style="background:var(--accent3);color:white">趋势三</span><div class="trend-body"><h4>竞争壁垒 = 行业 Know-how 数字化</h4><p>通用大模型能力快速收敛，真正的护城河在于行业经验的数字化 — 将行业知识转化为可训练的数据和规则。</p></div></div>
  <div class="trend"><span class="trend-num" style="background:var(--accent4);color:#0D111A">趋势四</span><div class="trend-body"><h4>中国模型性价比碾压</h4><p>DeepSeek / GLM / Qwen 开源 MIT 许可，价格仅为西方前沿模型的 1/50~1/350。阿里 Qwen 首次闭源旗舰模型，打破"中国开源、西方闭源"旧格局。</p></div></div>
  <div class="trend"><span class="trend-num" style="background:#E07BFF;color:white">趋势五</span><div class="trend-body"><h4>AI 从提效工具 → 商业模式重构</h4><p>AI 重新定义产品、服务与商业模式。情感 AI、AI 写真、教育出海等新赛道证明消费者愿意为"情绪价值"和"新型体验"付费。</p></div></div>

  <div class="highlight" style="margin-top:20px">💡 战略建议: 2026 年是 AI 落地窗口期 — 企业应尽快将 AI Agent 嵌入核心业务流程；开发者应关注 MCP/A2A 标准生态 & 优先选择性价比高的模型组合（Gemini/DeepSeek 互补）；投资者应关注垂直场景 + 软硬结合终端赛道。</div>
</div>

<!-- ═══════════════ SLIDE 10 — 总结 ═══════════════ -->
<div class="section title-page">
  <div class="accent-bar" style="margin:0 auto 30px"></div>
  <h1 style="font-size:48px">THANK YOU</h1>
  <div class="subtitle" style="margin-top:10px">2026 年 6 月 AI 行业资讯报告</div>

  <ul class="summary" style="text-align:left;max-width:800px;margin:40px auto 0">
    <li>AI Agent 时代全面到来 — Agentic 流量已超人类</li>
    <li>MCP + A2A 双协议互补 — AI 世界的 TCP/IP 标准确立</li>
    <li>Claude Opus 4.8 登顶 Agent 赛道，GPT-5.5 领跑数学，Gemini 3.1 性价比最优</li>
    <li>中国开源模型崛起 — 性价比 50×+ 优势颠覆定价格局</li>
    <li>金融 / 医疗 / 教育 / 机器人 / 情感AI — 六大风口赛道已跑出商业闭环</li>
  </ul>

  <div class="source" style="margin-top:60px">
    数据来源: Computex 2026 · Microsoft Build · Forbes AI 50 · Artificial Analysis · LiveBench · 阿里云案例集 · 人民日报<br>
    生成日期: 2026年6月
  </div>
  <div style="text-align:right;color:var(--dim);font-size:12px;margin-top:10px">10 / 10</div>
</div>

</body>
</html>'''

desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
output_path = os.path.join(desktop, "AI行业最新资讯报告_2026年6月.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(HTML)
print(f"HTML saved to: {output_path}")

# Try to open in browser
import webbrowser
webbrowser.open(f"file:///{output_path}")
print("Opened in browser!")
