/* ═══ TSpace Studio — console logic ═══════════════════════════ */
"use strict";

const $ = (s, el) => (el || document).querySelector(s);
const $$ = (s, el) => Array.from((el || document).querySelectorAll(s));
const SNAP = window.PANDORA_SNAPSHOT || { trends: [], brands: [], runs: [], quota: {} };
const fmt = n => (n >= 1e6 ? (n / 1e6).toFixed(1) + "M" : n >= 1e3 ? (n / 1e3).toFixed(1) + "K" : String(n ?? 0));

/* ── starfield ─────────────────────────────────────────────── */
(() => {
  const cv = $("#starfield"), ctx = cv.getContext("2d");
  let stars = [];
  const size = () => {
    cv.width = innerWidth; cv.height = innerHeight;
    stars = Array.from({ length: 130 }, () => ({
      x: Math.random() * cv.width, y: Math.random() * cv.height,
      r: Math.random() * 1.3 + .2, p: Math.random() * Math.PI * 2,
      s: .3 + Math.random() * .8,
    }));
  };
  size(); addEventListener("resize", size);
  (function draw(t) {
    ctx.clearRect(0, 0, cv.width, cv.height);
    for (const st of stars) {
      const a = .25 + .55 * Math.abs(Math.sin(t / 1600 * st.s + st.p));
      ctx.globalAlpha = a;
      ctx.fillStyle = "#bcd7ff";
      ctx.beginPath(); ctx.arc(st.x, st.y, st.r, 0, 7); ctx.fill();
    }
    requestAnimationFrame(draw);
  })(0);
})();

/* ── view switching ────────────────────────────────────────── */
function goto(view) {
  $$(".rail-btn").forEach(b => b.classList.toggle("active", b.dataset.view === view));
  $$(".view").forEach(v => v.classList.toggle("active", v.id === "view-" + view));
  $(".stage").scrollTop = 0;
}
$$(".rail-btn").forEach(b => b.onclick = () => goto(b.dataset.view));
$$("[data-goto]").forEach(b => b.onclick = () => goto(b.dataset.goto));

function toast(msg) {
  const t = $("#toast"); t.textContent = msg; t.classList.add("show");
  clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove("show"), 2600);
}

/* ── quota widget (real numbers from the API) ──────────────── */
function setQuota(q) {
  const used = (q && q.used) ?? 0, limit = (q && q.limit) ?? 200;
  $("#quotaUsed").textContent = used;
  $("#quotaTotal").textContent = "/ " + limit;
  const C = 97.4;
  requestAnimationFrame(() =>
    $("#quotaArc").style.strokeDashoffset = C - C * Math.min(1, used / limit));
}
setQuota(SNAP.quota);

/* ── LIVE mode: same-origin BFF proxy, key stays server-side ─ */
const PROXY = "pandora-proxy";   // nginx: /tspace-studio/pandora-proxy/* -> pandora api (+key)
let liveBusy = false;
$("#modeSwitch").onclick = async function () {
  if (liveBusy) return;
  if (this.classList.contains("live")) {
    this.classList.remove("live");
    $("#modeLabel").textContent = "CACHED";
    renderSignals(SNAP.trends, SNAP.capturedAt);
    setQuota(SNAP.quota);
    toast("CACHED：顯示 " + (SNAP.capturedAt || "").slice(0, 16).replace("T", " ") + " 抓取的真實快照");
    return;
  }
  liveBusy = true;
  toast("正在經由伺服器端 proxy 即時呼叫 Pandora …");
  try {
    const r = await fetch(`${PROXY}/trends`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ type: "top", topN: 8, postsPerTrend: 3 }),
    });
    const obj = await r.json();
    if (!obj.success) throw new Error(obj.error || "proxy error");
    const trends = (obj.data || []).map(t => ({
      rank: t.rank, query: t.query, label: t.label || "",
      postCount: t.postCount || 0, totalVolume: t.totalVolume || 0,
      posts: (t.posts || []).slice(0, 3).map(p => ({
        author: p.author, url: p.url, source: p.source,
        excerpt: (p.excerpt || p.content || "").slice(0, 110),
        likes: p.likes || 0, comments: p.comments || 0,
        shares: p.shares || 0, volume: p.volume || 0,
      })),
    }));
    renderSignals(trends, new Date().toISOString());
    setQuota(obj.meta && obj.meta.quota);
    this.classList.add("live");
    $("#modeLabel").textContent = "LIVE";
    toast("LIVE：熱點已更新為即時資料（金鑰只存在伺服器端）");
  } catch (e) {
    toast("LIVE 呼叫失敗（proxy 未部署或配額用盡）— 維持快照資料");
  }
  liveBusy = false;
};

