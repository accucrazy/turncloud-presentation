# MEET TAIPEI 2026 — The Pocket Company · 內容飛輪六週之後

根目錄正式 deck（介紹 The Pocket Company 的 22 頁）原封不動，只把「內容飛輪」那段（原第 10–14 頁）換成六週後的實證版，共 25 頁。線上：https://accucrazy.github.io/turncloud-presentation/meet-taipei/

- `index.html` ─ 正式 deck（產出物，請勿手改；版型沿用根目錄正式 deck 的 CSS/JS）
- `src/deck-body.html` ─ 25 頁的內容，改字改這裡；`{B}` 會換成根目錄 `img/` 的 GitHub Pages 絕對網址；頁碼由 build 自動重排
- `src/mt.css` ─ 這份 deck 新增的版型（`mt-` 前綴）
- `src/build.py` ─ `python src/build.py` 重建 `index.html`（讀根目錄 `index.html` 的 `<style>` 與 `<script>`）
- `img/` ─ 新素材：案例短片 `case-taitie.mp4`（台鐵霸位伯，3.2 MB）、地端 Genjutsu 並排影片 `genjutsu-sbs.mp4`（8 MB）與封面圖

飛輪段落（第 10–15 頁）：選題表（Pandora 11/10–11/12 三天榜，第 9 名台鐵事件為選中的題）→ 熱點案例「台鐵霸位伯」（11/12 選題、11/13 上架、頻道第一）→ 24 小時排程 → 38 天三平台成績單 → 長尾心得 → 飛輪圖。第 4 頁：NVIDIA 生態系夥伴牆（正式 deck 停放在 `<template>` 的那頁，放回來）。第 23 頁：地端 Genjutsu（左原片、右 Ian + 台北捷運並排，原片聲音，`img/genjutsu-sbs.mp4`；數字來自 `media-mcp/outputs/ian-genjutsu/index.html` 第 13 版與 Higgsfield 對照表）。
數據來源（2026-11-18 21:50 抓）：YouTube Data API（`upload_youtube.build_service()`）、Meta Graph API（`social_upload.Client("instagram"|"threads")` 的 `/{media}/insights`）、Pandora `/api/public/trends`、`media-mcp/research/slap-shorts/<label>/story.json`（趨勢證據）與 `trend-uses.json`。翻頁：方向鍵；深連結 `#s12` 直接到第 12 頁。
