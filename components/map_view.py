"""
地圖顯示元件 - 顯示全台天氣地圖
"""
import folium
from folium import plugins
import streamlit as st
from streamlit_folium import st_folium
from typing import Dict, List, Any
from utils.constants import CITY_COORDINATES, TAIWAN_CITIES
from utils.helpers import get_weather_icon
from modules.api_client import weather_api
from modules.data_processor import weather_processor
from modules.cache_manager import cache_manager


class WeatherMap:
    """天氣地圖類別"""
    
    def __init__(self):
        # 台灣中心座標
        self.taiwan_center = [23.5, 121.0]
        self.default_zoom = 7
    
    def create_weather_map(self, all_cities_data: Dict[str, Any]) -> folium.Map:
        """
        建立天氣地圖
        
        Args:
            all_cities_data: 所有縣市的天氣資料
            
        Returns:
            Folium 地圖物件
        """
        # 建立地圖
        weather_map = folium.Map(
            location=self.taiwan_center,
            zoom_start=self.default_zoom,
            tiles='OpenStreetMap',
            control_scale=True
        )
        
        # 為每個縣市添加標記
        for city_name, coordinates in CITY_COORDINATES.items():
            if city_name in all_cities_data:
                city_weather = all_cities_data[city_name]
                self._add_city_marker(weather_map, city_name, coordinates, city_weather)
        
        # 添加圖層控制
        folium.LayerControl().add_to(weather_map)
        
        return weather_map
    
    def _add_city_marker(self, map_obj: folium.Map, city_name: str, 
                        coordinates: tuple, weather_data: Dict[str, Any]) -> None:
        """
        在地圖上添加縣市標記
        
        Args:
            map_obj: Folium 地圖物件
            city_name: 縣市名稱
            coordinates: 座標 (緯度, 經度)
            weather_data: 天氣資料
        """
        if not weather_data or 'periods' not in weather_data or not weather_data['periods']:
            return
        
        # 取得當前時段的天氣
        current_period = weather_data['periods'][0]
        weather_desc = current_period.get('weather', '無資料')
        min_temp = current_period.get('min_temp', 'N/A')
        max_temp = current_period.get('max_temp', 'N/A')
        pop = current_period.get('pop', 'N/A')
        
        # 取得天氣圖示
        weather_emoji = get_weather_icon(weather_desc)
        
        # 根據溫度決定標記顏色
        if isinstance(max_temp, (int, float)):
            if max_temp >= 30:
                color = 'red'
            elif max_temp >= 25:
                color = 'orange'
            elif max_temp >= 20:
                color = 'green'
            elif max_temp >= 15:
                color = 'lightblue'
            else:
                color = 'blue'
        else:
            color = 'gray'
        
        # 建立彈出視窗內容
        popup_html = f"""
        <div style="font-family: Arial; min-width: 200px;">
            <h4 style="margin: 0 0 10px 0; color: #2c3e50;">
                {weather_emoji} {city_name}
            </h4>
            <div style="font-size: 14px;">
                <p style="margin: 5px 0;">
                    <b>天氣：</b>{weather_desc}
                </p>
                <p style="margin: 5px 0;">
                    <b>溫度：</b>{min_temp}°C ~ {max_temp}°C
                </p>
                <p style="margin: 5px 0;">
                    <b>降雨機率：</b>{pop}%
                </p>
            </div>
        </div>
        """
        
        # 建立圖示 HTML
        icon_html = f"""
        <div style="
            font-size: 24px;
            text-align: center;
            line-height: 1;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        ">
            {weather_emoji}
        </div>
        """
        
        # 添加標記
        folium.Marker(
            location=coordinates,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{city_name}: {weather_desc}",
            icon=folium.DivIcon(html=icon_html)
        ).add_to(map_obj)
        
        # 添加圓形標記顯示溫度
        if isinstance(max_temp, (int, float)):
            folium.CircleMarker(
                location=coordinates,
                radius=8,
                popup=f"{city_name}<br>{max_temp}°C",
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.3,
                weight=2
            ).add_to(map_obj)


def get_all_cities_weather() -> Dict[str, Any]:
    """
    取得所有縣市的天氣資料
    
    Returns:
        所有縣市的天氣資料字典
    """
    all_cities_data = {}
    
    # 檢查快取
    cache_key = "all_cities_weather"
    cached_data = cache_manager.get(cache_key)
    
    if cached_data:
        return cached_data
    
    # 取得所有縣市資料
    with st.spinner('載入全台天氣資料中...'):
        progress_bar = st.progress(0)
        total_cities = len(TAIWAN_CITIES)
        
        for idx, city in enumerate(TAIWAN_CITIES):
            try:
                # 檢查個別縣市快取
                city_cache_key = f"forecast_{city}"
                city_data = cache_manager.get(city_cache_key)
                
                if not city_data:
                    # 從 API 取得資料
                    forecast_data = weather_api.get_forecast(city)
                    if forecast_data:
                        city_data = weather_processor.parse_forecast_data(forecast_data, city)
                        if city_data:
                            cache_manager.set(city_cache_key, city_data)
                
                if city_data:
                    all_cities_data[city] = city_data
                
            except Exception as e:
                print(f"取得 {city} 天氣資料時發生錯誤: {e}")
            
            # 更新進度
            progress_bar.progress((idx + 1) / total_cities)
        
        progress_bar.empty()
    
    # 存入快取
    if all_cities_data:
        cache_manager.set(cache_key, all_cities_data, ttl=1800)  # 30 分鐘
    
    return all_cities_data


def render_weather_map():
    """渲染天氣地圖元件"""
    st.subheader('🗺️ 全台天氣地圖')
    
    # 取得所有縣市天氣資料
    all_cities_data = get_all_cities_weather()
    
    if not all_cities_data:
        st.error('❌ 無法載入天氣資料')
        return
    
    # 建立地圖
    weather_map_obj = WeatherMap()
    taiwan_map = weather_map_obj.create_weather_map(all_cities_data)
    
    # 顯示地圖
    st_folium(
        taiwan_map,
        width=None,
        height=600,
        returned_objects=[]
    )
    
    # 顯示圖例說明
    st.markdown('---')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('#### 📍 地圖說明')
        st.markdown("""
        - 🌡️ 點擊縣市圖示查看詳細天氣資訊
        - 🔴 紅色圓圈：高溫 (≥30°C)
        - 🟠 橙色圓圈：溫暖 (25-29°C)
        - 🟢 綠色圓圈：舒適 (20-24°C)
        - 🔵 藍色圓圈：涼爽 (<20°C)
        """)
    
    with col2:
        st.markdown('#### 📊 資料統計')
        
        # 統計資訊
        total_cities = len(all_cities_data)
        
        # 計算平均溫度
        all_temps = []
        for city_data in all_cities_data.values():
            if city_data.get('periods'):
                period = city_data['periods'][0]
                if period.get('max_temp'):
                    all_temps.append(period['max_temp'])
        
        if all_temps:
            avg_temp = sum(all_temps) / len(all_temps)
            max_temp_overall = max(all_temps)
            min_temp_overall = min(all_temps)
            
            st.write(f"📍 顯示縣市數: {total_cities}")
            st.write(f"🌡️ 全台平均溫度: {avg_temp:.1f}°C")
            st.write(f"🔥 最高溫: {max_temp_overall}°C")
            st.write(f"❄️ 最低溫: {min_temp_overall}°C")


# 建立地圖物件實例
weather_map = WeatherMap()