/* ═══ AGENTS ═════════════════════════════════════════════════ */
const AGENTS = [
  { code: "PANDORA", name: "Pandora", tone: "var(--cyan)", img: "assets/agent_pandora.jpg",
    shop: "Pandora 情報所", sells: "賣訊號 · 熱點與情緒",
    role: "SIGNAL · 市場訊號", desc: "每小時爬 Threads 熱點、品牌與品類聲量，附情緒分數。她是整條產線的耳朵 — 你看到的 Signals 頁就是她的工作台。",
    skills: "trend ranking · sentiment · brand pulse", tools: "BigQuery · Threads 速爬 (Cloud Run) · 精準表" },
  { code: "MOANA", name: "Moana", tone: "var(--orange)", img: "assets/agent_moana.jpg",
    shop: "Moana 文化工作室", sells: "賣語感 · Culture Listening",
    role: "CULTURE · 語感萃取", desc: "把 Pandora 抓回來的原話聽懂：口語、梗、痛點。Culture Listening 是她的方法論 — 產出的不是翻譯，是語感。",
    skills: "culture brief · verbatim mining · hook writing", tools: "Pandora corpus · 在地詞庫 · LLM" },
  { code: "BANANA", name: "Banana", tone: "var(--gold)", img: "assets/agent_banana.jpg",
    shop: "Banana 圖文工坊", sells: "賣素材 · 圖 / 文 / 影",
    role: "VISUAL · 圖文生成", desc: "拿著 Moana 的 brief 產視覺：商品照、情境圖、短影音。Banana Split 就是他的產線介面 — 也是我們要開放給開發者的那一層。",
    skills: "product shot · scene gen · motion", tools: "gen model fleet · brand kit · asset store" },
  { code: "ADRIANA", name: "Adriana", tone: "var(--violet)", img: "assets/agent_adriana.jpg",
    shop: "Adriana 投放代理", sells: "賣觸及 · CRM × CAPI",
    role: "DELIVERY · 投放回流", desc: "素材出去、數據回來：受眾標籤、CAPI 回傳、成效歸因。她讓「哪張素材有效」變成下一輪 Pandora 的輸入。",
    skills: "audience tagging · CAPI sync · attribution", tools: "TCRM · TCDP · Meta CAPI" },
  { code: "STACEY", name: "Stacey", tone: "var(--green)", img: "assets/agent_stacey.jpg",
    shop: "Stacey 街公所", sells: "管排程 · 驗收與記帳",
    role: "ORCHESTRATOR · 總指揮", desc: "整條 run 的排程、驗收與記帳由她負責。每一步誰做了什麼、花了幾個 credit，全部留痕。",
    skills: "run orchestration · QA · metering", tools: "A2A bus · policy engine · ledger" },
];

(() => {
  const row = $("#streetRow");
  AGENTS.forEach((a, i) => {
    const el = document.createElement("div");
    el.className = "shop-card";
    el.style.setProperty("--tone", a.tone);
    el.innerHTML = `
      <span class="shop-awning"></span>
      <img src="${a.img}" alt="${a.name}">
      <b>${a.shop}</b><em>${a.sells}</em>
      <span class="shop-open">營業中</span>`;
    el.onclick = () => selectAgent(i);
    row.appendChild(el);
  });
  const rent = document.createElement("div");
  rent.className = "shop-card rent";
  rent.innerHTML = `
    <span class="shop-awning"></span>
    <div class="rent-mark">＋</div>
    <b>你的店</b><em>店面招租 · 一把 pk_ key 就能開店</em>
    <span class="shop-open vacant">FOR RENT</span>`;
  rent.onclick = () => goto("develop");
  row.appendChild(rent);

  window.selectAgent = i => {
    $$(".shop-card").forEach((n, j) => n.classList.toggle("sel", i === j));
    const a = AGENTS[i];
    $("#agentDetail").innerHTML = `
      <div class="ad-head">
        <img src="${a.img}" alt="">
        <div><em style="color:${a.tone}">${a.role}</em><b>${a.name}</b></div>
      </div>
      <p>${a.desc}</p>
      <div class="harness">
        <div class="hrow"><b>SKILL</b><span>${a.skills}</span></div>
        <div class="hrow"><b>TOOL</b><span>${a.tools}</span></div>
        <div class="hrow"><b>A2A</b><span>${a.code} 可被其他 agent 以 <code>a2a://${a.code.toLowerCase()}</code> 呼叫</span></div>
      </div>`;
  };
  selectAgent(0);

  const runs = SNAP.runs || [];
  const posts = runs.reduce((s, r) => s + (r.posts || 0), 0);
  $("#statStrip").innerHTML = [
    [AGENTS.length, "AGENTS ONLINE"],
    [runs.length, "PANDORA RUNS · 8HR"],
    [fmt(posts), "POSTS CRAWLED"],
    ["2", "MARKETS · TW + TH"],
  ].map(([v, k]) => `<div class="stat"><b>${v}</b><em>${k}</em></div>`).join("");
})();

/* ═══ SIGNALS ════════════════════════════════════════════════ */
let selTrend = 0;
let curTrends = [];

function renderSignals(trends, capturedAt) {
  curTrends = trends || [];
  selTrend = 0;
  if (!curTrends.length) return;
  const maxV = Math.max(...curTrends.map(t => t.totalVolume));
  $("#signalMeta").innerHTML =
    `<span class="pill cyan">近 7 天</span><span class="pill">快照 ${(capturedAt || "").slice(5, 16).replace("T", " ")}</span>`;

  $("#trendList").innerHTML = curTrends.map((t, i) => `
    <div class="trend-row ${i === 0 ? "sel" : ""}" data-i="${i}">
      <span class="rk">${String(t.rank).padStart(2, "0")}</span>
      <span class="q"><b>${t.query}</b><em>${t.label}</em></span>
      <span class="vol"><b>${fmt(t.totalVolume)}</b><em>${t.postCount} posts</em></span>
      <span class="trend-bar"><i style="width:${Math.round(t.totalVolume / maxV * 100)}%"></i></span>
    </div>`).join("");
  $$("#trendList .trend-row").forEach(r => r.onclick = () => {
    selTrend = +r.dataset.i;
    $$("#trendList .trend-row").forEach(x => x.classList.toggle("sel", x === r));
    renderTrendPosts();
  });
  renderTrendPosts();
}

