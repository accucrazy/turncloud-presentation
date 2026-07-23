# tpc-siam-partnership — Content Tech × Bureau of Wonders 合作提案（英文 · 33 頁）

> 對象：**Bureau of Wonders（BOW，tbowonders.com）**——曼谷精品 PR / 體驗 agency（客戶：Chaumet、Loro Piana、LV、CASIO、AIA…）。
> 定位：**Content Tech partnership proposal**——開場用「我們早就在監聽你的世界」（Pandora 2.18M 對話）當證據，收在共建泰國 Content Tech + 90-day pilot。
> 線上：**https://turncloud.thepocket.company/siam-partnership/**（VM `/var/www/deck/siam-partnership/`）。
> 基底：複製自 `tpc-launch-en` 改造；共用素材吃線上根網域 `/img/`，本 deck 專屬素材在 `img/`。
> 文案原則：對方英文非母語 → **字少、字大**，一行一句。

## 頁面結構（33 頁 · 頁碼 02..33，封面無頁碼）

| # | data-slide | 內容 |
|---|---|---|
| 01 | (cover) | Content Tech — Turning great places into compounding stories · Banana 生成曼谷版團隊圖 `img/cover_hero_bangkok.jpg` |
| 02 | intro_bio | Ian Wu 英文 bio（左 bullets＋pills、右 Google Cloud 演講照）· CSS `sp-bio` |
| 03 | intro_nvidia | NVIDIA 照片牆 ×4（GTC keynote 牆 / Inception 攤位 / meetup / 立牌照）· `sp-photowall`，GTC 圖 `object-fit:contain` 保 logo |
| 04 | intro_about | 全英文時間軸 fullbleed `intro_about.jpg`（Banana 英譯） |
| 05 | intro_brands | 品牌牆（英文標題＋裁切版 logo 牆）· `sp-brandwall` |
| 06 | intro_thailand | Accucrazy Thailand 2019：Oriental Princess AI 膚檢 + Meitu×Lazada + **泰國商務處 AI 影片 `th_tteo.mp4`**（自動播）· `sp-thwall` |
| 07–13 | （產品段） | AI OS 概念 → Agent 團隊 → Pandora 兩頁（沿用 tpc-launch-en） |
| 14 | siam_proof | Pandora 已在監聽實證：4 統計卡 + 5 列關鍵字排行（芒果糯米 1.06M 置頂） |
| 15 | siam_reports | 真實報告牆 ×3 微傾斜截圖 + "Not slides. Real reports." |
| 16 | siam_insight | **4 張圖文洞察卡**：左＝真實貼文截圖（可點，連回原始 IG reel）、右＝數據→洞察→`→ 建議行動` |
| 17 | siam_foodie | **SiamFoodie live demo**：左＝手機直式錄屏 `img/siamfoodie_demo.mp4`（8.9s muted loop 自動播，選語言→逛 37 家餐廳→開 STARBUCKS 詳情）、右＝4 卡（5 語言 / AI concierge / booking→delivery / built in days）· `sp-foodie` |
| 18–27 | （產品段） | Moana / Banana / Reels Studio / Adriana / Stacey（沿用） |
| 28–29 | ecosystem | 生態系 chapter + Rytho demo（raccoon / luna 深入頁已刪，finale 小卡保留） |
| 30 | siam_cobuild | 共建泰國 Content Tech：左卡 WE BRING THE TECHNOLOGY（agents ring 插圖）× 右卡 YOU BRING THE CULTURE（BOW 遊船晚宴照 `bow_event.jpg`）· `sp-cobuild` |
| 31 | siam_framework | Content Tech flywheel（4 相位卡含 agent 頭像）＋三條合作軌＋90-day pilot 收尾條 · `sp-flywheel` |
| 32 | finale | 生態系收斂（ecosystem grow-up） |
| 33 | redeem | 100 Banana Split credits · FOR THE BOW TEAM |

## 第 16 頁四張貼文的原始連結

| 卡片 | Instagram reel |
|---|---|
| 冰箱磁鐵 83,075 讚（ICONSIAM） | https://www.instagram.com/reel/DWTqCE3CfIB/ |
| 芒果糯米吃播 20K 讚 | https://www.instagram.com/reel/DWi1UDFCe4u/ |
| SÚNDALO 香水（Siam Center） | https://www.instagram.com/reel/DWOodmQEvHC/ |
| NEXTOPIA 永續 reel | https://www.instagram.com/reel/DTKWQgxicV-/ |

貼文截圖是 `instagram.com/reel/<code>/embed/captioned/` 頁以 560 寬 viewport（dsf=1）截的；連結從 Pandora report-view 文章列表挖出。

## 第 17 頁 SiamFoodie demo 影片的製作方式

- 來源 app：`https://siamfoodie--siamfoodie-1ce1a.asia-east1.hosted.app/`（Siam Paragon AI 美食 concierge demo）。
- 錄製：parent repo 根的 `_record_siamfoodie.py`——Playwright headless Chromium，480×1040 手機直式 viewport，`record_video_dir` 錄 webm。腳本：語言頁 → English → 平滑捲餐廳牆 → Cafe & Dessert 篩選 → 開餐廳詳情卡捲菜單。
- 轉檔：`_convert_sf.py`——**Playwright 內建 ffmpeg 沒有 mp4 muxer / libx264 preset**，要用 `imageio-ffmpeg` 的完整 ffmpeg；掐頭 4.8s（載入等待），輸出 8.88s H.264。
- 注意：app 的 AI 對話後端會回 network error，demo 腳本刻意**不送出訊息**。

## Pandora 監聽數據源（12 組關鍵字報告）

芒果糯米 1,055,093 / ICONSIAM 577,136 / Siam Paragon 248,466 / Siam Center 193,370 / NEXTOPIA 39,641 / MELAND 28,618 / Siam Takashimaya 17,180 / SookSiam 8,921 / Siam Discovery 5,569 / SEA LIFE 4,341 …報告連結在 `pandora.thepocket.company/report-view/*`（詳 SLIDE_FRAMEWORK.md §16）。

## 專屬 CSS

全部集中在 `</style>` 前的 `sp-*` 區塊：`sp-statgrid / sp-rows / sp-insightgrid / sp-wall / sp-flywheel / sp-bio / sp-photowall / sp-thwall / sp-brandwall / sp-cobuild / sp-foodie`。

## 維護

- 頁碼重編：parent repo 根的 `_renumber_pg.py "turncloud-presentation\tpc-siam-partnership\index.html"`（自動算 total＝pg span 數＋1）。
- 部署：

```bash
cd tpc-siam-partnership && tar -czf ../../siam-partnership.tar.gz .
gcloud compute scp siam-partnership.tar.gz reel-studio:/tmp/ --zone=asia-east1-b --project=the-pocket-banana-f8811
gcloud compute ssh reel-studio --zone=asia-east1-b --project=the-pocket-banana-f8811 \
  --command="sudo rm -rf /var/www/deck/siam-partnership && sudo mkdir -p /var/www/deck/siam-partnership && sudo tar xzf /tmp/siam-partnership.tar.gz -C /var/www/deck/siam-partnership && sudo chown -R www-data:www-data /var/www/deck/siam-partnership"
```

- 驗證：`https://turncloud.thepocket.company/siam-partnership/?v=<隨機>` → 33 頁、`../img/` 素材全 200、第 16 頁貼文可點開、第 17 頁影片自動播。

*Last updated · 2026-07-23*
