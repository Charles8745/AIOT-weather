"""
API 客戶端 - 負責與中央氣象署 API 互動
"""
import requests
from typing import Optional, Dict, Any
from config.config import CWA_API_KEY, API_ENDPOINTS
from utils.rate_limiter import rate_limited_request


class WeatherAPIClient:
    """中央氣象署 API 客戶端"""
    
    def __init__(self):
        self.api_key = CWA_API_KEY
        self.base_headers = {
            'accept': 'application/json',
        }
    
    @rate_limited_request
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        發送 API 請求（已加入限速保護）
        
        Args:
            endpoint: API 端點 URL
            params: 額外的查詢參數
            
        Returns:
            API 回應的 JSON 資料，如果失敗則回傳 None
        """
        try:
            # 設定基本參數
            request_params = {'Authorization': self.api_key}
            if params:
                request_params.update(params)
            
            # 發送請求
            response = requests.get(
                endpoint,
                headers=self.base_headers,
                params=request_params,
                timeout=10
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.Timeout:
            print("API 請求超時")
            return None
        except requests.exceptions.RequestException as e:
            print(f"API 請求錯誤: {e}")
            return None
        except ValueError as e:
            print(f"JSON 解析錯誤: {e}")
            return None
    
    def get_forecast(self, location: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        取得一般天氣預報（36小時）
        
        Args:
            location: 縣市名稱，如果為 None 則取得所有縣市
            
        Returns:
            天氣預報資料
        """
        params = {}
        if location:
            params['locationName'] = location
        
        return self._make_request(API_ENDPOINTS['forecast'], params)
    
    def get_weather_36hr(self, location: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        取得36小時詳細天氣預報
        
        Args:
            location: 縣市名稱
            
        Returns:
            詳細天氣預報資料
        """
        params = {}
        if location:
            params['locationName'] = location
            
        return self._make_request(API_ENDPOINTS['weather_36hr'], params)
    
    def get_week_forecast(self, location: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        取得一週天氣預報
        
        Args:
            location: 縣市名稱
            
        Returns:
            一週天氣預報資料
        """
        params = {}
        if location:
            params['locationName'] = location
            
        return self._make_request(API_ENDPOINTS['weather_week'], params)
    
    def get_observation(self, station: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        取得觀測站即時資料
        
        Args:
            station: 觀測站名稱
            
        Returns:
            觀測資料
        """
        params = {}
        if station:
            params['stationName'] = station
            
        return self._make_request(API_ENDPOINTS['observation'], params)
    
    def get_warnings(self) -> Optional[Dict[str, Any]]:
        """
        取得天氣警特報
        
        Returns:
            警特報資料
        """
        return self._make_request(API_ENDPOINTS['warning'])


# 建立全域 API 客戶端實例
weather_api = WeatherAPIClient()
