# ☁️ 台灣氣象資料網站

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

一個功能完整、介面美觀的台灣天氣資訊互動式網站，提供即時天氣、精準預報，一目了然。

## 🌐 Demo Site

**線上展示網站**: [https://aiot-weather-vesae2s9zpz6zpe2vcgqsa.streamlit.app/](https://aiot-weather-vesae2s9zpz6zpe2vcgqsa.streamlit.app/)

立即體驗完整功能，無需安裝！

---

![Taiwan Weather Dashboard](assets/images/screenshot.png)

## ✨ 專案特色

- 🌡️ **即時天氣資訊** - 22 個縣市即時天氣狀況
- 📊 **三時段預報** - 今日白天、今晚明晨、明日白天詳細預報
- 🗺️ **全台天氣地圖** - 互動式地圖，點擊查看各縣市詳情
- 💨 **空氣品質監測** - 88 個空品測站即時 AQI 數據
- 📅 **一週天氣預報** - 溫度趨勢與降雨機率圖表
- ⚠️ **天氣警報** - 即時顯示特殊天氣警報與影響範圍
- 📱 **響應式設計** - 支援桌機、平板、手機瀏覽
- 🎨 **清爽介面** - CWA 風格淡藍色設計，使用體驗優異

## 🖼️ 功能展示

### 主頁面
三欄式佈局設計：
- **左欄**：目前狀態 + 本週預報
- **中欄**：主溫度顯示 + 分時段預報
- **右欄**：空氣品質 + 天氣警報

### 進階功能
- **🗺️ 全台地圖** - 查看所有縣市天氣分布
- **📊 縣市總覽** - 表格式或卡片式檢視全台天氣
- **📈 完整預報** - 7 天溫度與降雨趨勢圖表
- **💨 空品詳情** - 88 個測站詳細 AQI 資訊

## 🚀 快速開始

### 環境需求

- Python 3.10 或以上版本
- pip 套件管理工具
- Git 版本控制

### 安裝步驟

#### 1. 克隆專案

```bash
git clone https://github.com/Charles8745/AIOT-weather.git
cd AIOT-weather
```

#### 2. 建立虛擬環境

```bash
# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

#### 3. 安裝依賴套件

```bash
pip install -r requirements.txt
```

#### 4. 設定 API 金鑰

1. 複製環境變數範本：
   ```bash
   cp .env.example .env
   ```

2. 編輯 `.env` 檔案，填入您的 API 金鑰：
   ```env
   CWA_API_KEY=your_cwa_api_key_here
   MOENV_API_KEY=your_moenv_api_key_here
   ```

3. 取得 API 金鑰：
   - **中央氣象署**: https://opendata.cwa.gov.tw/
   - **環保署**: https://data.moenv.gov.tw/

#### 5. 執行應用程式

```bash
streamlit run app.py
```

應用程式將在 `http://localhost:8501` 啟動 🎉

## 📁 專案結構

```
AIOT-weather/
│
├── app.py                      # 主程式入口
├── requirements.txt            # 套件依賴清單
├── .env.example               # 環境變數範例
├── .gitignore                 # Git 忽略檔案
├── README.md                  # 專案說明文件（本檔案）
├── DEPLOYMENT.md              # 部署指南
├── TEST_REPORT.md             # 測試報告
├── 程式計劃書.md              # 開發計劃書
│
├── .streamlit/
│   └── config.toml            # Streamlit 設定檔
│
├── config/
│   └── config.py              # 應用程式設定
│
├── modules/
│   ├── api_client.py          # API 連線模組
│   ├── data_processor.py      # 資料處理模組
│   ├── cache_manager.py       # 快取管理模組
│   └── rate_limiter.py        # 速率限制模組
│
├── components/
│   ├── weather_card.py        # 天氣卡片元件
│   ├── forecast_chart.py      # 預報圖表元件
│   ├── map_view.py            # 地圖顯示元件
│   ├── air_quality.py         # 空氣品質元件
│   ├── weather_overview.py    # 縣市總覽元件
│   └── weather_warnings.py    # 天氣警報元件
│
├── utils/
│   ├── constants.py           # 常數定義
│   ├── helpers.py             # 輔助函數
│   └── ui_helpers.py          # UI 輔助函數
│
└── assets/
    ├── images/                # 圖片資源
    └── styles/                # 自訂 CSS 樣式
        └── cwa_style.css      # CWA 風格樣式
```

## 🎯 功能清單

### ✅ 已完成功能

#### 核心功能
- [x] 22 個縣市即時天氣資料
- [x] 三時段預報（今日白天、今晚明晨、明日白天）
- [x] 溫度、降雨機率、天氣描述、舒適度顯示
- [x] 天氣圖示整合（☀️ 🌤️ ⛅ ☁️ 🌧️ ⛈️）

#### 進階功能
- [x] 全台天氣地圖（Folium 互動式地圖）
- [x] 縣市總覽（卡片式/表格式切換）
- [x] 一週天氣預報（7 天溫度與降雨趨勢圖表）
- [x] 空氣品質監測（88 個測站 AQI 資料）
- [x] 天氣警報系統（即時特報顯示）

#### 效能優化
- [x] 資料快取機制（30分鐘～1小時 TTL）
- [x] API 請求速率限制（60 requests/minute）
- [x] 錯誤處理與友善提示
- [x] 效能監控工具
- [x] 快取命中率追蹤

#### UI/UX
- [x] CWA 風格淡藍色設計
- [x] 響應式三欄佈局
- [x] 一頁式設計，按鈕切換功能
- [x] 載入動畫與狀態提示
- [x] 自訂 CSS 樣式

## 🔧 技術架構

### 核心技術

| 技術 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 主要開發語言 |
| Streamlit | 1.28.0+ | Web 應用框架 |
| Plotly | 5.17.0+ | 互動式圖表 |
| Folium | 0.15.0+ | 地圖視覺化 |
| Pandas | 2.0.0+ | 資料處理 |
| Requests | 2.31.0+ | API 請求 |
| psutil | 5.9.0+ | 效能監控 |

### API 整合

**中央氣象署開放資料平台**
- 一般天氣預報 (F-C0032-001)
- 鄉鎮天氣預報 (F-D0047-091)
- 觀測資料 (O-A0001-001)
- 天氣警特報 (W-C0033-001)

**環保署開放資料平台**
- 空氣品質監測 (aqx_p_432)

### 架構設計

```
使用者介面 (Streamlit)
        ↓
   UI 元件層
        ↓
   資料處理層
        ↓
   快取管理層
        ↓
   API 客戶端層
        ↓
外部 API 服務
```

## 📊 效能指標

- **API 平均響應時間**: 0.355 秒
- **記憶體使用**: 每 10 個城市約 0.41 MB
- **快取命中率**: 已實作追蹤機制
- **並發請求限制**: 60 requests/minute
- **快取有效時間**:
  - 天氣預報: 30 分鐘
  - 週預報: 1 小時
  - 空氣品質: 10 分鐘
  - 天氣警報: 10 分鐘

## 🌐 部署到 Streamlit Cloud

詳細部署步驟請參考 [DEPLOYMENT.md](DEPLOYMENT.md)

### 快速部署

1. 推送程式碼到 GitHub
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. 前往 [Streamlit Cloud](https://share.streamlit.io/)

3. 設定環境變數（Secrets）
   ```toml
   CWA_API_KEY = "your_cwa_api_key"
   MOENV_API_KEY = "your_moenv_api_key"
   ```

4. 部署完成！

## 🧪 測試

### 執行測試

```bash
# 確認所有功能正常
streamlit run app.py

# 測試項目：
# ✅ 縣市選擇器
# ✅ 天氣資料載入
# ✅ 三時段預報顯示
# ✅ 全台地圖互動
# ✅ 縣市總覽搜尋
# ✅ 一週預報圖表
# ✅ 空氣品質資料
# ✅ 天氣警報顯示
```

### 測試報告

詳細測試結果請參考 [TEST_REPORT.md](TEST_REPORT.md)

- ✅ 所有核心功能測試通過 (7/7)
- ✅ API 連線正常
- ✅ 資料解析準確
- ✅ 介面顯示正確
- ✅ 快取機制運作良好

## 🔍 疑難排解

### API 金鑰問題

**問題**: 無法載入天氣資料

**解決方案**:
1. 確認 `.env` 檔案存在且 API 金鑰正確
2. 檢查 API 金鑰格式（無多餘空格）
3. 確認 API 金鑰有效且未過期
4. 檢查 API 請求次數限制

### 載入緩慢

**問題**: 資料載入時間過長

**解決方案**:
- 第二次載入會使用快取，速度會更快
- 檢查網路連線狀態
- 確認 API 服務運作正常
- 清除瀏覽器快取後重新載入

### 部署失敗

**問題**: Streamlit Cloud 部署失敗

**解決方案**:
1. 檢查 `requirements.txt` 是否包含所有依賴
2. 確認 Python 版本相容性（需 3.10+）
3. 查看 Streamlit Cloud 部署日誌
4. 確認環境變數設定正確

## 📝 更新日誌

### v1.0.0 (2025-12-03)
- ✅ 完成核心功能開發
- ✅ 整合 6 大 API
- ✅ 實作效能優化
- ✅ UI/UX 設計完成
- ✅ 準備部署上線

## 🤝 貢獻指南

歡迎貢獻！請遵循以下步驟：

1. Fork 本專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add: 新增某某功能'`)
4. 推送至分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

### 開發規範

- 遵循 PEP 8 程式碼風格
- 撰寫清楚的 commit message
- 新增功能請附上測試
- 更新相關文件

## 📄 授權

本專案採用 MIT License - 詳見 [LICENSE](LICENSE) 檔案

## 👨‍💻 作者

**Charles8745**
- GitHub: [@Charles8745](https://github.com/Charles8745)
- Repository: [AIOT-weather](https://github.com/Charles8745/AIOT-weather)

## 🙏 致謝

- **資料來源**: [中央氣象署開放資料平台](https://opendata.cwa.gov.tw/)
- **資料來源**: [環保署空氣品質監測網](https://data.moenv.gov.tw/)
- **開發框架**: [Streamlit](https://streamlit.io/)
- **視覺化工具**: [Plotly](https://plotly.com/) · [Folium](https://python-visualization.github.io/folium/)

## 📧 聯絡方式

如有任何問題或建議，歡迎透過以下方式聯繫：
- GitHub Issues: [提交問題](https://github.com/Charles8745/AIOT-weather/issues)
- Email: 透過 GitHub Profile

## 🌟 Star History

如果這個專案對您有幫助，請給予 ⭐ Star 支持！

---

**Made with ❤️ in Taiwan | 台灣製造**
