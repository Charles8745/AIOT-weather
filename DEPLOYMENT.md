# 部署指南 📦

本文件說明如何將台灣氣象資料網站部署到 Streamlit Cloud。

## 📋 部署前檢查清單

### 必要檔案
- [x] `app.py` - 主程式
- [x] `requirements.txt` - 依賴套件清單
- [x] `.env.example` - 環境變數範本
- [x] `.gitignore` - Git 忽略清單
- [x] `README.md` - 專案說明
- [x] `.streamlit/config.toml` - Streamlit 設定

### 程式碼檢查
- [x] 所有模組正常運作
- [x] API 金鑰使用環境變數
- [x] 無硬編碼的敏感資訊
- [x] 錯誤處理機制完整
- [x] 快取機制正常運作

### 測試檢查
- [x] 本地測試通過
- [x] 所有功能可正常使用
- [x] 響應速度可接受
- [x] 無明顯錯誤或警告

## 🚀 Streamlit Cloud 部署步驟

### 步驟 1: 準備 GitHub Repository

1. **確認 Git 狀態**
   ```bash
   git status
   ```

2. **提交所有變更**
   ```bash
   git add .
   git commit -m "feat: 完成部署準備，準備發布 v1.0.0"
   ```

3. **推送到 GitHub**
   ```bash
   git push origin main
   ```

### 步驟 2: 設定 Streamlit Cloud

1. **前往 Streamlit Cloud**
   - 網址：https://share.streamlit.io/
   - 使用 GitHub 帳號登入

2. **建立新應用**
   - 點擊 "New app" 按鈕
   - 選擇 Repository：`Charles8745/AIOT-weather`
   - Branch：`main`
   - Main file path：`app.py`

3. **設定環境變數（重要！）**
   點擊 "Advanced settings"，在 Secrets 區塊加入：
   
   ```toml
   CWA_API_KEY = "CWA-E2FC2F13-090B-4F3D-8055-521347898182"
   MOENV_API_KEY = "fc3438b1-5643-49c4-b2f6-5017887b72ad"
   ```

4. **部署應用**
   - 點擊 "Deploy!"
   - 等待 2-5 分鐘，系統會自動安裝依賴並啟動應用

### 步驟 3: 驗證部署

部署完成後，檢查以下項目：

- [ ] 應用程式成功啟動
- [ ] 縣市選擇器正常運作
- [ ] 天氣資料正確載入
- [ ] 三時段預報顯示正常
- [ ] 全台地圖可正常開啟
- [ ] 縣市總覽搜尋功能正常
- [ ] 一週預報圖表正常顯示
- [ ] 空氣品質資料正確載入
- [ ] 天氣警報正常顯示
- [ ] 無明顯錯誤訊息

## 🔧 常見問題排解

### 問題 1: ModuleNotFoundError

**症狀**: 部署時出現「找不到模組」錯誤

**解決方案**:
```bash
# 更新 requirements.txt
pip freeze > requirements.txt

# 提交並推送
git add requirements.txt
git commit -m "fix: 更新 requirements.txt"
git push origin main
```

### 問題 2: API 金鑰錯誤

**症狀**: 無法載入天氣資料

**解決方案**:
1. 檢查 Streamlit Cloud 的 Secrets 設定
2. 確認 API 金鑰格式正確（無多餘空格）
3. 重新部署應用

### 問題 3: 記憶體不足

**症狀**: 應用程式崩潰或載入緩慢

**解決方案**:
```python
# 在 app.py 中調整快取設定
@st.cache_data(ttl=3600, max_entries=50)  # 減少快取項目
def get_weather_data(city):
    # ...
```

### 問題 4: 靜態資源載入失敗

**症狀**: CSS 或圖片無法載入

**解決方案**:
- 確認檔案路徑使用相對路徑
- 檢查 `.gitignore` 是否誤排除了必要檔案
- 確認 `assets/` 目錄已提交至 Git

## 📊 效能優化建議

### 1. 快取策略
```python
# 不同資料使用不同的快取時間
@st.cache_data(ttl=1800)  # 30 分鐘 - 天氣預報
@st.cache_data(ttl=3600)  # 1 小時 - 週預報
@st.cache_data(ttl=600)   # 10 分鐘 - 空氣品質
```

### 2. 減少 API 請求
- 使用快取減少重複請求
- 實作請求速率限制
- 批次載入資料

### 3. 優化載入速度
- 延遲載入非關鍵資料
- 使用 `st.spinner()` 提供載入提示
- 減少初始載入的資料量

## 🔄 更新部署

當需要更新應用程式時：

```bash
# 1. 進行修改
# 2. 測試修改
streamlit run app.py

# 3. 提交變更
git add .
git commit -m "feat: 新增功能說明"
git push origin main

# 4. Streamlit Cloud 會自動重新部署
```

## 📈 監控與維護

### 查看應用日誌
1. 登入 Streamlit Cloud
2. 進入應用程式設定
3. 查看 "Logs" 分頁

### 效能監控
- 觀察應用程式載入時間
- 檢查 API 請求次數
- 監控錯誤率

### 定期維護
- [ ] 每週檢查 API 金鑰有效性
- [ ] 每月更新依賴套件
- [ ] 定期檢查錯誤日誌
- [ ] 追蹤使用者反饋

## 🎯 部署檢查表

部署前請確認：

- [ ] 所有功能已測試
- [ ] API 金鑰已設定為環境變數
- [ ] requirements.txt 包含所有依賴
- [ ] .gitignore 正確設定
- [ ] README.md 完整且準確
- [ ] 無硬編碼的敏感資訊
- [ ] 錯誤處理機制完善
- [ ] 快取機制正常運作
- [ ] 程式碼已推送至 GitHub
- [ ] Streamlit Cloud 設定正確

## 📞 需要協助？

如遇到部署問題：
1. 查看 Streamlit Cloud 日誌
2. 檢查 GitHub Issues
3. 參考 Streamlit 官方文件：https://docs.streamlit.io/
4. 透過 GitHub Issues 回報問題

---

**祝您部署順利！🎉**