function renderTrendPosts() {
  const t = curTrends[selTrend];
  if (!t) return;
  $("#postPanelHead").innerHTML =
    `<b>「${t.query}」原始貼文</b><span class="tiny">top ${t.posts.length} · by volume</span>`;
  $("#postList").innerHTML = t.posts.map(p => `
    <div class="post-card">
      <div class="ph"><span>@${p.author} · ${p.source}</span>
        <a href="${p.url}" target="_blank" rel="noopener">開啟 ↗</a></div>
      <p>${p.excerpt}</p>
      <div class="pm"><span>♥ ${fmt(p.likes)}</span><span>💬 ${fmt(p.comments)}</span>
        <span>↻ ${fmt(p.shares)}</span><span style="color:var(--cyan)">vol ${fmt(p.volume)}</span></div>
    </div>`).join("");
}

renderSignals(SNAP.trends, SNAP.capturedAt);

(() => {
  $("#toStudio").onclick = () => { goto("studio"); toast("已把訊號帶進 Studio — 按「執行 Run」看整條產線"); };

  /* brand pulse */
  const brands = SNAP.brands || [];
  $("#brandTabs").innerHTML = brands.map((b, i) =>
    `<button class="brand-tab ${i === 0 ? "sel" : ""}" data-i="${i}">${b.brand}</button>`).join("");
  $$("#brandTabs .brand-tab").forEach(b => b.onclick = () => {
    $$("#brandTabs .brand-tab").forEach(x => x.classList.toggle("sel", x === b));
    renderBrand(+b.dataset.i);
  });
  renderBrand(0);

  function renderBrand(i) {
    const b = brands[i]; if (!b) return;
    const pos = b.posts.filter(p => (p.sentiment ?? 0) > .15).length;
    const neg = b.posts.filter(p => (p.sentiment ?? 0) < -.15).length;
    const neu = b.posts.length - pos - neg;
    const pct = n => Math.round(n / Math.max(1, b.posts.length) * 100);
    $("#sentiBar").innerHTML =
      `<i style="width:${pct(pos)}%;background:var(--green)"></i>` +
      `<i style="width:${pct(neu)}%;background:rgba(255,255,255,.18)"></i>` +
      `<i style="width:${pct(neg)}%;background:var(--pink)"></i>`;
    $("#sentiLegend").innerHTML =
      `<span>正面 ${pct(pos)}%</span><span>中性 ${pct(neu)}%</span><span>負面 ${pct(neg)}%</span>`;
    $("#brandPosts").innerHTML = b.posts.slice(0, 6).map(p => {
      const s = p.sentiment ?? 0;
      const cls = s > .15 ? "senti-pos" : s < -.15 ? "senti-neg" : "";
      return `<div class="post-card">
        <div class="ph"><span>@${p.author}</span><a href="${p.url}" target="_blank" rel="noopener">↗</a></div>
        <p>${p.excerpt}</p>
        <div class="pm"><span>♥ ${fmt(p.likes)}</span>
          <span class="${cls}">sentiment ${s > 0 ? "+" : ""}${(+s).toFixed(2)}</span></div>
      </div>`;
    }).join("");
  }
})();

/* ═══ STUDIO — the run ═══════════════════════════════════════ */
const LAB = (window.LAB_DATA && window.LAB_DATA.experiments) || [];
const cvsExp = LAB.find(e => e.id === "cvs_coffee");

const RUN_HOOKS = (cvsExp && cvsExp.brief && cvsExp.brief.hooks) || [
  { angle: "比較文正面迎戰", copy: "有人說我們的冰美式喝起來像星巴克。我們想說：對，然後只要 45 塊。" },
  { angle: "上班日儀式感", copy: "會議前 3 分鐘，樓下就能拿到的那杯黑咖啡，是今天唯一準時的東西。" },
  { angle: "通勤路上", copy: "捷運出口到公司的 400 公尺，配一杯大冰美，剛好醒完。" },
];

const RUN_STEPS = [
  { agent: 0, dur: 2600, lines: [
    ["pandora", "POST /api/public/query {\"searchExpression\":\"星巴克\",\"table\":\"precise\"}"],
    ["pandora", "← 200 · 12 posts · quota 195/200", "cost"],
    ["pandora", "偵測到高分歧貼文：@_.wyyyh_「全家的冰美式跟星巴克…」 sentiment -0.73"],
    ["pandora", "a2a://moana ← signal_bundle (12 posts, 3 highlights)", "a2a"],
  ]},
  { agent: 1, dur: 3200, lines: [
    ["moana", "Culture Listening：讀取原話，抽出口語與梗"],
    ["moana", "verbatim:「可能是我不懂喝吧」「比起來根本沒差」「只要一半價錢」"],
    ["moana", "痛點 → 價格 vs 品質的自我懷疑；切角 → 正面迎戰比較文"],
    ["moana", "a2a://banana ← culture_brief + 3 hooks (zh-Hant)", "a2a"],
  ]},
  { agent: 2, dur: 4200, lines: [
    ["banana", "載入 brand kit bk_ncc_coffee（色票 / 字級 / 禁用元素）"],
    ["banana", "gen 1:1 × 3 variants … morning desk / studio mint / street golden-hour"],
    ["banana", "3 assets rendered · 4.2 credits", "cost"],
    ["banana", "a2a://adriana ← asset_bundle (3 img + 3 copy)", "a2a"],
  ]},
  { agent: 3, dur: 2400, lines: [
    ["adriana", "受眾規劃：互動過「超商咖啡」相關貼文的 lookalike"],
    ["adriana", "CAPI mapping 就緒 · 投放後成效將回流 Pandora"],
    ["adriana", "a2a://stacey ← delivery_plan", "a2a"],
  ]},
  { agent: 4, dur: 2200, lines: [
    ["stacey", "QA：brand kit 合規 ✓ · 文案不像廣告腔 ✓ · 圖無文字錯誤 ✓"],
    ["stacey", "run 完成 · 總用量 6.4 credits · 全程 41s · ledger #r_8f2c", "cost"],
  ]},
];

