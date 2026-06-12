# TurnCloud × The Pocket Company — Launch Presentation

這個 repo 是 **The Pocket Company（Accucrazy 肖準）加入騰雲 TurnCloud** 發表會的線上簡報與相關案例資料的 **唯一正式來源（canonical source）**。

> 規矩一句話：**GitHub 上的這份 repo 就是正確版本。** 任何地方（網域、VM、其他 repo）如果跟這裡不一致，以這裡為準，並把那邊同步回來。

---

## 1. 線上位置（兩個部署，內容必須一致）

| 位置 | URL | 由誰提供 |
|---|---|---|
| 自訂網域 | https://turncloud.thepocket.company/ | GCP VM（nginx，`/var/www/deck/`） |
| GitHub Pages | https://accucrazy.github.io/turncloud-presentation/ | 本 repo（`main` 分支） |

**兩邊內容必須一致**，且都等於本 repo `main` 的最新狀態。更新流程見第 4 節。

---

## 2. 正確版本（很重要）

- **主視覺發表會 deck = repo 根目錄的 `index.html`**（標題：`Enterprise AIOS — 我們想要一起長大的生態系`）。
- 這份 deck 的「正確基準」是 commit **`8aba57a`**（`Add 'one more thing' redeem slide with QR…`）── 含 **trailer 片頭**、**redeem / QR 兌換頁**、以及 Raccoon / Rytho / Luna / CUHK GFMC 生態系內容。
- 過去曾有一份 **不同 repo（`turncloudlaunch` / `tpc-launch-deck/v2`）的舊分支** 被誤部署到網域上（缺 trailer + redeem）。**那份不是正確版本**，已被本 repo 的版本取代。

---

## 3. 目錄結構

| 路徑 | 內容 |
|---|---|
| `index.html` | ⭐ 主發表會 deck（正確版本，自動產生 — 勿直接手改，見第 4 節） |
| `BRIEFING.md` | ⭐ 規矩 / 戰情手冊 ── 內容定位、敘事結構、講稿、商業模式、競品、CTA。建 deck 前先讀這份。 |
| `tpc-launch/` | deck 的建置專案：`slides.yaml`、`templates/`、`build.py`、`generate_*.py`。`tpc-launch/index.html` 已對齊根目錄正確版（資產以 `../img/` 指回根目錄）。 |
| `tpc-launch-en/` | 英文版發表會 deck（English version，內容同步自正確版）。 |
| `tengyun-report/` | 騰雲發表會 × Computex 口碑成效戰報（破百萬次觀看、含 Pandora 聲量轉位頁）。 |
| `img/` | 主 deck 用到的所有圖片與影片資產。 |
| `aios.html` · `slides/` · `sharing/` · `babycam-dtc/` · `assets/` | 其他相關簡報 / 分享頁 / 素材。 |

---

## 4. 怎麼改、怎麼建（建置規矩）

主 deck（`index.html`）是 **自動產生** 的，**請勿直接手改**。

```bash
cd tpc-launch
# 1) 改內容 → 編輯 slides.yaml
# 2) 改版型 → 編輯 templates/
# 3) 重新產圖（需要時）→ python generate_*.py
# 4) 重建 HTML
python build.py
```

> ⚠️ 已知結構待辦：`tpc-launch/` 內的 `slides.yaml` 仍是較舊的版本，與目前根目錄正確 deck 尚未完全對齊。若要用 `build.py` 重建根目錄 deck，需先把建置來源（`slides.yaml` / `templates/`）校正到正確版本，否則會覆蓋出舊內容。

---

## 5. 部署（讓網域 + GitHub Pages 一致）

改完、commit 並 push 到 `main` 後：

1. **GitHub Pages** 會自動由 `main` 重新發佈（約 1–2 分鐘）。
2. **GCP VM（網域）** 需手動同步：把 `index.html` 與用到的 `img/` 資產上傳到 `reel-studio:/var/www/deck/`（root deck），`tengyun-report/`、`tpc-launch-en/` 同理放到對應子目錄。

部署後務必驗證：slide 數正確、`img/` 圖片 0 broken、影片可載入（HTTP 200）。

---

## 6. 一句話總結

> **Runtime 讓 AI 運行空間，AI OS 讓企業管理 AI，AI Agents 真正開始為企業工作。**
> 詳細敘事與所有數字、講稿，see **[`BRIEFING.md`](./BRIEFING.md)**。
