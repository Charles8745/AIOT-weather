"""
輔助函數
"""
from typing import Optional
from utils.constants import WEATHER_ICONS


def get_weather_icon(weather_description: str) -> str:
    """
    根據天氣描述取得對應的圖示
    
    Args:
        weather_description: 天氣描述文字
        
    Returns:
        天氣圖示 emoji
    """
    for key, icon in WEATHER_ICONS.items():
        if key in weather_description:
            return icon
    
    # 預設圖示
    if '晴' in weather_description:
        return '☀️'
    elif '雨' in weather_description:
        return '🌧️'
    elif '雲' in weather_description or '陰' in weather_description:
        return '☁️'
    else:
        return '🌤️'


def get_aqi_info(aqi_value: int) -> dict:
    """
    根據 AQI 數值取得對應的等級資訊
    
    Args:
        aqi_value: AQI 數值
        
    Returns:
        包含等級、標籤和顏色的字典
    """
    from utils.constants import AQI_LEVELS
    
    for level, info in AQI_LEVELS.items():
        if info['range'][0] <= aqi_value <= info['range'][1]:
            return {
                'level': level,
                'label': info['label'],
                'color': info['color'],
                'value': aqi_value
            }
    
    # 超出範圍時回傳危害等級
    return {
        'level': 'hazardous',
        'label': '危害',
        'color': '#7E0023',
        'value': aqi_value
    }


def format_temperature(temp: Optional[float]) -> str:
    """
    格式化溫度顯示
    
    Args:
        temp: 溫度數值
        
    Returns:
        格式化的溫度字串
    """
    if temp is None:
        return 'N/A'
    return f"{temp}°C"


def format_probability(prob: Optional[int]) -> str:
    """
    格式化機率顯示
    
    Args:
        prob: 機率數值（0-100）
        
    Returns:
        格式化的機率字串
    """
    if prob is None:
        return 'N/A'
    return f"{prob}%"