(() => {
  $("#pipeline").innerHTML = AGENTS.map((a, i) =>
    `<div class="pipe-node" data-i="${i}" style="--tone:${a.tone}">
       <img src="${a.img}" alt=""><b>${a.code}</b>
     </div>${i < AGENTS.length - 1 ? '<span class="pipe-arrow">▸</span>' : ""}`).join("");

  /* CLI command preview — built from the selects */
  const buildCmd = () => {
    const r = $("#recipeSel").value, k = $("#brandKit").value;
    return `tpc run ${r} --brand "超商咖啡" --kit ${k} --days 14 --out 3`;
  };
  const renderCmd = () => {
    $("#cliCmd").innerHTML = `<span class="ps">$</span> ${buildCmd()}`;
  };
  $("#recipeSel").onchange = renderCmd;
  $("#brandKit").onchange = renderCmd;
  renderCmd();

  /* plugin market strip — 套路就是 plugin */
  const PLUGINS = [
    ["@tpc/signal-to-post", "官方 · 熱點轉圖文", "1.2K 安裝", "var(--cyan)"],
    ["@moana/tw-slang", "官方 · 台灣語感庫", "890 安裝", "var(--orange)"],
    ["@ian/手搖飲套路", "個人開發者 · 飲料店哏圖", "312 安裝", "var(--gold)"],
    ["@cody/agent-bridge", "Cody 從這裡串進來 · MCP", "NEW", "var(--violet)"],
    ["@bkk/thai-launch", "曼谷團隊 · 泰文素材", "97 安裝", "var(--green)"],
    ["your-plugin", "你的套路 · tpc plugin publish", "—", "var(--dim)"],
  ];
  $("#pluginGrid").innerHTML = PLUGINS.map(([id, desc, meta, tone]) => `
    <div class="plugin-chip" style="--tone:${tone}">
      <code>${id}</code><em>${desc}</em><span>${meta}</span>
    </div>`).join("");

  let running = false;
  $("#runBtn").onclick = async () => {
    if (running) return;
    running = true;
    $("#runBtn").textContent = "⏳ Running…";
    $("#runStatus").textContent = "running";
    $("#runlog").innerHTML = `<div class="ln cmd"><span class="ps">$</span><span class="m">${buildCmd()}</span></div>`;
    $("#outputs").innerHTML = "";
    $("#outMeta").textContent = "產出中…";
    $$(".pipe-node").forEach(n => n.classList.remove("run", "done"));

    const log = (agent, msg, cls) => {
      const t = new Date().toTimeString().slice(3, 8);
      const a = AGENTS.find(x => x.code.toLowerCase() === agent);
      const el = document.createElement("div");
      el.className = "ln " + (cls || "");
      el.innerHTML = `<span class="t">${t}</span><span class="a" style="color:${a ? a.tone : "var(--mut)"}">${agent}</span><span class="m">${msg}</span>`;
      $("#runlog").appendChild(el);
      $("#runlog").scrollTop = 1e6;
    };
    const wait = ms => new Promise(r => setTimeout(r, ms));

    for (const step of RUN_STEPS) {
      const node = $(`.pipe-node[data-i="${step.agent}"]`);
      node.classList.add("run");
      for (const [agent, msg, cls] of step.lines) {
        log(agent, msg, cls);
        await wait(step.dur / step.lines.length);
      }
      node.classList.remove("run");
      node.classList.add("done");
    }

    const imgs = ["assets/gen_out_1.jpg", "assets/gen_out_2.jpg", "assets/gen_out_3.jpg"];
    $("#outputs").innerHTML = RUN_HOOKS.slice(0, 3).map((h, i) => `
      <div class="out-card">
        <img src="${imgs[i]}" alt="">
        <div class="oc-body"><em>HOOK ${i + 1} · ${h.angle}</em><p>${h.copy}</p></div>
      </div>`).join("");
    $$(".out-card").forEach((c, i) => setTimeout(() => c.classList.add("show"), 150 * i));
    const receipt = document.createElement("div");
    receipt.className = "ln receipt";
    receipt.innerHTML = `<span class="ps">✓</span><span class="m">run 完成 —— manifest 已寫入 <b>~/.tpc/runs/r_8f2c.json</b>（4 steps · 6.4 credits · QA pass）</span>`;
    $("#runlog").appendChild(receipt);
    $("#runlog").scrollTop = 1e6;
    $("#outMeta").textContent = "3 assets · 6.4 credits";
    $("#runStatus").textContent = "done · ledger #r_8f2c";
    $("#runBtn").textContent = "▶ 再跑一次";
    running = false;
  };
})();

