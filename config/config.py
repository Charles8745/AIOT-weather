"""
設定檔 - 載入環境變數和常數
"""
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 中央氣象署 API 設定
CWA_API_KEY = os.getenv('CWA_API_KEY')
CWA_BASE_URL = 'https://opendata.cwa.gov.tw/api'

# 環保署 API 設定
MOENV_API_KEY = os.getenv('MOENV_API_KEY')

# API 端點
API_ENDPOINTS = {
    'forecast': f'{CWA_BASE_URL}/v1/rest/datastore/F-C0032-001',  # 一般天氣預報
    'weather_36hr': f'{CWA_BASE_URL}/v1/rest/datastore/F-D0047-089',  # 36小時天氣預報
    'weather_week': f'{CWA_BASE_URL}/v1/rest/datastore/F-D0047-091',  # 一週天氣預報
    'observation': f'{CWA_BASE_URL}/v1/rest/datastore/O-A0001-001',  # 自動氣象站觀測資料
    'warning': f'{CWA_BASE_URL}/v1/rest/datastore/W-C0033-001',  # 天氣警特報
    'aqi': 'https://data.moenv.gov.tw/api/v2/aqx_p_432',  # 空氣品質指標 (環保署)
}

# 快取設定
CACHE_EXPIRY = 1800  # 30分鐘（秒）

# 頁面設定
PAGE_TITLE = '台灣天氣資訊站'
PAGE_ICON = '🌤️'
LAYOUT = 'wide'
