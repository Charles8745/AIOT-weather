# 🚀 Streamlit Cloud 部署步驟指南

## 📋 前置準備確認

✅ **已完成項目**：
- [x] 程式碼已推送到 GitHub (Charles8745/AIOT-weather)
- [x] README.md 已完成
- [x] DEPLOYMENT.md 已完成
- [x] requirements.txt 包含所有依賴
- [x] .streamlit/config.toml 已設定
- [x] .env.example 提供 API 金鑰範本
- [x] 所有功能測試通過

## 🌐 開始部署

### 步驟 1: 前往 Streamlit Cloud

1. 開啟瀏覽器，前往：**https://share.streamlit.io/**
2. 點擊右上角的 **"Sign in"** 或 **"Sign up"**
3. 選擇 **"Continue with GitHub"**
4. 授權 Streamlit 存取您的 GitHub 帳號

### 步驟 2: 建立新應用程式

1. 登入後，點擊 **"New app"** 按鈕
2. 在部署設定頁面填寫：

   ```
   Repository: Charles8745/AIOT-weather
   Branch: main
   Main file path: app.py
   ```

3. **App URL** (可選)：
   - 如果想自訂網址，可以設定為：`taiwan-weather-dashboard`
   - 最終網址會是：`https://taiwan-weather-dashboard.streamlit.app`

### 步驟 3: 設定環境變數（重要！）

1. 點擊 **"Advanced settings"**
2. 在 **"Secrets"** 區塊中，貼上以下內容：

   ```toml
   # 中央氣象署 API 金鑰
   CWA_API_KEY = "CWA-E2FC2F13-090B-4F3D-8055-521347898182"
   
   # 環保署 API 金鑰
   MOENV_API_KEY = "fc3438b1-5643-49c4-b2f6-5017887b72ad"
   ```

3. 確認格式正確（TOML 格式，使用雙引號）

### 步驟 4: 開始部署

1. 確認所有設定無誤
2. 點擊 **"Deploy!"** 按鈕
3. 等待部署程序（通常需要 2-5 分鐘）

### 步驟 5: 監控部署進度

部署過程中可以看到：
- ✅ Cloning repository...
- ✅ Installing Python...
- ✅ Installing requirements...
- ✅ Running app.py...
- 🎉 Your app is live!

## ✅ 部署完成後驗證

### 功能驗證清單

訪問您的應用程式網址，檢查以下功能：

#### 基本功能
- [ ] 應用程式成功載入
- [ ] 頁面標題顯示正確
- [ ] 縣市選擇器運作正常
- [ ] 可以切換不同縣市

#### 天氣資料
- [ ] 目前狀態卡片顯示（溫度、天氣）
- [ ] 本週預報顯示（5 天）
- [ ] 分時段預報顯示（今日、今晚、明日）
- [ ] 主溫度顯示區正確（大字體溫度）

#### 進階功能
- [ ] 🗺️ 全台地圖按鈕可開啟
- [ ] 📊 縣市總覽功能正常
- [ ] 📈 完整預報圖表顯示
- [ ] 💨 空品詳情正確載入
- [ ] ⚠️ 天氣警報顯示

#### 效能與穩定性
- [ ] 首次載入時間 < 10 秒
- [ ] 切換縣市反應迅速
- [ ] 無明顯錯誤訊息
- [ ] 快取機制運作（重複查詢更快）

## 🔧 常見問題排解

### 問題 1: ModuleNotFoundError

**錯誤訊息**: `ModuleNotFoundError: No module named 'xxx'`

**解決方法**:
1. 檢查 `requirements.txt` 是否包含該模組
2. 確認版本號正確
3. 重新部署應用程式

### 問題 2: API 金鑰錯誤

**錯誤訊息**: API 請求失敗或無資料

**解決方法**:
1. 在 Streamlit Cloud 點擊應用程式設定 (⋮ 選單)
2. 選擇 "Settings" → "Secrets"
3. 檢查 API 金鑰格式和內容
4. 確認使用 TOML 格式且有雙引號
5. 儲存後點擊 "Reboot app"

### 問題 3: 部署失敗

**錯誤訊息**: Build failed

**解決方法**:
1. 查看詳細的錯誤日誌
2. 確認 Python 版本相容性
3. 檢查 `requirements.txt` 所有套件可安裝
4. 確認沒有語法錯誤

### 問題 4: 應用程式很慢

**可能原因**: 
- 首次載入需要初始化快取
- API 請求較多

**解決方法**:
- 正常現象，第二次使用會更快
- 快取機制會自動優化效能

## 📱 分享您的應用程式

部署成功後，您會獲得一個公開網址，例如：
```
https://taiwan-weather-dashboard.streamlit.app
```

您可以：
1. **分享連結**：將網址傳給任何人
2. **嵌入網站**：使用 iframe 嵌入
3. **自訂網域**：升級到 Streamlit Cloud Teams 版本

## 🔄 更新應用程式

當您修改程式碼並推送到 GitHub 後：

```bash
git add .
git commit -m "Update: 新增功能"
git push origin main
```

**Streamlit Cloud 會自動重新部署！** 無需手動操作。

## 📊 監控與管理

### 查看應用程式狀態

1. 登入 Streamlit Cloud
2. 在 Dashboard 中找到您的應用程式
3. 可以看到：
   - 運行狀態
   - 訪問次數
   - 資源使用情況

### 管理選項

- **Reboot app**: 重新啟動應用程式
- **Delete app**: 刪除應用程式
- **Settings**: 修改設定和 Secrets
- **Logs**: 查看運行日誌

## 🎉 完成！

恭喜您成功部署台灣氣象資料網站到 Streamlit Cloud！

### 後續步驟

1. **測試所有功能**確保運作正常
2. **分享給朋友**收集使用回饋
3. **持續優化**根據使用情況改進
4. **監控效能**確保穩定運行

### 資源連結

- **您的應用程式**: https://[your-app-name].streamlit.app
- **GitHub Repository**: https://github.com/Charles8745/AIOT-weather
- **Streamlit 文件**: https://docs.streamlit.io/
- **技術支援**: GitHub Issues

---

**🌟 如果部署成功，別忘了給專案 GitHub Repository 一個 Star！**