/* ═══ LAB — real experiments ═════════════════════════════════ */
(() => {
  const flow = [
    ["01 · SIGNAL", "Pandora 抓真貼文", "品牌詞或品類詞 · 近 14 天 · 含情緒", "var(--cyan)"],
    ["02 · FILTER", "訊噪分離", "量測 noise ratio · 品牌詞常常一半是雜訊", "var(--violet)"],
    ["03 · CULTURE", "Moana 聽語感", "抄原話 → 痛點 → 在地語言的 hook", "var(--orange)"],
    ["04 · CREATIVE", "Banana 產素材", "brief 直接變 visual prompt · 1:1 社群圖", "var(--gold)"],
    ["05 · VERDICT", "工作流結論", "這種品牌該怎麼餵，才會產出好素材", "var(--green)"],
  ];
  $("#labFlow").innerHTML = flow.map(([i, b, e, c], k) =>
    `<div class="lf-step"><i style="color:${c}">${i}</i><b>${b}</b><em>${e}</em></div>` +
    (k < flow.length - 1 ? '<span class="lf-arr">─▶</span>' : "")).join("");

  if (!LAB.length) {
    $("#labGrid").innerHTML = `<div class="glass panel" style="grid-column:1/-1;color:var(--mut);font-size:13px;line-height:1.8">
      實驗結果生成中 — pipeline 正在跑「Pandora → Culture Listening → Banana」。完成後重新整理此頁。</div>`;
    return;
  }
  const brands = new Set(LAB.map(e => e.brand)).size;
  $("#labMeta").innerHTML = `<span class="pill cyan">${LAB.length} experiments</span>
    <span class="pill violet">${brands} brands</span>
    <span class="pill orange">TW + TH</span><span class="pill">全部真資料</span>`;

  const maniTrace = m => !m ? "" : `
      <div class="exp-mani">
        <div class="em-head"><code>${m.runId}</code><span>${m.recipe}</span>
          <b>${m.totalCredits} cr</b></div>
        <div class="em-steps">${m.steps.map(s =>
          `<span class="em-step ${s.status}" title="${s.out}">
             <b>${s.agent}</b>${(s.ms / 1000).toFixed(1)}s · ${s.credits}cr</span>`).join("<i>▸</i>")}
        </div>
      </div>`;

  $("#labGrid").innerHTML = LAB.map(e => {
    const ev = (e.evidence || [])[0];
    const brief = e.brief || {};
    const phrases = (brief.consumer_phrases || []).slice(0, 2);
    const hooks = (brief.hooks || []).slice(0, 2);
    const noise = Math.round((brief.noise_ratio ?? 0) * 100);
    return `
    <div class="exp-card ${e.group ? "grouped" : ""}">
      <div class="exp-head"><b>${e.brand}</b>
        <span style="display:flex;gap:6px;align-items:center">
          ${e.window_label ? `<span class="mk win">📅 ${e.window_label}</span>` : ""}
          <span class="mk ${e.market.toLowerCase()}">${e.market} · ${e.lang}</span></span></div>
      <div class="exp-hypo">假設：${e.hypothesis}</div>
      <div class="exp-chain">
        <div class="chain-row"><b style="color:var(--cyan)">SIGNAL</b>
          <div class="evi">關鍵字 <code>${e.keyword}</code> · ${e.postCount} 篇真貼文 · 雜訊 ${noise}%
            ${ev ? `<span class="quote">「${ev.content}」<i> — @${ev.author}${ev.sentiment != null ? " · 情緒 " + (+ev.sentiment).toFixed(2) : ""}</i></span>` : ""}
          </div></div>
        <div class="chain-row"><b style="color:var(--orange)">CULTURE</b>
          <div class="evi"><strong style="color:var(--ink)">${brief.insight || ""}</strong>
            ${phrases.map(p => `<span class="quote">原話：「${p}」</span>`).join("")}
          </div></div>
        <div class="chain-row"><b style="color:var(--gold)">HOOKS</b>
          <div class="evi">${hooks.map(h => `<span class="quote"><i>${h.angle}</i><br>${h.copy}</span>`).join("")}</div></div>
      </div>
      <div class="exp-outs">
        ${(e.images || []).map((img, i) => `
          <figure class="exp-out"><img src="assets/${img}" alt="" loading="lazy">
            <figcaption>${(hooks[i] && hooks[i].copy) ? hooks[i].copy : ""}</figcaption></figure>`).join("")}
      </div>
      ${maniTrace(e.manifest)}
      <div class="exp-foot"><b>VERDICT</b> · ${brief.workflow_note || ""}</div>
    </div>`;
  }).join("");

  const learns = [
    ["cyan", "① 品類詞 > 品牌詞", "品牌詞雜訊高", "「全家」一半在講政治和日常。品類詞（超商咖啡、健身早餐）長出來的洞察乾淨得多。"],
    ["orange", "② 洞察藏在競品串", "搜對手，找到自己", "搜「星巴克」反而挖到超商咖啡的機會點。聆聽的邊界要畫在品類，不是品牌。"],
    ["gold", "③ 原話就是文案", "不要翻譯，要引用", "好 hook 幾乎都是消費者原話的變形。Culture Listening 的產出是語感，不是摘要。"],
    ["green", "④ 海外市場可複製", "TW 深度 · TH 已收料", "泰文貼文已經抓得到。同一條產線換語言就能出在地素材 — 這是出海的底氣。"],
    ["violet", "⑤ 訊號有日期", "產線是活的", "肯德基「近 3 天」和「上週」兩個時間窗抓到的話不一樣，素材跟著換 — 這是模板做不到的。"],
    ["cyan", "⑥ manifest 是標準", "每個 run 一張單據", "步驟、耗時、credit、QA 全記錄（tpc.run-manifest/v1）。有這張單據，別人才能基於我們的產線蓋自己的店。"],
  ];
  $("#learnGrid").innerHTML = learns.map(([c, b, i, p]) =>
    `<div class="learn"><i style="color:var(--${c})">${i}</i><b>${b}</b><p>${p}</p></div>`).join("");
})();

