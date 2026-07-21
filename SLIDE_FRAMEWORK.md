# Slide Framework — Harness Bundle

> 這是給 **接手的 AI Agent** 讀的全套 onboarding 文件，放在 `turncloud-presentation` repo 根目錄。
> 它本身就是一份 **Harness** — 整捆 `memory + skills + tools` 塞進 LLM 的 input，
> 你看完就有能力直接動工：在我們的 framework 上加 slide、改內容、出新 deck、生成新的 hero image。
>
> **TL;DR**（2026-06-23 校時）
> - **這個 repo 就是唯一正式來源（canonical source）**。版本規矩見 [§0](#0-版本規矩-version-rules) 與 `README.md`。
> - 正式發表 deck = **repo 根目錄 `index.html`**，**目前 24 頁**（cover → trailer → … → redeem/QR）。最新版逐頁清單見 [§1.5 最新版投影片進度](#15-memory-最新版投影片進度current-deck-inventory)。英文版 `tpc-launch-en/`（也是 24 頁，內容同步）。
> - Build framework 本體在 `tpc-launch/`：執行 `python build.py`，讀 `slides.yaml` + `templates/` → 產出 `index.html`（13 個 Jinja2 templates，`SilentUndefined` 哲學）。
> - **🔴 最重要的現實落差（比舊版更嚴重）**：repo 內**沒有任何一份 `slides.yaml` 與目前 canonical `index.html` 對得起來**。`tpc-launch/slides.yaml`（26 頁、缺 trailer/redeem）與被棄用的 `tpc-launch-deck/v2/slides.yaml`（27 頁、merger/runtime/problem/closing）**都不符合**。canonical deck 雖然頂部還掛著「自動產出」橫幅，但**實際上已是手動維護的單檔 HTML，build pipeline 已與它脫鉤**。→ **改正式 deck 請直接編輯根目錄 `index.html`**；**千萬不要 `python build.py` 蓋過去**（會用舊內容覆蓋）。這正是 `CODYML_PLAN.md` Phase 0 要修的第一個技術債。
> - 影片 / 圖片素材集中放在 repo 根目錄 `img/`（主 deck 引用）與 `tpc-launch/img/`（框架素材庫）；衍生 deck 可用 NTFS junction 或 `../img/` 相對路徑重用。
> - 要生新 infographic / hero image：寫一個 `generate_*.py`，呼叫 Gemini `nano-banana-pro-preview`（model 寫死在腳本）。目前主圖 harness 已演進到 **`harness_as_llm_input_v11b_final.jpg`**（slide 06 fullbleed 用的就是這張）。
> - **環境**：`pip install -r tpc-launch/requirements.txt requests` · API key 放在各 deck 自己的 `.env`（檔案不入 git）→ 詳見 [§8.0 Setup](#80-setup-環境準備-python-api-key-env)
> - **部署**：push `main` → GitHub Pages 自動發佈；自訂網域 `turncloud.thepocket.company` 在 GCP VM（nginx），要手動同步 → 詳見 [§12 Deploy 層](#12-quirks-已知陷阱與注意事項)

---

## 目錄

0. [版本規矩 (Version Rules)](#0-版本規矩-version-rules)
1. [Memory · 這份 repo 的 context](#1-memory-這份-repo-的-context)
1.5. [Memory · 最新版投影片進度（Current Deck Inventory）](#15-memory-最新版投影片進度current-deck-inventory)
2. [Memory · Brand Glossary（詞彙表）](#2-memory-brand-glossary詞彙表)
3. [Memory · Narrative Principles（敘事原則）](#3-memory-narrative-principles敘事原則)
4. [Skills · 怎麼加一個 slide](#4-skills-怎麼加一個-slide)
5. [Skills · Template 完整參考](#5-skills-template-完整參考)
6. [Skills · slides.yaml 語法與慣例](#6-skills-slidesyaml-語法與慣例)
7. [Skills · 派生新 deck（siam-paragon 做法）](#7-skills-派生新-deck-siam-paragon-做法)
8. [Skills · Setup · Python 環境 / API Key / .env](#80-setup-環境準備-python-api-key-env) · [用 Gemini 生成 infographic / hero image](#8-skills-用-gemini-生成-infographic--hero-image)
9. [Tools · build.py](#9-tools-buildpy)
10. [Tools · 影片與圖片素材庫](#10-tools-影片與圖片素材庫)
11. [Tools · generate\_\*.py 圖片生成腳本](#11-tools-generate_py-圖片生成腳本)
12. [Quirks · 已知陷阱與注意事項](#12-quirks-已知陷阱與注意事項)
13. [Recipes · 常見工作流](#13-recipes-常見工作流)
14. [衍生 deck · `ai-talk-deck`（AI 演講合併版）](#14-衍生-deck-ai-talk-deckai-演講合併版)

---

## 0 · 版本規矩 (Version Rules)

> 這節是 2026-06 版本對齊後新增的，**優先級最高**，違反會直接造成線上版本錯誤。

1. **這個 repo（`github.com/accucrazy/turncloud-presentation`）= 唯一正式來源。** 任何地方（網域、VM、其他 repo、本機資料夾）與這裡不一致，以這裡為準。
2. **正式發表 deck = repo 根目錄 `index.html`**，目前 **24 頁**（cover → trailer → … → 生態系 finale → redeem/QR）。歷史基準是 commit **`8aba57a`**（"Add 'one more thing' redeem slide with QR…"），之後又經多次內容/影片更新，**最新 commit `35950a9`（2026-06-23）**換上新的 Culture Listening / Motion Lab / Reels Studio demo `.mov`。逐頁內容見 [§1.5](#15-memory-最新版投影片進度current-deck-inventory)。
3. **歷史教訓**：曾有另一個 repo（`turncloudlaunch` / `tpc-launch-deck/v2`）的舊分支被誤部署到 `turncloud.thepocket.company`（缺 trailer + redeem）。**不要再從那個 repo 部署任何東西。** 那份 `tpc-launch-deck/v2/` 仍在工作機根目錄（含一個本 repo 沒有的 `slide_voc_compare.html` template 與 `pandora-case.html`），但**不是正式來源**。
4. 兩個部署（GitHub Pages + GCP VM 網域）**內容必須一致**，更新流程見 `README.md` §5 與本檔 §12。
5. 🔴 **建置來源與正式 deck 已脫鉤（升級版警告）**：經 2026-06-23 重新核對，**repo 內沒有任何一份 `slides.yaml` 能重建出目前的 canonical `index.html`**：
   - `tpc-launch/slides.yaml` = 26 頁（`cover / overview / aios_concept / workforce / harness_skill / 5 agents+demo / moana_case_02 / adriana_crm_capi / adriana_crm_demo / gfmc_academic / ecosystem`），**沒有 trailer、沒有 redeem**。
   - 棄用的 `tpc-launch-deck/v2/slides.yaml` = 27 頁（多了 `merger / runtime / problem / three_layers / closing`），同樣**沒有 trailer/redeem**，且 agent demo 編排不同。
   - canonical `index.html` 的內嵌註解（`<!-- SLIDE 02: trailer -->`…）顯示它**曾是 build 產物**，但來源那份 `slides.yaml`（含 trailer+redeem 的 24 頁版）目前**不在本 repo 內**（推測在 `turncloudlaunch` 那台機器或從未 commit）。
   - **結論**：目前**改正式 deck = 直接編輯根目錄 `index.html`**；`python build.py` 只用於 `tpc-launch/` 內的框架實驗，**產物絕不可覆蓋根目錄 deck**。把建置來源校正回 canonical（或改用 CodyML）是 `CODYML_PLAN.md` Phase 0 的前置工作。

---

## 1 · Memory · 這份 repo 的 context

### Repo 結構（現狀）

```
turncloud-presentation/             # Git repo: github.com/accucrazy/turncloud-presentation（★ canonical）
├── index.html                      # ★ 正式發表 deck（24 頁，基準 commit 8aba57a）— 手動維護，目前不是 build 產物
├── img/                            # ★ 主 deck 的 30 個資產（圖片 + demo 影片）
├── tpc-launch-en/                  # ★ 英文版發表 deck（手動翻譯自根目錄 index.html，資產用 ../img/ 共用）
├── tpc-launch/                     # 框架本體（build 系統）
│   ├── build.py                    # slides.yaml → index.html
│   ├── slides.yaml                 # ★ 編輯這個改內容（⚠ 目前是 5/28 舊版，見 §0.5）
│   ├── index.html                  # 已對齊根目錄正確版（資產以 ../img/ 指回根目錄）
│   ├── templates/                  # Jinja2 templates (slide_*.html + base.html + _macros.html)
│   ├── img/                        # 框架素材庫（肖像 / infographic / 動效背景 / 影片）
│   ├── generate_*.py               # 用 Gemini 生圖的腳本（一張圖一個腳本）
│   ├── requirements.txt / .env.example
│   └── .env                        # GEMINI_API_KEY（不入 git，本機自備）
├── tengyun-report/                 # 騰雲發表會 × Computex 口碑成效戰報（24 頁，含 Pandora 聲量轉位頁）
├── sharing/                        # Ian 個人分享 deck（UrCEO）— 獨立 HTML，不走 build.py
├── slides/ · aios.html · babycam-dtc/ · assets/   # 其他簡報 / 分享頁 / 素材
├── BRIEFING.md                     # 規矩 / 戰情手冊（敘事、商業模式、講稿）
├── README.md                       # repo 總說明 + 版本規矩 + 部署流程
└── SLIDE_FRAMEWORK.md              # ← 你正在看的這份（framework onboarding harness）
```

> **歷史 workspace 備註**：本檔早期版本寫的 `c:\dev\acqustion and sharing\` workspace（含 `siam-paragon/`、`acqusition/`、`kfc-ig-crawler/` 等）是另一台機器的本機資料夾，**不在這個 repo 內**。Siam Paragon 提案至今 local-only 未部署。當前作業 workspace 為 `d:\DEV\Turncloud Launch\`（內含本 repo 的 clone）。

### 我們已經做過什麼

| Deck | 路徑 | 語言 | 目的 |
|---|---|---|---|
| **TPC × TurnCloud 正式發表 deck** | `index.html`（repo root） | 中文 | TPC × TurnCloud 發表會 keynote（24 頁，⭐ 正式版本） |
| **英文版發表 deck** | `tpc-launch-en/` | 英文 | 同上內容的英文版（手動翻譯，非 build 產物） |
| **TPC launch framework** | `tpc-launch/` | 中文 | 整套 build framework 的源頭（slides.yaml + templates + generate scripts） |
| **騰雲口碑戰報** | `tengyun-report/` | 中文 | 騰雲發表會 × Computex 口碑成效報告（破百萬觀看 + Pandora 前後對比） |
| **UrCEO 分享** | `sharing/` | 中文 | Ian 對其他 CEO 分享被併購故事 |
| **Siam Paragon 提案** | （另一台機器 local-only） | 英文 | Siam Paragon Digital Space 導客提案（14 slides，未部署） |

### 線上部署（兩處，內容必須一致）

| 位置 | URL | 機制 |
|---|---|---|
| 自訂網域 | https://turncloud.thepocket.company/ （`/en/`、`/tengyun-report/`） | GCP VM `reel-studio` · nginx · `/var/www/deck/` · **手動同步** |
| GitHub Pages | https://accucrazy.github.io/turncloud-presentation/ | push `main` 自動發佈 |

---

## 1.5 · Memory · 最新版投影片進度（Current Deck Inventory）

> 這節記錄 **canonical `index.html` 此刻的實際內容**（2026-06-23 核對），讓接手的 agent 不必把 4000 多行 HTML 讀過一遍就知道「現在這份 deck 到底長怎樣、講什麼、用哪些素材」。
> 來源：repo 根目錄 `index.html`（HEAD = `35950a9`）。**這是手動維護的真實狀態，不是 `slides.yaml` 的內容**（見 §0.5）。

### 整份 deck 的敘事弧（一句話）

> **Cover（一起長大的生態系）→ Trailer 預告 → 三層架構（Runtime→AI OS→Agents）→ One OS·Two Spaces → 5 位 AI 員工總覽 → Harness Engineering 主圖 → 五位 Agent 逐一登場（每位「人物頁 + live demo」）→ 開放生態系（Raccoon/Rytho/Luna/CUHK）→ Finale（一起長大）→ One More Thing：送 100 點 Banana Split。**

### 逐頁清單（24 頁）

| # | id (`data-slide`) | template / variant | tone | 標題 / 重點 | 主要素材 |
|---|---|---|---|---|---|
| 01 | *(cover)* | `cover` | cyan | **Enterprise AIOS — 我們想要一起長大的生態系**；署名 **Ian Wu · CEO Accucrazy** | `cover_hero_santamonica.jpg` · accucrazy×turncloud logo |
| 02 | `trailer` | `trailer`（特製） | — | 全幅預告片，點擊開聲 | `trailer.mov` |
| 03 | `overview` | `overview` | cyan | **Physical Runtime → AI OS → AI Agents** 三層架構一圖看懂（CHAPTER 01） | `anim_runtime_iso` / `anim_aios_orb` / `anim_agents_ring` |
| 04 | `aios_concept` | `duality` | cyan | **One OS · Two Spaces**：同一套 AI OS 編排「實體」與「數位」兩種空間 | `space_physical.jpg` · `space_virtual.jpg` |
| 05 | *(workforce)* | `bg-violet`（workforce grid） | violet | **AI OS 之上 — 企業的 AI 工作者**：5 位 Agent chip 一字排開 | `07_workforce.jpg` |
| 06 | `harness_skill` | `fullbleed` | — | **Multi-Agent × Harness Engineering** 主圖（powered by TSpace · Turncloud VIN） | `harness_as_llm_input_v11b_final.jpg` |
| 07 | `pandora` | `agent` / `portraitL` | cyan | **Pandora — 看見市場的 AI**（AGENT 01） | `08_pandora.jpg` |
| 08 | `pandora_demo` | `demo` / `spotL` | cyan | Pandora 自動洞察 live demo | `pandora_demo.mov` |
| 09 | `moana` | `agent` / `portraitR` | orange | **Moana — 內容生成 · Culture Listening**（AGENT 02） | `09_moana.jpg` |
| 10 | `moana_culture_flow` | `demo` / `stacked` | orange | Moana Culture Listening 架構流程 | `moana_culture_flow.png` |
| 11 | `moana_culture_demo` | `demo` / `cinema` | orange | Culture Listening live demo　**🆕 6/23 換新片** | `culture_listening.mov` |
| 12 | `banana` | `agent` / `portraitL` | gold | **Banana — 視覺生成 AI**（AGENT 03） | `10_banana.jpg` |
| 13 | `banana_split_demo` | `demo` / `spotL` | gold | Banana Split / Motion Lab demo　**🆕 6/23 換新片** | `motion_lab.mov` |
| 14 | `banana_video_edit` | `demo` / `cinema` | orange | Reels Studio agentic 影片剪輯 demo　**🆕 6/23 換新片** | `reels_studio_demo.mov` |
| 15 | `adriana` | `agent` / `portraitR` | violet | **Adriana — 廣告優化 · CRM × CAPI**（AGENT 04） | `11_adriana.jpg` |
| 16 | `adriana_demo` | `demo` / `spotR` | violet | Adriana AI 廣告數據對話 demo | `adriana_demo.mov` |
| 17 | `stacey` | `agent` / `portraitC` | green | **Stacey — 總指揮 Orchestrator**（AGENT 05） | `12_stacey.jpg` |
| 18 | `stacey_demo` | `demo` / `spotL` | green | Stacey 多 Agent 調度 demo | `stacey_demo.mp4` |
| 19 | `ecosystem_chapter` | `chapter` / `side-hero` | cyan | 章節破題：**開放生態系** | `ecosystem_chapter_hero*` |
| 20 | `raccoon_partnership` | `demo` / `stacked` | cyan | Raccoon AI — 客服 AI 專家（私域對話回流 Pandora） | partner hero |
| 21 | `rytho_partnership` | `demo` / `stacked` | orange | Rytho — 懂台灣饒舌的 rapper AI | `rytho_demo.mp4` |
| 22 | `luna_partnership` | `demo` / `spotR` | orange | Luna AI — 複製靈魂的自媒體爆文專家 | `partner_luna_hero.png` |
| 23 | *(finale)* | `bg-dark` | cyan | **Finale — 在 AI 時代，一起長大的生態系**（Raccoon/Rytho/Luna + CUHK 2026 GFMC Madrid） | `finale_santamonica.jpg` |
| 24 | `redeem` | `redeem`（特製） | orange/cyan | **One More Thing**：送現場貴賓 **100 點 Banana Split 試用點數** + QR | `banana_redeem_qr.png` |

> 註：第 01 / 05 / 23 頁沒有 `data-slide` 屬性（cover / workforce / finale 是版型特製頁）；頁碼以 deck 內 `NN / 24` 為準。

### 與舊版 `slides.yaml` 的差異（為什麼不能直接 rebuild）

canonical `index.html`（24 頁）**比 `tpc-launch/slides.yaml`（26 頁）多了**：`trailer`(02)、`redeem`(24)、三個 partner 頁的具體編排、finale 改寫。
**少了**（被砍 / 合併）：`moana_case_02`、`adriana_crm_capi`、`adriana_crm_demo`、`gfmc_academic`（併進 finale）、舊 `ecosystem` 頁。
→ 任何一邊直接 build 都會把對方的差異洗掉。**改正式 deck 一律直接編 `index.html`。**

### 近期更新軌跡（git log 摘要）

| commit | 日期 | 內容 |
|---|---|---|
| `35950a9` | **2026-06-23** | 換上新的 Culture Listening / Motion Lab / Reels Studio demo `.mov`（slide 11/13/14） |
| `b6ba37f` | 2026-06-13 | 新增本 `SLIDE_FRAMEWORK.md` + 修 README |
| `161bb0c` | 2026-06 | 新增英文版 `tpc-launch-en/` |
| `0637a09` | 2026-06 | repo 根目錄加 `BRIEFING.md` |
| `95a801e` | 2026-06 | 把 `tpc-launch/` 內 deck 對齊到根目錄正確版（資產改 `../img/`） |
| `8aba57a` | 2026-05 | redeem/QR「one more thing」頁（版本規矩的歷史基準） |
| `bf29f8c` | 2026-05 | trailer 片頭頁 |
| `dcbc278` | 2026-05 | harness diagram v11b（agent 用官方肖像 + Digital World） |

> 另有一條 `tengyun-report/` 的更新線（騰雲 × Computex 口碑戰報：Pandora 聲量轉位頁、Facebook 跨平台、量價圖嵌貼文小截圖），與主 deck 平行維護。

---

## 2 · Memory · Brand Glossary（詞彙表）

> 這套詞彙系統是我們在多次 deck 迭代中固定下來的，**新 agent 要嚴格依照使用**，不要自由發揮替換。

### 母組織 · 平台層

| 詞 | 全稱 / 解釋 | 用法 |
|---|---|---|
| **TurnCloud** | 騰雲科技（母公司）。也是「Turncloud VIN」這個地端模型的 brand owner | Turncloud / 騰雲 兩種寫法都用 |
| **Accucrazy** | 肖準行銷（被併購的子公司，Ian 的公司）| **絕對不要寫成「肖準」** — 早期 deck 有錯，已全部替換成 Accucrazy |
| **The Pocket Company (TPC)** | Accucrazy × Turncloud 整合後做出來的 AI OS 子品牌 | 「The Pocket Company」或「TPC」 |
| **TSpace** | TPC 之下、由 Turncloud 撐起的 AI OS 架構名 · 也是 Multi-Agent + Harness Engineering 的容器 | "Powered by TSpace" / "framework by TSpace" |
| **Turncloud VIN** | 騰雲基於 NVIDIA Nemotron 為 TSpace 優化的**地端模型** | 出現在「SOTA / 地端」並列時 |
| **AI OS** | "AI Operating System" 也是 "Agent Orchestrated Space" — 同時編排**實體空間**與**數位空間** | 大寫 |

### 5 個 AI Agent（順序固定）

| Code | 中文角色 | 英文 role | 顏色 | 肖像檔 |
|---|---|---|---|---|
| **Pandora** | 輿情洞察 Agent | Market Intelligence / Listening | `cyan` | `08_pandora.jpg` |
| **Moana** | 內容生成 Agent · Culture Listening | Content / Culture Listening | `orange` | `09_moana.jpg` |
| **Banana** | 視覺生成 Agent | Visual Generation | `gold` | `10_banana.jpg` |
| **Adriana** | 廣告優化 Agent · CRM × CAPI | Ad / Personalization | `violet` | `11_adriana.jpg` |
| **Stacey** | 總指揮 Agent · Orchestrator | Orchestrator | `green` | `12_stacey.jpg` |

> Agent 名字大小寫：英文標題用 `Pandora`（capitalized），label/code 用 `PANDORA` (uppercase mono)。

### 技術名詞

| 詞 | 解釋 |
|---|---|
| **Harness** | LLM 的 input bundle = `skill + tool` 整捆塞進去。Harness Engineering 是 2026 新興詞 |
| **A2A** | Agent-to-Agent protocol。Agent 互相對話協作 |
| **MCP** | Model Context Protocol。Agent 取資源的標準 |
| **TCRM** | Turncloud CRM master |
| **TCDP** | Turncloud Customer Data Platform |
| **CAPI** | Meta Conversions API。第一方數據回傳 Meta |
| **Tool Universe** | Harness 圖中底部那條 band — DataLake / CDP / MDP / BigQuery / POS / 刷卡機 / IoT |

### 三層架構（重要 mental model）

```
LAYER 03 · AGENTS    AI Agent Workforce        violet  ← Pandora / Moana / Banana / Adriana / Stacey
LAYER 02 · AI OS     Enterprise AI OS          cyan    ← 編排層 · Orchestrator · A2A · MCP · Memory · Policy · Governance
LAYER 01 · RUNTIME   Physical Space Runtime    orange  ← by 騰雲 · 讓 AI 進入實體空間
```

**口訣：** `One OS · Two Spaces · Five Agents`

---

## 3 · Memory · Narrative Principles（敘事原則）

> 這些是經 Ian 多次反饋固定下來的「**怎麼說故事**」原則。新 agent **要嚴格遵守**，不然會被退稿。

### Principle 1 · Real Content Wins, Not Cookie Death

❌ 不要寫：「Cookie 退場 → 所以要建第一方數據」（這是被動、技術導向的論述）
✅ 要寫：「人們渴望真實內容 → 所以要從口碑經營 → 互動 → 標籤 → 投放」（主動、用戶導向）

**為什麼：** 整個 5-stage user journey 第一步就是 **Word-of-Mouth Inflow**（不是廣告）。論述必須對齊這個前提。

### Principle 2 · 不要過度堆砌數字 / 縮寫

- 不要 prefix 一堆 "PE 7-10x · EPS 提升 · NDR 237 萬" — 除非原始檔案就有
- 不要自己生數字（ROAS 3-5x、CTR +15-30% 這類是業界常識區間，可以保留，但要謹慎）
- **不要新增 Ian 沒提過的具體數字**

### Principle 3 · Subject-First, 對話感

- 對話感的句子比 PPT 條列風更有力（「酒吧聊天」風格）
- 標題要短、有畫面感
- `tagline` 要有「金句」感，不是 summary

### Principle 4 · Ian 的具體用詞偏好

| 偏好的詞 | 避免的詞 |
|---|---|
| 真實內容 / 真實口吻 / 在地語境 | "user-generated content" 學術詞 |
| 自己擁有的 / owned / sovereign | "monetize" / "leverage" |
| 飛輪 / 閉環 / 自我演化 | "synergy" / "ecosystem" 空洞詞 |
| 整捆塞進 / 一氣呵成 | "robust integration" |
| **Accucrazy** | ~~肖準~~（這個已淘汰） |

### Principle 5 · 區分 audience

| Audience | 應該強調 | 不要碰 |
|---|---|---|
| 給 CEO 的分享 | mindset、心理、捨不得、PE/PS 概念 | 細部技術 |
| 給上市公司母公司董事會 | EPS 貢獻、毛利率、人才即庫存 | startup 黑話 |
| 給品牌客戶（如 Siam Paragon）| user journey、ROAS、第一方數據 | 我們自己的併購故事 |
| 給其他 AI 公司 / TPC keynote | Harness / A2A / Multi-Agent / Tool Universe | 客戶案例細節 |

---

## 4 · Skills · 怎麼加一個 slide

### 最小範例（一個 chapter break slide）

在 `slides.yaml` 的 `slides:` list 中加一塊：

```yaml
  # ─── SLIDE NN: 你的 slide 名稱 ───────────────────────────────
  - id: my_new_slide                 # 必填，唯一字串，當 HTML data-slide
    template: chapter                # 必填，從第 5 節清單選一個
    tone: cyan                       # 該 slide 主色（cyan/violet/orange/green/gold/pink）
    eyebrow: "CHAPTER · WHATEVER"    # 上方小標
    title: 'Why <span class="c">this</span> matters'   # 主標，可內嵌 HTML
    lede: 'Supporting paragraph with <strong>emphasis</strong>.'
    bullets:                         # 3 個 bullets 排成 grid
      - { tone: cyan,   label: "01 · POINT A", text: 'First reason ...' }
      - { tone: orange, label: "02 · POINT B", text: 'Second reason ...' }
      - { tone: violet, label: "03 · POINT C", text: 'Third reason ...' }
    tagline: 'A punchy closing line.'
    meta_left: "Footer left text"
```

存檔後：

```powershell
cd turncloud-presentation\tpc-launch    # 或 siam-paragon
python build.py
```

`✓ Built index.html — N slides` 出現即成功。重新整理瀏覽器即可看到。

### 開發循環（recommended）

```powershell
python build.py --watch    # 監看 slides.yaml + templates/，存檔自動重 build
```

然後另開瀏覽器分頁，每次存檔重新整理。

---

## 5 · Skills · Template 完整參考

`turncloud-presentation/tpc-launch/templates/` 目前有 13 個 slide template：

### `cover` · 封面頁

```yaml
- id: cover
  template: cover
  media: img/01_cover.jpg              # 背景圖（可為 .mp4/.mov → 自動轉 <video>）
  logos:                               # 選用：兩個 logo + × 符號
    left:  { src: "img/accucrazy-logo.webp", alt: "Accucrazy",  brand: "accucrazy" }
    right: { src: "img/turncloud-logo.png",  alt: "TurnCloud",  brand: "turncloud" }
  pre: "PROPOSAL · 2026"               # 標題上方小字
  title: 'Big <span class="c">colored</span> title'
  lede: 'Multi-line lede paragraph.'
  signatures:
    - { strong: "Powered by", text: "TPC × Turncloud" }
    - { strong: "Designed for", text: "Whatever 2026" }
```

> 已定義 `cover-logo-*` CSS class：`accucrazy` / `turncloud`。其他 brand 名會走 default 樣式。

### `chapter` · 章節破題頁（大標 + 3 bullets）

```yaml
- id: my_chapter
  template: chapter
  tone: cyan
  hero_image: img/something.jpg        # 選用：full-bleed 背景圖
  eyebrow: "CONTEXT"
  title: '<span class="c">Big title</span>'
  lede: '一段論述...'
  bullets:                             # 固定 3 個（CSS grid 3 cols）
    - { tone: cyan,   label: "01", text: '...' }
    - { tone: orange, label: "02", text: '...' }
    - { tone: violet, label: "03", text: '...' }
  tagline: '收尾金句'
  audio: img/some-music.mp4            # 選用：slide 進入時自動播音樂
```

### `demo` · 影片 / 圖片 demo（4 種 variant）

```yaml
- id: my_demo
  template: demo
  variant: cinema                      # cinema / spotL / spotR / stacked
  tone: violet
  backdrop: img/anim_backdrop.jpg
  media: img/some_video.mp4            # ★ 主角：影片 or 圖
  media_fit: contain                   # contain / cover
  media_alt: "Description"
  marker: "● LIVE · DEMO"              # 左上角的小標
  tag: { color: violet, text: "TAG TEXT" }
  title: '主標'
  subtitle: '副標'
  pills:                               # 選用：底部 1–3 個 pill 卡片
    - tone: violet
      label: "WHAT IT DOES"
      name: "Closed-loop insight"
      bullets:
        - 'point 1'
        - 'point 2'
  tagline: '收尾金句'                  # 選用
  audio: true                          # 選用：影片 controls 開、不 muted
  meta_left: "Footer left"
```

| variant | 用法 |
|---|---|
| `cinema` | 全幅影片，文字以玻璃卡浮在上方（最 dramatic） |
| `spotL` | 影片佔左 66%，文字在右邊 column |
| `spotR` | 鏡像 spotL |
| `stacked` | 標題上、巨大 media 中、pills 下 — **infographic 通常用這個** |

### `stage` · 階段流程（多 panel 橫列）

```yaml
- id: my_stage
  template: stage
  tone: cyan
  backdrop: img/anim_backdrop.jpg
  arrows: true                         # 選用：panel 之間畫箭頭
  tag: { color: cyan, text: "STAGES" }
  title: 'Five stages'
  subtitle: '...'
  panels:                              # 支援 3 / 4 / 5 個 panel
    - tone: cyan
      art: img/08_pandora.jpg          # 選用：panel 內的圖（可為影片）
      art_fit: cover                   # cover / contain
      label: "STAGE 01"
      name: 'Title<br>two lines'
      bullets: ['point 1', 'point 2']
      body: '一段論述'
      via: 'via something'             # 選用：底部小字
    # ... 重複 N 個 panel
  tagline: '收尾金句'
  meta_left: "Footer left"
```

> `panel.wide: true` 可讓單一 panel 寬度為 1.6× 其他。

### `two_col` · 媒體 + 多個 box（左圖右文）

```yaml
- id: my_two_col
  template: two_col
  bg: dark                             # dark / warm / cover（控背景）
  media: img/some_image.jpg
  media_alt: "..."
  media_fit: cover
  media_flex: "1.1"                    # 選用：左欄 flex 值（讓圖更大）
  tag: { color: violet, text: "..." }
  title: '...'
  subtitle: '...'
  boxes:                               # 右欄一疊 box
    - color: violet
      title: '<strong>Box title</strong>'
      bullets: ['point 1', 'point 2']
    - color: cyan
      title: '<strong>Another</strong>'
      body: '一段純文字 body'           # body 跟 bullets 二選一
  meta_left: "Footer left"
```

### `agent` · Agent 個人介紹（portrait + blocks）

```yaml
- id: pandora
  template: agent
  variant: portraitC                   # portraitL / portraitR / portraitC
  tone: cyan
  backdrop: img/anim_backdrop.jpg
  portrait: img/08_pandora.jpg         # ★ Agent 肖像
  codename: "AGENT 01 · PANDORA"
  tag: { color: cyan, text: "AGENT 01 / 05" }
  title: '<span class="c">Pandora</span> — 看見市場的 AI'
  subtitle: '...'
  blocks:                              # 通常 2–3 個 block
    - tone: cyan
      label: "WHAT SHE DOES"
      name: '她做什麼'
      bullets: ['...']
    - tone: orange
      label: "TECH"
      name: '底層技術'
      body: '...'
  meta_left: "Pandora — ..."
```

### `closing` · 結尾頁

```yaml
- id: closing
  template: closing
  media: img/14_closing.jpg            # 全幅背景
  quote: '<strong>One bold quote</strong> as the closing line.'
  lede: 'Supporting paragraph.'
  sig: 'TPC × TURNCLOUD · 2026'
```

### 其他可用 template

| Template | 用途 |
|---|---|
| `overview` | 三層架構一張圖看懂（Layer 01/02/03） |
| `duality` | One OS · Two Spaces（左實體空間 / 右數位空間 split layout） |
| `aios_split` | AI OS 雙空間變形 |
| `workforce` | "5 位 Agent 一字排開"頁（pre-agent intro） |
| `ecosystem` | 開放生態系（partner brands、模組陳列） |
| `layers` | 多層架構展示（替代 demo cinema 的另一種視覺） |

> 進階用法請直接讀對應的 `templates/slide_*.html` — 它們是 Jinja2，欄位都自我說明。

---

## 6 · Skills · slides.yaml 語法與慣例

### Inline HTML (重要！)

`title` / `subtitle` / `lede` / `body` / `bullets` 都會被 `| safe` 渲染，**可以放 HTML**。

| 語法 | 用途 |
|---|---|
| `<br>` | 強制換行（標題常用） |
| `<strong>...</strong>` | 粗體 |
| `<span class="c">...</span>` | cyan 著色文字 |
| `<span class="v">...</span>` | violet 著色 |
| `<span class="o">...</span>` | orange 著色 |
| `<span class="g">...</span>` | green 著色 |
| `<span class="p">...</span>` | pink 著色 |
| `<strong class="c">...</strong>` | 粗體 + 著色（最強調） |

### YAML 字串 quoting

優先順序（為了避免 escape 地獄）：

1. 不含特殊字符 → 不加引號
2. 內含 `"` → 用單引號包：`'He said "hello"'`
3. 內含 `'` → 用雙引號包：`"It's working"`
4. 多行 → 用 `|-`：

```yaml
lede: |-
  Line 1<br>
  Line 2 with <strong>bold</strong>
```

### 常見錯誤

| 錯誤 | 結果 | 修法 |
|---|---|---|
| 用 `items:` 而非 `bullets:` | Jinja 拿到 `dict.items` 方法，不是 list | **永遠用 `bullets:`** |
| 漏寫 `template:` | build 直接報錯 `缺少 template 欄位` | 補上 |
| 路徑寫 `./img/...` | 變成 `././img/...` 在某些瀏覽器壞 | 用 `img/...`，不加 `./` |
| YAML 縮排錯 | build 報 `expected ..., got ...` | YAML 嚴格 2-space，不要 tab |
| 在中文字串裡漏掉 quotes | Parser 行為不可預期 | 含全形標點時務必加引號 |

### Tone 與 color 對照（slide 內顏色系統）

| YAML value | CSS class | 字串顏色 (`<span>`) |
|---|---|---|
| `cyan` | `tag-cyan / chapter-bullet-cyan / ...` | `<span class="c">` |
| `violet` | `... -violet` | `<span class="v">` |
| `orange` | `... -orange` | `<span class="o">` |
| `green` | `... -green` | `<span class="g">` |
| `gold` | `... -gold` | (沒專屬 inline class) |
| `pink` | `... -pink` | `<span class="p">` |

---

## 7 · Skills · 派生新 deck（siam-paragon 做法）

當你需要做一份**新主題、新語言、但要沿用同套視覺**的 deck：

```powershell
# 1. 建資料夾 + 複製 framework 核心
$NEW = "new-deck"
mkdir $NEW
mkdir "$NEW\assets"
Copy-Item turncloud-presentation\tpc-launch\build.py $NEW\
Copy-Item -Recurse turncloud-presentation\tpc-launch\templates $NEW\templates

# 2. 用 NTFS junction 重用所有 img 素材（不複製大檔）
cmd /c mklink /J "$NEW\img" "C:\dev\acqustion and sharing\turncloud-presentation\tpc-launch\img"

# 3. 複製 .env (GEMINI_API_KEY)，如果你之後要生圖
Copy-Item turncloud-presentation\tpc-launch\.env $NEW\.env

# 4. （如果是英文版）改 templates/base.html：
#    - <html lang="zh-Hant"> → <html lang="en">
#    - rotate-prompt 內的中文改英文
#    - <link href=Inter:...> 加 Inter 字型

# 5. 寫一份新的 slides.yaml（從零或複製改寫）
# 6. python build.py → index.html
```

> 為什麼用 junction：影片 (.mov) 動輒 30–70 MB，複製浪費空間且兩邊容易脫鉤。junction 讓兩 deck 共享同一份 source of truth，且 `slides.yaml` 中路徑寫 `img/foo.mp4` 直接 work。
>
> **限制**：junction 是 Windows local-only；deploy 到 GitHub Pages 時要記得把實際素材複製進去，或在 deploy 腳本處理。Siam Paragon 提案目前是 local-only，未 deploy。

---

## 8.0 · Setup · 環境準備 (Python · API Key · .env)

> 跑 `build.py` 只需 Python + YAML + Jinja2。
> 跑 `generate_*.py` 多需要 **GEMINI_API_KEY** 才能呼 Gemini API。
> 兩件事**分開**設定。

### A · Python 依賴

`turncloud-presentation/tpc-launch/requirements.txt` 列：

```text
Jinja2>=3.1.0           # build.py 渲染 templates
PyYAML>=6.0             # 讀 slides.yaml
google-genai>=0.3.0     # （備用：official SDK）
python-dotenv>=1.0.0    # generate_*.py 讀 .env
```

但我們現在的 `generate_*.py` 直接用 `requests` 打 REST API（不走 google-genai SDK），所以**實際還需要**：

```text
requests>=2.31.0
```

一次裝齊：

```powershell
cd turncloud-presentation\tpc-launch
pip install -r requirements.txt requests
```

> 如果 PowerShell 用 conda env / venv：先 activate 再 pip install。

### B · GEMINI_API_KEY 從哪來

1. 開 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 用 Google 帳號登入
3. 按 **「Create API key」** → 拿到一串 `AIzaSy...` 開頭的字串
4. **重要**：那串 key 等同密碼，**不要 commit 進 git**

### C · 把 key 放進 .env

每個會跑 generate script 的目錄都需要自己的 `.env`：

```
turncloud-presentation/tpc-launch/.env         ← 主 deck 用
siam-paragon/.env                              ← Siam Paragon deck 用
<未來新 deck>/.env                              ← 派生新 deck 時要複製
```

`.env` 內容（就一行夠用）：

```env
GEMINI_API_KEY=AIzaSy_your_actual_key_here
```

> generate scripts 同時支援 `GEMINI_API_KEY` 和 `GOOGLE_API_KEY`，任一即可。
> `.env.example`（已 commit）長這樣，**請拿來當範本**：
>
> ```env
> GOOGLE_API_KEY=AIzaSy_your_key_here
> GEMINI_MODEL=gemini-2.5-flash
> ```
>
> 注意：`.env.example` 寫的是舊 model 名稱 `gemini-2.5-flash`，但我們的 generate scripts 寫死用 **`nano-banana-pro-preview`**（image generation 模型），所以 `GEMINI_MODEL` 那行可以無視。

### D · 現狀（這 repo 內已存在的 .env）

| 路徑 | 狀態 |
|---|---|
| `turncloud-presentation/tpc-launch/.env` | ✅ 已設定，可直接跑 |
| `siam-paragon/.env` | ✅ 已設定（從 tpc-launch 複製過來） |

複製方式（派生新 deck 時）：

```powershell
Copy-Item turncloud-presentation\tpc-launch\.env <new-deck>\.env
```

### E · 確認 key 有效（30 秒測試）

```powershell
cd turncloud-presentation\tpc-launch
python -c "import os; from dotenv import load_dotenv; load_dotenv(); k=os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY'); print('OK' if k and k.startswith('AIza') else 'MISSING')"
```

預期輸出：`OK`

或直接跑一支現成腳本看會不會 crash：

```powershell
python generate_harness_diagram_v4.py
# 預期看到: generating harness_as_llm_input_v4 ... (N refs)
#          saved harness_as_llm_input_v4.jpg (~1.3MB, ~30s)
```

### F · Gemini API 重點參數（generate_*.py 都這樣設）

| 參數 | 值 | 說明 |
|---|---|---|
| Model | `nano-banana-pro-preview` | image generation 用這個，不是 `gemini-2.5-flash` |
| Endpoint | `https://generativelanguage.googleapis.com/v1beta/models/<MODEL>:generateContent?key=<KEY>` | REST |
| `responseModalities` | `["IMAGE"]` | 只要圖不要文字 |
| `imageConfig.aspectRatio` | `"16:9"` | keynote 標準。infographic 也用這個 |
| `timeout` | `300` | 30 秒太短，Gemini 偶爾要 60s+ |
| Retry | 3 次，遇到 `429/500/502/503/504` 倒退 backoff | 已寫進 `call_api()` |

### G · 已知 rate-limit / cost 警示

- Gemini API 免費 tier 有 daily quota，密集生圖會撞上
- 生一張 16:9 圖約 30–40 秒；失敗會自動 retry 最多 3 次
- 若連續失敗：先檢查 quota，再檢查 key 是否被 revoke
- 不要把 `.env` push 到 GitHub — `.gitignore` 已包含 `.env` 但別人 fork 後可能還是要重新設

### H · `.gitignore` 須包含的項目

```gitignore
.env
.env.local
__pycache__/
*.pyc
```

主 repo (`turncloud-presentation/.gitignore`) 已包含這些。**派生新 deck 時記得也加 `.gitignore`**。

---

## 8 · Skills · 用 Gemini 生成 infographic / hero image

我們用 Google Gemini 的 `nano-banana-pro-preview` 模型生成所有 hero image / infographic。

> 環境準備請先看 §8.0。下面假設你的 `.env` 已經有 `GEMINI_API_KEY`。

### 模板 script（一張圖一個檔，命名 `generate_<thing>.py`）

```python
"""
Generate: <在這寫這張圖做什麼用>
Outputs: <相對路徑>
"""
import base64, json, mimetypes, os, sys, time
from pathlib import Path
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")
API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not API_KEY:
    raise SystemExit("Set GEMINI_API_KEY in .env")

MODEL = "nano-banana-pro-preview"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

OUT_DIR = ROOT / "img"           # 或 "assets"
OUT_DIR.mkdir(exist_ok=True)

# Reference 圖（強烈建議：給一張既有 reference 維持 style）
REF = OUT_DIR / "some_reference.jpg"

def load_ref(path, label):
    if not path.exists(): return []
    mime, _ = mimetypes.guess_type(str(path))
    return [
        {"text": f"Reference — {label}: keep style/palette consistent."},
        {"inline_data": {"mime_type": mime or "image/jpeg",
                         "data": base64.b64encode(path.read_bytes()).decode()}},
    ]

STYLE = (
    "STYLE: ... 詳細描述風格 ..."
)

PROMPT = """
... 詳細描述構圖、文字、layout ...

TEXT ACCURACY — 列出所有要正確渲染的英文/中文字串
"""

def call_api(prompt, refs, attempt=1, max_attempts=3):
    parts = []
    for r in refs: parts.extend(r)
    parts.append({"text": prompt})
    parts.append({"text": STYLE})
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": "16:9"},
        },
    }
    try: r = requests.post(URL, json=payload, timeout=300)
    except Exception as e:
        if attempt < max_attempts:
            time.sleep(5 * attempt); return call_api(prompt, refs, attempt+1, max_attempts)
        return None
    if r.status_code != 200:
        print(f"http {r.status_code}: {r.text[:600]}")
        if r.status_code in (429,500,502,503,504) and attempt<max_attempts:
            time.sleep(10*attempt); return call_api(prompt, refs, attempt+1, max_attempts)
        return None
    data = r.json()
    for c in data.get("candidates", []):
        for p in c.get("content", {}).get("parts", []):
            inline = p.get("inlineData") or p.get("inline_data")
            if inline and inline.get("data"): return base64.b64decode(inline["data"])
    print("no image:", json.dumps(data, ensure_ascii=False)[:500])
    return None

def main():
    out_name = sys.argv[1] if len(sys.argv) > 1 else "output_name"
    refs = [load_ref(REF, "previous version")]
    refs = [r for r in refs if r]
    print(f"generating {out_name}...", flush=True)
    t0 = time.time()
    data = call_api(PROMPT, refs)
    if data is None: print("FAILED"); return 1
    ext = "png" if data[:8] == b"\x89PNG\r\n\x1a\n" else "jpg"
    out = OUT_DIR / f"{out_name}.{ext}"
    out.write_bytes(data)
    print(f"saved {out.name} ({len(data)//1024} KB, {time.time()-t0:.1f}s)")
    return 0

if __name__ == "__main__": sys.exit(main())
```

### Prompt 工程心得（從 harness v1 → v4 + capi_flow_en 累積）

1. **永遠給一張 reference**。用前一版作 reference 可以維持 style/palette/character consistency
2. **明列 TEXT ACCURACY 區塊**：把所有要正確渲染的英文/中文字串一條一條列出來。Gemini 對拼字/中文相對弱，明列可以提升正確率
3. **拒絕清單也要寫**：`NO stock-icon-pack iconography` / `NO photorealism` / `NO Chinese characters` 等
4. **STYLE 跟 PROMPT 分兩段傳**（先 PROMPT 再 STYLE，或反之），模型對「分段指令」比一坨指令理解更好
5. **角色一致性**：肖像類圖把 5 個 agent portraits 同時當 reference 傳進去（每張附 label），可大幅提升角色相似度
6. **小瑕疵接受**：常見小瑕疵（多餘 watermark 字 / 標籤錯位 / `JetBrains Mono` 殘字）— 若不影響主訊息，直接 ship；要 polish 就重跑（同 prompt 通常會略有不同）
7. **檔名版本化**：`harness_v1 → v2 → v3 → v4`，不要 overwrite，方便回溯

### 完整 worked example

最完整的 reference example 是這兩個檔：

- `turncloud-presentation/tpc-launch/generate_harness_diagram_v4.py`
  → Pixar 3D keynote hero, 多角色一致性, A2A + Tool Universe + Harness Manual + LLM Orb 整場景
- `siam-paragon/generate_capi_flow_en.py`
  → 2D flat web infographic, 多 card layout + 右側 panel + 底部 outcome row + footnote

直接複製改 prompt 是最快路徑。

---

## 9 · Tools · build.py

`turncloud-presentation/tpc-launch/build.py`（也是 `siam-paragon/build.py` 的同一份副本）：

```
python build.py                       # 一次 build
python build.py --watch               # 監看模式
python build.py --out preview.html    # 輸出到別的檔
```

### 內部邏輯

1. 讀 `slides.yaml` → 拿 `meta` + `slides[]`
2. 對每個 slide：根據 `template` 欄位找對應 `templates/slide_<template>.html`，用 Jinja2 渲染
3. 把每個 slide 渲染結果串成一坨 HTML，塞進 `templates/base.html` 的 `{{ slides_html | safe }}`
4. 寫進 `index.html`

### `SilentUndefined` quirk

build.py 用 `SilentUndefined` — **不存在的變數會渲染成空字串**，不會炸掉。
這對快速開發很友善，但要小心**拼錯欄位名不會報錯**，只是該欄位變空。
找問題時：直接看產出的 `index.html`，看缺什麼。

### 終端 encoding

Windows PowerShell 跑 build 時遇到 `UnicodeEncodeError`，先設定 UTF-8：

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null
python build.py
```

---

## 10 · Tools · 影片與圖片素材庫

**集中地：`turncloud-presentation/tpc-launch/img/`**

### Agent 肖像（重要！永遠用這 5 張作 reference）

| File | Agent | Color |
|---|---|---|
| `08_pandora.jpg` | Pandora — silver-haired woman in grey suit | cyan |
| `09_moana.jpg` | Moana — curly-afro woman with pink megaphone, orange tee | orange |
| `10_banana.jpg` | Banana — yellow banana mascot, round glasses, bow tie | gold |
| `11_adriana.jpg` | Adriana — brunette woman, round glasses, sage blazer, glowing tablet | violet |
| `12_stacey.jpg` | Stacey — dark-brown high-ponytail, dark-navy blazer, holographic stylus | green |

### Demo 影片

> ★ = canonical `index.html`（24 頁）**目前實際引用中**的影片，對應頁碼見 §1.5。🆕 = 2026-06-23 commit `35950a9` 換上的新錄影。

| File | 用在哪頁 | 用途 |
|---|---|---|
| `trailer.mov` ★ | 02 trailer | 全幅預告片（點擊開聲） |
| `pandora_demo.mov` ★ | 08 | Pandora 自動洞察報告 demo |
| `culture_listening.mov` ★ 🆕 | 11 moana_culture_demo | Moana Culture Listening 錄影（31 MB） |
| `motion_lab.mov` ★ 🆕 | 13 banana_split_demo | Banana / Motion Lab demo（53 MB） |
| `reels_studio_demo.mov` ★ 🆕 | 14 banana_video_edit | Reels Studio agentic 剪輯 demo（50 MB） |
| `adriana_demo.mov` ★ | 16 | Adriana AI 廣告數據對話 demo |
| `stacey_demo.mp4` ★ | 18 | Stacey orchestration demo |
| `rytho_demo.mp4` ★ | 21 | Rytho（rapper AI partner）demo |
| `moana_culture_case.mp4` | （舊版/備用） | Moana culture listening · 猛健樂 case |
| `moana_case_02.mov` | （舊版/未引用） | Moana case 2（69 MB，舊 slides.yaml 才有的 `moana_case_02` 頁） |
| `banana_split_demo.mp4` / `banana_video_demo.mp4` | （舊版/備用） | 早期 Banana demo，已被上面的新 `.mov` 取代 |
| `adriana_crm_demo.mov` | （舊版/未引用） | Adriana CRM × CAPI demo（舊 `adriana_crm_demo` 頁，現已砍） |

### Chapter / Cover heroes

| File | 用途 |
|---|---|
| `01_cover.jpg` ~ `14_closing.jpg` | Main deck 各章節 hero（依編號對應 slide） |
| `cover_hero_pandora.jpg` | Pandora-led keynote cover |
| `cover_hero_santamonica.jpg` | Santa Monica 海邊辦公室 hero |
| `cover_hero_square.jpg` | 方形 hero variant |
| `finale_santamonica.jpg` | 結尾 hero（搭 cover） |
| `ecosystem_chapter_hero.jpg` | Ecosystem chapter break |

### Infographic / 架構圖

| File | 用途 |
|---|---|
| `aios_infographic_v2/v3/v4.jpg` | One OS · Two Spaces 主架構圖 |
| `harness_as_llm_input_v2..v8/v11b_final.jpg` | Harness Engineering 主圖（多代演進） |
| `adriana_crm_capi_flow.png` | AI CRM × Meta CAPI 流程圖（中文）|
| `siam-paragon/assets/stage04_capi_flow_en.jpg` | 同上但**英文版** |
| `banana_split_flow.png` | Banana Split data flow |
| `moana_culture_flow.png` | Moana Culture Listening 架構 |

### Animated backdrops

| File | 用途 |
|---|---|
| `anim_backdrop.jpg` | 預設 backdrop（demo/stage 預設值） |
| `anim_aios_orb.jpg` | AI OS orb 動效背景 |
| `anim_agents_ring.jpg` | Agent ring（5 agent 環繞構圖） |
| `anim_runtime_iso.jpg` | Runtime 等軸測 |

### Space duality

| File | 用途 |
|---|---|
| `space_physical.jpg` | 實體空間 — POS/工廠/門市 |
| `space_virtual.jpg` | 數位空間 — agents collaborating |

### Logo

| File | Notes |
|---|---|
| `accucrazy-logo.webp` | Accucrazy logo |
| `turncloud-logo.png` | Turncloud logo |
| `tspace_logo.png` | TSpace logo |

### Icons (16 個 small flat illustrations)

`icon_*.jpg` — 小型 flat-style illustration，用在 ecosystem / stage panels 等。常見：
`icon_agent_team / icon_challenge / icon_fusion / icon_legacy_infra / icon_runtime_engine / icon_scattered_tools / icon_unify_os / icon_user_memory / icon_voc_fusion / ...`

---

## 11 · Tools · generate_*.py 圖片生成腳本

### 既存的腳本

| Script | 產出 | 風格 |
|---|---|---|
| `tpc-launch/generate_anim_assets.py` | `anim_*.jpg` 四張動效背景 | abstract animation |
| `tpc-launch/generate_duality_assets.py` | `space_physical.jpg` / `space_virtual.jpg` | dual-space illustration |
| `tpc-launch/generate_aios_infographic.py` | `aios_infographic_v3.jpg` | 雙欄式 infographic |
| `tpc-launch/generate_stage_panels.py` | `icon_*.jpg` 多個 | small flat illustrations |
| `tpc-launch/generate_ecosystem_chapter_hero.py` | `ecosystem_chapter_hero.jpg` | chapter hero |
| `tpc-launch/generate_harness_diagram.py` ~ `_v4.py` | `harness_as_llm_input_v*.jpg` | Pixar 3D keynote hero (4 iterations) |
| `siam-paragon/generate_capi_flow_en.py` | `stage04_capi_flow_en.jpg` | 2D flat web infographic |

### 跑哪一支看哪一支

每支腳本都自帶 prompt + style + ref，互相獨立可單跑：

```powershell
cd turncloud-presentation\tpc-launch    # or siam-paragon
python generate_harness_diagram_v4.py   # 跑哪支看你要重跑哪張
```

### 何時自己寫一支新的 vs 修改既有

- **修既有** 如果你只是要 polish 同一張圖的細節（例如 v3 → v4）
- **新寫一支** 如果這是一張**完全不同主題**的圖（例如 Siam Paragon 專屬的 CAPI flow）

---

## 12 · Quirks · 已知陷阱與注意事項

### Framework 層

| Quirk | 怎麼處理 |
|---|---|
| 🔴 **repo 內沒有任何 `slides.yaml` 對得起目前的 24 頁 canonical deck**（`tpc-launch/`=26 頁、棄用的 `tpc-launch-deck/v2/`=27 頁，皆缺 trailer/redeem） | **改正式 deck 直接編根目錄 `index.html`**；`build.py` 產物絕不可覆蓋它（見 §0.5、§1.5） |
| 根目錄 `index.html` 與 `tpc-launch-en/index.html` 目前是**手動維護**，不是 build 產物 | 小改可直接編輯這兩份；大改建議先把 slides.yaml 校正回來再走 build 流程 |
| `tpc-launch/index.html` 是自動產出的 | **不要直接編輯**。改 `slides.yaml` 跑 build |
| `SilentUndefined` 不報錯 | 欄位名拼錯只會變空，找問題看產出 HTML |
| `base.html` 寫死 `<html lang="zh-Hant">` | 英文 deck 要在自己的 templates copy 改 `lang="en"` |
| `base.html` 寫死 rotate-prompt 中文 | 英文 deck 要在自己的 copy 改英文 |
| `cover-logo-{brand}` CSS 只定義 accucrazy/turncloud | 其他 brand 走 default 樣式（也 OK） |
| YAML 用 `items:` 會撞 jinja dict.items | **永遠用 `bullets:`** |
| `stg-cols-N` CSS 對 3/4/5 都 OK | 超過 5 可能 layout 跑掉 |
| 字體 `Noto Sans TC` 中英都用 | 英文版加 `Inter` 後排版更舒服 |

### 內容層

| Quirk | 怎麼處理 |
|---|---|
| 公司名是 **Accucrazy**，不是「肖準」 | 早期 deck 有錯，已修，新內容禁用 |
| 「Cookie 死了」這個論述 Ian 反對 | 改用「People crave real content」 |
| Ian 沒提過的數字不要自己加 | ROAS 3-5x、CTR +15-30% 這類業界常識可以保留，但謹慎 |
| 「肖準 = 4500 萬 = 賺很多」這種誇耀 Ian 反對 | sharing/ deck 已調為謙遜版 |

### Git 層

| Quirk | 怎麼處理 |
|---|---|
| `turncloud-presentation` 是 git repo（accucrazy/turncloud-presentation），**且是唯一正式來源** | commit/push 前先 `git status` 看狀態 |
| 工作機上可能存在**其他含舊版 deck 的 repo / 資料夾**（如 `turncloudlaunch`、`tpc-launch-deck/v2`） | **不要從那些地方部署**，以本 repo 為準（見 §0） |
| `siam-paragon/` 不是 git repo（另一台機器） | local-only |
| NTFS junction 的 `img/` | git 不會 track，deploy 時要實際複製檔案 |
| 大影片 (>50MB) push 會 warn | <100MB 還是過得去，但要注意 |
| `.env` 含 `GEMINI_API_KEY`，已在 `.gitignore` | **不要 commit** |
| Git author identity 未設 | commit 用 `git -c user.name="Ian" -c user.email="ian@accucrazy.com" commit ...` |
| Windows PowerShell 不吃 heredoc | commit message 多行用 `-F file` 不要用 `<<EOF` |

### Deploy 層

| Quirk | 怎麼處理 |
|---|---|
| GitHub Pages | push 到 `main` 即自動部署（約 1–2 分鐘） |
| 自訂網域 `turncloud.thepocket.company` | GCP VM `reel-studio`（zone `asia-east1-b`，nginx，web root `/var/www/deck/`）— **不會自動同步**，push 後要手動上傳（見 §13 Recipe 9） |
| 兩個部署內容必須一致 | 更新任何 deck 後，兩邊都要更新並驗證（slide 數、圖片 0 broken、影片 HTTP 200） |
| `sharing/`、`tengyun-report/`、`tpc-launch-en/` 都是 repo 子目錄 | 改的時候記得 push，VM 端同步到對應子目錄 |
| `siam-paragon/` 未部署 | 純 local proposal |

---

## 13 · Recipes · 常見工作流

### Recipe 1 · 「加一個 chapter break」

```yaml
# 在 slides.yaml 的 slides: list 加
- id: my_chapter
  template: chapter
  tone: orange
  eyebrow: "CHAPTER 03 · 新章節"
  title: '一個<span class="o">新</span>主題'
  lede: '這段論述...'
  bullets:
    - { tone: cyan,   label: "01", text: '第一點' }
    - { tone: orange, label: "02", text: '第二點' }
    - { tone: violet, label: "03", text: '第三點' }
  tagline: '收尾'
  meta_left: "Footer 文字"
```

`python build.py` → 完成。

### Recipe 2 · 「在某 slide 嵌個 demo 影片」

```yaml
- id: my_demo
  template: demo
  variant: cinema
  tone: violet
  backdrop: img/anim_backdrop.jpg
  media: img/pandora_demo.mov         # 直接用既有素材
  media_fit: contain
  marker: "● LIVE DEMO"
  tag: { color: violet, text: "PANDORA · LIVE" }
  title: '看 <span class="c">Pandora</span> 跑'
  subtitle: '...'
  meta_left: "Pandora demo"
```

### Recipe 3 · 「改某 slide 的標題」

直接編輯 `slides.yaml` 中對應 slide 的 `title:` 欄位。`python build.py`。**不要動 `index.html`**。

### Recipe 4 · 「翻譯整份 deck 成英文（或別的語言）」

1. 複製整個 deck 到新資料夾（見 §7）
2. 改 `templates/base.html`：`lang` + rotate-prompt
3. 把 `slides.yaml` 整份翻譯（保留 HTML tags、`<span class="c">`、`<strong>` 等）
4. `python build.py`

### Recipe 5 · 「換掉某張 hero image 成英文版」

1. 寫一支 `generate_<thing>_en.py`（參考 §8 模板 + `siam-paragon/generate_capi_flow_en.py`）
2. 把中文原圖當 reference 傳入
3. `python generate_<thing>_en.py`
4. 改 `slides.yaml` 對應 slide 的 `media:` 路徑指向新圖
5. `python build.py`

### Recipe 6 · 「重新生成有問題的 hero image」

直接重跑該 generate script：`python generate_harness_diagram_v4.py`
每次跑 Gemini 結果略有不同。不滿意就再跑一次（或微調 prompt 後再跑）。

### Recipe 7 · 「插入一個 5-step flow」

```yaml
- id: my_flow
  template: stage
  tone: cyan
  arrows: true                        # 步驟之間畫箭頭
  tag: { color: cyan, text: "FLOW" }
  title: 'Five steps'
  panels:
    - { tone: cyan,   label: "01", name: 'Step 1', body: '...' }
    - { tone: orange, label: "02", name: 'Step 2', body: '...' }
    - { tone: violet, label: "03", name: 'Step 3', body: '...' }
    - { tone: green,  label: "04", name: 'Step 4', body: '...' }
    - { tone: cyan,   label: "05", name: 'Step 5', body: '...' }
  meta_left: "Footer"
```

### Recipe 8 · 「commit + push 到 GitHub」

```powershell
cd turncloud-presentation

# 看狀態
git status

# 確認沒有要 commit `.env` / 大檔
git add slides.yaml index.html img/new_thing.jpg

# 用 -F file 寫 commit message（PowerShell 不吃 heredoc）
@"
feat(deck): your one-line summary

- bullet 1
- bullet 2
"@ | Out-File -Encoding utf8 .commit-msg.tmp

git -c user.name="Ian" -c user.email="ian@accucrazy.com" commit -F .commit-msg.tmp
Remove-Item .commit-msg.tmp
git push origin main
```

### Recipe 9 · 「同步到 VM（turncloud.thepocket.company）」

push 到 GitHub 後，網域那份**不會自動更新**，要手動同步：

```powershell
# 1. 上傳改過的檔案（範例：根目錄 index.html + 新圖）
gcloud compute scp index.html reel-studio:/tmp/index.html --zone=asia-east1-b --project=the-pocket-banana-f8811
gcloud compute scp img/new_thing.jpg reel-studio:/tmp/new_thing.jpg --zone=asia-east1-b --project=the-pocket-banana-f8811

# 2. SSH 進去裝到 web root（root deck 在 /var/www/deck/，en 版在 /var/www/deck/en/，tengyun 在 /var/www/deck/tengyun-report/）
gcloud compute ssh reel-studio --zone=asia-east1-b --project=the-pocket-banana-f8811 --command="sudo cp /tmp/index.html /var/www/deck/index.html && sudo cp /tmp/new_thing.jpg /var/www/deck/img/ && sudo chown -R www-data:www-data /var/www/deck"

# 3. 驗證（cache-bust + 檢查資產）
# 開 https://turncloud.thepocket.company/?v=<隨機字串> · 確認 slide 數、圖片、影片都正常
```

> 驗證標準：slide 數正確、`img/` 圖片 0 broken、影片 HTTP 200。md5 比對 local vs VM 最保險。

---

## 14 · 衍生 deck · `ai-talk-deck`（AI 演講合併版）

> **這是一份合併型 deck，就放在本 repo 的 `ai-talk-deck/` 子資料夾**（與正式 deck 同 repo、各自獨立）。
> 用途：一場「AI 演講 + 騰雲集團介紹 + The Pocket Company 介紹」三合一的對外簡報。
> 線上位置：**`https://turncloud.thepocket.company/ai-talk/`**（GCP VM `reel-studio` 的 `/var/www/deck/ai-talk/`，手動同步，做法同 [Recipe 9](#recipe-9-同步到-vmturncloudthepocketcompany)）。

### 結構（`ai-talk-deck/index.html` 是唯一進入點）

它是一個**純前端播放器**：所有頁面在 `index.html` 的 `SLIDES` 陣列中組裝，分三段、目前共 **44 頁**：

| 段 | 來源陣列 | 型別 | 內容 |
| --- | --- | --- | --- |
| AI 演講 | `TALK`（19 張） | `image` → `img/talk/*.png` | 原始演講 PPT 的精選頁（雨傘 → 滑鼠 → Transformer → 訓練/湧現 → 口碑成效 → 商業模式 → 市場/漏斗）。完整 56 頁清單留在 `TALK_FULL` 註解裡，要加回某張就把名字複製上來。 |
| 騰雲集團介紹（2 頁） | `TC`（2 張） | `image` → `img/tc/*.png` | 都用原始 PPTX 截圖：`s2` =「6870 亮點」總覽、`s4` =「**國際市場開拓**」海外版圖（亞洲 HUB 地圖 + 海外營收 35%→41%）。其他頁截圖在 `img/tc/s1..s17.png`，換頁只要改 `TC` 陣列。舊的 10 頁 HTML 版仍留在 `slides/tc-*.html`（曾短暫用 `tc-02` 當亮點頁，現已回到 `s2` 截圖）。 |
| The Pocket Company | `pocket-intro` + `POCKET`（22 張） | `html` / `pocket` | `slides/pocket-intro.html` 是章節過場（背景圖 `img/pocket_chapter_bg.jpg` 由 `generate_pocket_bg.py` 用 Banana/Gemini 生成）；其餘是從正式 deck 拆出來的單頁，放在 `pocket/p*.html`。 |

**Pocket 段的資產解析**：`pocket/p*.html` 以 `srcdoc` 載入，並在 `<head>` 注入 `<base href="https://turncloud.thepocket.company/">`，因此它們內部的 `img/*.mov` 等資產**直接吃線上正式 deck 的素材**，不需重複上傳。改 `POCKET_BASE` 常數即可切換來源。

### 🔊 媒體播放規則（聲音/影片只在「當前頁」）

> **背景**：每張 `pocket/p*.html` 內嵌一段 `// single-slide embed: force active + best-effort autoplay`，會在 iframe 一載入就 `play()`。因為 `index.html` 會**預載前後鄰頁**，若不控管，影片（尤其 RYTHO 的饒舌 `rytho_demo.mp4`，帶 `controls`、不 muted）會**還沒翻到就先出聲，而且翻過去後不會停**。

`index.html` 的 `syncMedia()` 由父層統一控管（在 `show()` 切頁時、以及每個 iframe `load` 後各呼叫一次）：

- **非當前頁**：所有 `<video>/<audio>` 一律 `pause()` 並 `currentTime=0`（歸零，下次從頭）。
- **當前頁**：只有「**靜音背景循環**」(`muted` 且無 `controls`，如 `culture_listening` / `pandora_demo`) 會自動續播；
  **含聲音的 demo**（有 `controls`，如 **RYTHO 饒舌**、Reels Studio / Motion Lab）到站時保持暫停，**交給簡報者點擊 play**（投影片上有「♪ 點影片開聲」提示）。

> 結果：RAP 音樂只會在 RYTHO 那頁、且由簡報者主動播放；任何頁離開後聲音立即停止。改 deck 時若新增帶聲影片，沿用「有 `controls` = 手動、`muted` 無 `controls` = 自動循環」這個約定即可，不必再改 `syncMedia()`。

### 部署（同 Recipe 9，但目標是子目錄）

```bash
# 1. 打包（排除 dev 腳本與暫存檔）
tar -czf ../ai-talk-deck.tar.gz --exclude="*.py" --exclude="_*" --exclude="*.pptx" .
# 2. 上傳 + 解壓到子目錄
gcloud compute scp ../ai-talk-deck.tar.gz reel-studio:/tmp/ --zone=asia-east1-b --project=the-pocket-banana-f8811
gcloud compute ssh reel-studio --zone=asia-east1-b --project=the-pocket-banana-f8811 \
  --command="sudo rm -rf /var/www/deck/ai-talk && sudo mkdir -p /var/www/deck/ai-talk && sudo tar xzf /tmp/ai-talk-deck.tar.gz -C /var/www/deck/ai-talk && sudo chown -R www-data:www-data /var/www/deck/ai-talk"
# 3. 驗證 https://turncloud.thepocket.company/ai-talk/?v=<隨機>  → 44 頁、資產 200、聲音只在 RYTHO
```

> 只改 `index.html`（例如調整 `TALK`/`TC` 陣列或 `syncMedia()`）時，可只 scp 單檔到 `/tmp/` 再 `sudo cp` 進 `/var/www/deck/ai-talk/index.html`，不必整包重傳。

---

## 15 · 衍生 deck · `rtx-talk-deck`（RTX 演講版）

> **與 `ai-talk-deck` 同款外殼**（同一個播放器引擎 + `syncMedia()` 規則），放在本 repo 的 `rtx-talk-deck/` 子資料夾。
> 用途：RTX / NVIDIA 場合的演講 ——「NemoClaw × Nemotron + 騰雲發表會精選 + 地端多模態工作流」，
> 結論收在「**把雲端服務落到地端 = 商機**」。
> 線上位置：**`https://turncloud.thepocket.company/rtx-talk/`**（VM `/var/www/deck/rtx-talk/`，手動同步，同 Recipe 9）。

### 結構（`rtx-talk-deck/index.html` 是唯一進入點，共 44 頁 = 33 + 6 + 5）

| 段 | 來源陣列 | 型別 | 內容 |
| --- | --- | --- | --- |
| NemoClaw × Nemotron | `NEMO`（33 張） | `image` → `img/nemo/p01..p33.png` | `Nemoclaw (1).pdf`（源檔在使用者 Downloads，完整版；先前為 14 頁精簡版）整份 200dpi 截圖：cover → Accucrazy 歷程 → 客戶牆 → TPC agents → Pandora / Culture Listening → fine-tune 論述 → NemoClaw harness → CRM / Stacy / Paul agents → MCP tools。換頁：把新 PDF 丟進 `_convert_nemo1.py` 重轉，覆蓋 `img/nemo/` 並改 `NEMO` 陣列長度。 |
| 騰雲發表會精選 | `POCKET`（6 張） | `pocket` | 從 `ai-talk-deck/pocket/` 複製的拆頁：`p02_overview / p03_aios_concept / p06_pandora / p11_banana / p13_banana_video_edit / p18_ecosystem_chapter`。同樣以 `srcdoc` + `<base href=POCKET_BASE>` 吃線上正式 deck 素材。增減頁：從 `ai-talk-deck/pocket/` 再複製對應檔案進來並改 `POCKET` 陣列。 |
| 地端多模態工作流 | `LOCAL`（5 張） | `html` → `slides/local-*.html` | 全新手刻（深色 + NVIDIA 綠，共用 `slides/local.css`）：`local-intro`（章節過場）→ `local-pipeline`（4 步工作流圖）→ `local-demo-a`（商品照→實穿，用 NEARBY 素材 `img/local/`）→ `local-demo-b`（實穿→影片，**影片版位佔位**）→ `local-conclusion`（雲端 vs 地端對照 + 商機結論）。※ 原 `local-demo-c`（狗血故事）已依需求移除。 |

**Demo B 素材佔位約定**：素材就緒後放進 `img/local/` —— Demo B 影片命名 `tryon_video.mp4`，再把該頁 `.slot` 區塊換成 `<video>`（HTML 內有註解示範）。帶聲 demo 記得加 `controls`（= 簡報者手動播），靜音循環用 `muted loop` 無 `controls`（= 自動播）。

### 部署（同 ai-talk-deck，目標子目錄 `/var/www/deck/rtx-talk/`）

```bash
cd rtx-talk-deck && tar -czf ../../rtx-talk.tar.gz .
gcloud compute scp rtx-talk.tar.gz reel-studio:/tmp/ --zone=asia-east1-b --project=the-pocket-banana-f8811
gcloud compute ssh reel-studio --zone=asia-east1-b --project=the-pocket-banana-f8811 \
  --command="sudo rm -rf /var/www/deck/rtx-talk && sudo mkdir -p /var/www/deck/rtx-talk && sudo tar xzf /tmp/rtx-talk.tar.gz -C /var/www/deck/rtx-talk && sudo chown -R www-data:www-data /var/www/deck/rtx-talk"
# 驗證 https://turncloud.thepocket.company/rtx-talk/?v=<隨機> → 44 頁、nemo 圖 200、pocket 段影片可播
```

---

## 附錄 · 給 LLM Agent 的 onboarding cheat sheet

如果你是剛被叫進來的新 agent，**讀完這份就可以動工**。五件最重要的事：

0. **版本規矩最大**（§0）
   → 這個 repo 是唯一正式來源；正式 deck = 根目錄 `index.html`（基準 `8aba57a`）
   → `tpc-launch/slides.yaml` 是舊版，rebuild 前要先校正，**不要拿 build 產物蓋掉正式 deck**
   → 改完要同步兩個部署（GitHub Pages 自動 + VM 手動，見 Recipe 9）


1. **環境**：跑 `build.py` 只需 PyYAML + Jinja2；跑 `generate_*.py` 還要 `requests` + `python-dotenv` + 一支 `GEMINI_API_KEY`（放在 deck 目錄的 `.env`）。詳見 §8.0。

2. **編輯 `slides.yaml`，不要編輯 `index.html`**
   → `python build.py` 重 build

3. **詞彙與敘事原則嚴格遵守**（§2 §3）
   → 不是「肖準」，是 **Accucrazy**
   → 不是「Cookie 死了」，是 **「Real Content Wins」**
   → 不要自己生 Ian 沒提過的數字

4. **重用既有素材，不要重新生成**
   → 影片在 `turncloud-presentation/tpc-launch/img/`
   → 5 個 Agent 肖像永遠用 `08_pandora.jpg` ~ `12_stacey.jpg`
   → 要生新圖時，**寫一支 `generate_*.py`** 並用前一版作 reference

剩下的所有細節都在這份檔。Good luck.

---

*Last updated · 2026-07-21 · §15 `rtx-talk-deck` 融合更新為 44 頁（NemoClaw × Nemotron 完整 33 頁 + 騰雲發表會精選 6 頁 + 地端多模態工作流手刻 5 頁，狗血故事 Demo C 已移除）· `/rtx-talk/` 已重部署 · Demo B 素材佔位約定）。先前：§14 `ai-talk-deck`（44 頁 · 媒體只在當前頁播放規則 · `/ai-talk/` 部署）· §1.5 最新版投影片進度（24 頁逐頁清單）· This document is the Harness for the slide framework.*