/* ═══ MOAT ═══════════════════════════════════════════════════ */
(() => {
  const dots = [
    { x: 78, y: 76, n: "一般生圖工具", d: "Midjourney / 各家 image model" },
    { x: 55, y: 84, n: "模板工具 Canva" },
    { x: 16, y: 26, n: "傳統輿情公司" },
    { x: 30, y: 55, n: "廣告代理商" },
    { x: 80, y: 48, n: "Meta Advantage+" },
    { x: 76, y: 14, n: "The Pocket Company", us: true },
  ];
  $("#posmap").innerHTML =
    `<span class="axis ay">▲ 自有輿情資料（每天在長）</span>
     <span class="axis ax">素材產線自動化 ▶</span>` +
    dots.map(d => `<div class="pos-dot ${d.us ? "us" : ""}" style="left:${d.x}%;top:${d.y}%">
        <i></i><b>${d.n}</b></div>`).join("");

  const loop = [
    ["👂", "聽 · Pandora", "每天爬回台灣（和泰國）真正在說的話", "var(--cyan)"],
    ["🧠", "懂 · Moana", "Culture Listening：原話 → 語感 → 切角", "var(--orange)"],
    ["🎨", "做 · Banana", "brief 直接變素材，不經過想像", "var(--gold)"],
    ["📤", "投 · Adriana", "素材出去，標籤與成效跟著回來", "var(--violet)"],
  ];
  $("#cultureLoop").innerHTML = loop.map(([i, b, e, c]) =>
    `<div class="loop-step"><i>${i}</i><div><b style="color:${c}">${b}</b><em>${e}</em></div></div>`).join("") +
    `<div class="loop-back">↺ 成效資料回流 Pandora — 下一輪素材比這一輪更準</div>`;

  $("#moatCards").innerHTML = [
    ["var(--cyan)", "MOAT 01 · 資料飛輪", "素材是從「今天的對話」長出來的",
     "生圖工具人人有，但別人的 prompt 來自想像，我們的 prompt 來自 Pandora 今天抓回來的原話。資料每天在長，領先每天在加大。"],
    ["var(--orange)", "MOAT 02 · 方法論", "Culture Listening 不是翻譯，是語感",
     "把「可能是我不懂喝吧」這種自嘲留在文案裡，才像真人。這套從原話到 hook 的萃取流程已經跑成 recipe，可以複製、可以賣。"],
    ["var(--green)", "MOAT 03 · 多市場產線", "同一條產線，換語言就能出海",
     "實驗證明泰國 Threads 已經抓得到。台灣練深度、泰國先收料，之後每開一個市場，只是多接一個語感庫，不用重建產線。"],
  ].map(([c, i, b, p]) =>
    `<div class="moat-card"><i style="color:${c}">${i}</i><b>${b}</b><p>${p}</p></div>`).join("");
})();

/* ═══ ECOSYSTEM · 生態系街區 ═════════════════════════════════ */
(() => {
  const SHOPS = [
    {
      tone: "var(--cyan)", name: "小編代操工作室", builder: "台北 · 3 個人 · 客戶 20 間手搖飲和餐酒館",
      shape: "痛：一間店一週要花 8 小時想哏做圖",
      story: "現在早上跑一次 <code>tpc run</code>，抓昨晚大家真的在聊什麼，套自己寫的「餐飲哏套路」plugin，一間店 10 分鐘出一週的圖文。接案量從 20 間變 50 間，人沒有多。",
      prims: ["餐飲哏套路 plugin", "每天的輿情訊號", "一鍵出圖"],
      biz: "月費 1.5 萬/店 · 素材成本剩零頭",
    },
    {
      tone: "var(--gold)", name: "電商代營運公司", builder: "幫 momo／蝦皮品牌操盤 · 雙 11 是生死線",
      shape: "痛：檔期前 300 個 SKU 素材做不完",
      story: "以前排攝影棚排三週；現在白底商品照丟進去，一個 SKU 長 12 張生活情境圖，雙 11 素材一週內全數交付。客戶問「你們哪來這麼多攝影師」。",
      prims: ["商品情境包套路", "品牌色票自動套", "批量出圖"],
      biz: "按 SKU 計件收費 · 毛利翻倍",
    },
    {
      tone: "var(--violet)", name: "廣告代理商", builder: "30 個品牌客戶 · 提案就是戰場",
      shape: "痛：pitch 一次要兩週生 mockup",
      story: "現在比稿當天，用客戶品類「真實的輿情」跑出三套方向 — 客戶看到的第一句話是消費者自己說的。介面掛代理商的 logo，客戶以為是自研系統。",
      prims: ["白牌介面", "即時輿情", "提案級素材"],
      biz: "向客戶收月租 · 用量跟我們結算",
    },
    {
      tone: "var(--orange)", name: "KOL 電商團隊", builder: "網紅團購 · 每檔期 72 小時決勝負",
      shape: "痛：團購素材永遠趕不上開團",
      story: "開團前一天，把粉絲留言區的原話抓出來變文案 —「這就是我上次問的那個！」— 素材當天出，語感是粉絲自己的話，轉單率看得見。",
      prims: ["留言原話轉文案", "開團倒數排程", "分潤報表"],
      biz: "每檔團購按成效抽成",
    },
    {
      tone: "var(--green)", name: "獨立開發者", builder: "一個人 · 老婆開手搖店 · 晚上寫 code",
      shape: "賺：把自己的套路上架，睡覺也分潤",
      story: "幫老婆的店練出一套「飲料店哏圖套路」，<code>tpc plugin publish</code> 上架。現在全台 312 間飲料店裝了他的 plugin，每次被執行他抽一份 — App Store 開發者的邏輯。",
      prims: ["SKILL.md 就是產品", "plugin 市集", "被執行就分潤"],
      biz: "312 安裝 · 被動收入",
    },
    {
      tone: "var(--cyan)", name: "AI 新創", builder: "兩個工程師 · 追著新模型跑",
      shape: "賺：新模型上市當天就開賣",
      story: "新的生成模型今天發佈？CLI 換個 <code>--model</code> 參數，昨天的 run 全部重跑一遍，新舊輸出並排 — 當天就能賣「新模型素材包」，比別人快一週。Cody 這類 agent 也直接串同一條 CLI。",
      prims: ["--model 一鍵換引擎", "舊 run 重放", "agent 直連"],
      biz: "評測訂閱 + 首發素材包",
    },
  ];
  $("#ecoMeta").innerHTML = `<span class="pill green">6 種台灣生意</span>
    <span class="pill">不用懂 AI</span><span class="pill cyan">同一本帳</span>`;
  $("#ecoGrid").innerHTML = SHOPS.map(s => `
    <div class="eco-shop" style="--tone:${s.tone}">
      <span class="shop-awning"></span>
      <div class="eco-head"><b>${s.name}</b><em>${s.builder}</em></div>
      <div class="eco-shape">${s.shape}</div>
      <p>${s.story}</p>
      <div class="eco-prims">${s.prims.map(p => `<code>${p}</code>`).join("")}</div>
      <div class="eco-biz">${s.biz}</div>
    </div>`).join("");

  const mani = (LAB.find(e => e.manifest) || {}).manifest;
  const step = s => `<div class="std-step">
      <b>${String(s.seq).padStart(2, "0")} · ${s.agent}</b><code>${s.api}</code>
      <span>${s.ms.toLocaleString()} ms</span><span>${s.credits} cr</span>
      <i class="${s.status}">${s.status === "pass" ? "✓ pass" : s.status}</i></div>`;
  $("#ecoStandard").innerHTML = mani ? `
    <div class="std-head"><code>${mani.runId}</code>
      <span class="pill violet">${mani.recipe}</span>
      <span class="pill">${mani.standard}</span>
      <span class="pill cyan">window ${mani.window.start} → ${mani.window.end}</span></div>
    <div class="std-steps">${mani.steps.map(step).join("")}</div>
    <div class="std-foot">上面這張是真的 — 全國電子那次實驗留下的單據：四步、各花幾秒、記幾個 credit、驗收過沒過。
      合計 <b>${mani.totalCredits} credits</b> 入帳。生意要掛上來之前，老闆想看的就是這張。</div>`
    : `<div class="std-foot">run manifest 生成中 — pipeline v2 跑完後重新整理。</div>`;
})();

/* ═══ RECIPES ════════════════════════════════════════════════ */
(() => {
  const R = [
    ["signal-to-post", "熱點轉社群圖文", "Pandora 訊號進、3 版圖文出。本 demo Studio 跑的就是這一條。", [0, 1, 2], "6.4 cr/run", "1.2K"],
    ["culture-listening", "在地語感詞庫", "持續聽一個品類，養出品牌自己的語感庫與禁用清單。", [0, 1], "8 cr/週", "640"],
    ["product-shot-pack", "商品情境包", "一張白底商品照，長出 12 個在地生活場景。", [2], "12 cr/run", "980"],
    ["overseas-launch", "海外市場登陸", "泰國版 signal-to-post：泰文原話 → 泰文素材。", [0, 1, 2], "9 cr/run", "NEW"],
    ["capi-audience-sync", "互動受眾回傳", "把素材互動者變成標籤，回傳 Meta CAPI。", [3], "3 cr/day", "450"],
    ["brand-pulse-weekly", "品牌聲量週報", "每週一早上，聲量、情緒、對手動態自動進信箱。", [0, 4], "4 cr/週", "2.1K"],
  ];
  $("#recipeGrid").innerHTML = R.map(([id, name, desc, ags, price, installs]) => `
    <div class="recipe-card">
      <div class="rc-top"><code>${id}</code><span class="rc-price">${price}</span></div>
      <b>${name}</b><p>${desc}</p>
      <div class="rc-agents">${ags.map(i => `<img src="${AGENTS[i].img}" title="${AGENTS[i].name}">`).join("")}</div>
      <div class="rc-foot"><span class="rc-installs">${installs} installs</span>
        <button class="tiny-btn" onclick="toast('Recipe 安裝後即出現在你的 Studio 下拉選單')">安裝</button></div>
    </div>`).join("");

  $("#anatomy").innerHTML = [
    ["SKILL.md", "這個配方的方法論：步驟、驗收標準、語感原則", "var(--cyan)"],
    ["TOOLS", "宣告要用哪些 tool：pandora.query、banana.gen、capi.sync", "var(--orange)"],
    ["BRAND KIT 掛載點", "色票、字級、禁用元素 — 換品牌不用改配方", "var(--gold)"],
    ["METERING", "每一步的 credit 單價，跑完自動記帳", "var(--green)"],
  ].map(([b, p, c]) =>
    `<div class="learn"><i style="color:${c}">▸</i><b>${b}</b><p>${p}</p></div>`).join("");
})();

/* ═══ KEYS ═══════════════════════════════════════════════════ */
(() => {
  const q = SNAP.quota || {};
  $("#keysMeta").innerHTML = `<span class="pill green">metering on</span>`;
  $("#keyList").innerHTML = `
    <div class="key-row">
      <div class="kr-top"><code class="pk">pk_live_••••••9xrsQs</code><span class="st on">ACTIVE</span></div>
      <p><b>Publishable</b> — 可以放進瀏覽器與第三方 app。只能讀，會被限流，可以隨時 revoke。
         Chris 現在發的就是這種。</p>
    </div>
    <div class="key-row">
      <div class="kr-top"><code class="sk">sk_live_••••••••••••</code><span class="st on">SERVER ONLY</span></div>
      <p><b>Secret</b> — 只住在伺服器。能寫、能生成、能花錢。這個 console 的 LIVE 模式
         就是經由後端 proxy 用它呼叫，前端永遠看不到。</p>
    </div>
    <div class="key-row">
      <div class="kr-top"><code class="pk">pk_partner_raccoon••</code><span class="st off">SCOPED</span></div>
      <p><b>Partner</b> — 生態系夥伴（如 Raccoon）拿到的 key 只開放特定 scope 與額度，
         用量各自記帳，超額自動降速而不是斷線。</p>
    </div>`;

  const used = q.used ?? 0, limit = q.limit ?? 200;
  $("#usage").innerHTML = [
    ["REST API", used, limit, "var(--cyan)"],
    ["MCP（建置中）", 0, limit, "var(--violet)"],
    ["UI SDK（規劃）", 0, limit, "var(--gold)"],
  ].map(([n, u, l, c]) => `
    <div class="u-row"><em><span>${n}</span><span>${u} / ${l}</span></em>
      <div class="u-bar"><i style="width:${Math.max(2, u / l * 100)}%;background:${c}"></i></div>
    </div>`).join("");
  $("#quotaNote").innerHTML =
    `左邊的數字是<b style="color:var(--ink)">真的</b>：這個 key 今天在 Pandora 的用量 ${used}/${limit}，
     直接讀自 API 回傳的 <code>meta.quota</code>。計量不用另外做 — 它已經在每個 response 裡。`;

  $("#scopes").innerHTML = [
    ["pandora.query", "讀輿情資料", true],
    ["pandora.trends", "讀熱點排行", true],
    ["banana.generate", "產圖文素材", true],
    ["banana.motion", "產短影音", false],
    ["adriana.capi", "回傳 Meta CAPI", false],
    ["ledger.read", "讀自己的帳", true],
  ].map(([k, d, on]) => `
    <div class="scope"><div><b>${k}</b><em>${d}</em></div>
      <span class="tgl ${on ? "on" : ""}"></span></div>`).join("");
})();

/* ═══ DEVELOP ════════════════════════════════════════════════ */
(() => {
  const TABS = [
    {
      id: "rest", name: "REST API", tag: "LIVE · 已可用", badge: "live",
      title: "curl · 今天就能跑（本 demo 的資料就是這樣來的）",
      code: `# 熱點排行 — 和這個 console Signals 頁同一支 API
curl -X POST https://pandora.thepocket.company/api/public/trends \\
  -H "x-api-key: $POCKET_KEY" \\
  -H "content-type: application/json" \\
  -d '{"type":"top","topN":8,"postsPerTrend":3}'

# 品牌聲量（含情緒分數）
curl -X POST https://pandora.thepocket.company/api/public/query \\
  -H "x-api-key: $POCKET_KEY" \\
  -d '{"table":"precise","searchExpression":"星巴克",
       "startDate":"2026-07-28","endDate":"2026-08-11","limit":12}'`,
      note: `<span class="badge live">LIVE</span>
        <b>已上線。</b>每個 response 都帶 <code>meta.quota</code>（本日用量），
        所以計量與帳單天生就有。這頁所有真資料 — 熱點、貼文、情緒 — 都是這兩支打回來的。`,
    },
    {
      id: "mcp", name: "MCP", tag: "建置中", badge: "wip",
      title: "mcp.json · 給 Claude / Cursor / 自家軟體",
      code: `{
  "mcpServers": {
    "pocket": {
      "url": "https://pandora.thepocket.company/mcp",
      "headers": { "x-api-key": "\${POCKET_KEY}" }
    }
  }
}

// agent 拿到的 tools：
//   pandora_query · pandora_trends · threads_scrape
//   banana_generate (roadmap) · capi_sync (roadmap)`,
      note: `<span class="badge wip">建置中</span>
        <b>Chris 的設計方向：</b>「全都包成 MCP 訪問、要帶 key」。
        把技術文件跟 key 給任何 agent（Claude、Cursor、客戶自己開發的軟體）就能用 —
        每一次 tool call 都掛在 key 上，可控、可計價。`,
    },
    {
      id: "sdk", name: "UI SDK", tag: "規劃", badge: "road",
      title: "十行做出一個 agent dashboard（本 console 就是 reference）",
      code: `<script type="module"
  src="https://cdn.thepocket.company/banana-ui@1/console.js"><\/script>

<banana-console
  publishable-key="pk_live_…"
  recipe="signal-to-post"
  brand-kit="bk_your_brand"
  market="tw"          <!-- tw | th | … 多市場同一組件 -->
  theme="tspace-dark">
</banana-console>`,
      note: `<span class="badge road">ROADMAP</span>
        <b>Shopify 的 Theme 層。</b>開發者不用重做 Signals、Run、計量這些 UI —
        掛上 web component、帶 pk_ key 就有一個自己的 console。
        你現在看的 TSpace Studio，就是這個 SDK 的第一個 reference implementation。`,
    },
  ];
  $("#devMeta").innerHTML = `<span class="pill green">REST live</span>
    <span class="pill">MCP 建置中</span><span class="pill">SDK 規劃</span>`;
  $("#devTabs").innerHTML = TABS.map((t, i) =>
    `<button class="dev-tab ${i === 0 ? "sel" : ""}" data-i="${i}">
       <b>${t.name}</b><em>${t.tag}</em></button>`).join("");
  const render = i => {
    const t = TABS[i];
    $("#codeTitle").textContent = t.title;
    $("#codeBlock").textContent = t.code;
    $("#codeNote").innerHTML = t.note;
  };
  $$("#devTabs .dev-tab").forEach(b => b.onclick = () => {
    $$("#devTabs .dev-tab").forEach(x => x.classList.toggle("sel", x === b));
    render(+b.dataset.i);
  });
  render(0);
  $("#copyBtn").onclick = () => {
    navigator.clipboard.writeText($("#codeBlock").textContent).then(() => toast("已複製"));
  };
})();
