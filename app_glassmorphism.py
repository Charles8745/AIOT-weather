"""
台灣氣象資料網站 - Glassmorphism 風格一頁式設計
"""
import streamlit as st
import time
from pathlib import Path
from config.config import PAGE_TITLE, PAGE_ICON
from modules.api_client import weather_api
from modules.data_processor import weather_processor
from modules.cache_manager import cache_manager
from utils.constants import TAIWAN_CITIES
from utils.helpers import get_weather_icon, format_temperature, format_probability
from utils.ui_helpers import show_error_with_details, performance_monitor

# 頁面設定
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 載入自訂 CSS
def load_css():
    css_file = Path(__file__).parent / "assets" / "styles" / "glassmorphism.css"
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# Session State 初始化
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = '臺北市'

# 頂部標題和縣市選擇器
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(f'<h1>{PAGE_ICON} WeatherWise Taiwan</h1>', unsafe_allow_html=True)

# 縣市選擇下拉選單
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    selected_city = st.selectbox(
        '選擇縣市',
        TAIWAN_CITIES,
        index=TAIWAN_CITIES.index(st.session_state.selected_city) if st.session_state.selected_city in TAIWAN_CITIES else 0,
        key='city_selector',
        label_visibility='collapsed'
    )
    st.session_state.selected_city = selected_city

st.markdown('<br>', unsafe_allow_html=True)

# 載入天氣資料
@st.cache_data(ttl=1800)
def get_cached_forecast(city):
    """獲取快取的天氣預報"""
    try:
        forecast_data = weather_api.get_forecast(city)
        if forecast_data:
            return weather_processor.parse_forecast_data(forecast_data, city)
    except Exception as e:
        st.error(f"載入天氣資料失敗: {str(e)}")
    return None

@st.cache_data(ttl=3600)
def get_cached_week_forecast(city):
    """獲取快取的一週預報"""
    try:
        from components.forecast_chart import get_week_forecast_data
        return get_week_forecast_data(city)
    except Exception:
        return None

@st.cache_data(ttl=600)
def get_cached_warnings():
    """獲取快取的天氣警報"""
    try:
        from components.weather_warnings import get_warnings_data
        return get_warnings_data()
    except Exception:
        return None

# 載入資料
with st.spinner('⏳ 載入天氣資料中...'):
    parsed_data = get_cached_forecast(selected_city)
    week_data = get_cached_week_forecast(selected_city)
    warnings_data = get_cached_warnings()

# ===== 主要內容區域 =====
if parsed_data:
    today_summary = weather_processor.get_today_summary(parsed_data)
    
    # 大型天氣顯示區
    st.markdown(f'''
    <div class="weather-hero">
        <div class="location">📍 {selected_city}</div>
        <div class="temperature">{today_summary["max_temp"]}°</div>
        <div class="description">{today_summary["weather_summary"]}</div>
        <div style="font-size: 5rem; margin-top: 1rem;">
            {get_weather_icon(today_summary["weather_summary"])}
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('<br>', unsafe_allow_html=True)
    
    # 資訊卡片網格
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
        <div class="info-card">
            <div class="icon">🌡️</div>
            <div class="value">{today_summary["min_temp"]}° - {today_summary["max_temp"]}°</div>
            <div class="label">溫度範圍</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="info-card">
            <div class="icon">💧</div>
            <div class="value">{int(today_summary["max_rain_prob"])}%</div>
            <div class="label">降雨機率</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        comfort_text = today_summary['periods'][0].get('comfort', '舒適') if today_summary['periods'] else '舒適'
        st.markdown(f'''
        <div class="info-card">
            <div class="icon">😌</div>
            <div class="value">{comfort_text}</div>
            <div class="label">舒適度</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        # 取得當前時間的風速（如果有的話）
        wind_speed = "--"
        if today_summary['periods']:
            wind_speed = "2-3"  # 這裡可以從 API 取得實際風速
        st.markdown(f'''
        <div class="info-card">
            <div class="icon">💨</div>
            <div class="value">{wind_speed}</div>
            <div class="label">風速 (m/s)</div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('<br><br>', unsafe_allow_html=True)

# Tab 選單 - 其他功能
tab1, tab2, tab3, tab4 = st.tabs(['📅 一週預報', '💨 空氣品質', '🗺️ 全台地圖', '⚠️ 天氣警報'])

# Tab 1: 一週預報
with tab1:
    if week_data:
        st.markdown('### 七天天氣預報')
        st.markdown('<br>', unsafe_allow_html=True)
        
        from components.forecast_chart import display_week_forecast_charts
        display_week_forecast_charts(week_data, selected_city)
        
        # 一週預報卡片
        cols = st.columns(7)
        
        for idx, day_data in enumerate(week_data[:7]):
            with cols[idx]:
                # 取得星期幾
                import datetime
                date_obj = datetime.datetime.fromisoformat(day_data['date'])
                weekday = ['週一', '週二', '週三', '週四', '週五', '週六', '週日'][date_obj.weekday()]
                
                # 天氣描述
                weather_desc = day_data.get('weather', '多雲')
                icon = get_weather_icon(weather_desc)
                
                st.markdown(f'''
                <div class="forecast-day">
                    <div class="day-name">{weekday}</div>
                    <div class="day-name">{date_obj.strftime("%m/%d")}</div>
                    <div class="icon">{icon}</div>
                    <div class="temp-high">{day_data.get("max_temp", "--")}°</div>
                    <div class="temp-low">{day_data.get("min_temp", "--")}°</div>
                    <div class="temp-low">💧 {day_data.get("rain_prob", "--")}%</div>
                </div>
                ''', unsafe_allow_html=True)
    else:
        st.info('📊 暫無一週預報資料')

# Tab 2: 空氣品質
with tab2:
    st.markdown('### 空氣品質監測')
    st.markdown('<br>', unsafe_allow_html=True)
    
    from components.air_quality import render_aqi_overview
    render_aqi_overview()

# Tab 3: 全台地圖
with tab3:
    st.markdown('### 全台天氣地圖')
    st.markdown('<br>', unsafe_allow_html=True)
    
    from components.map_view import render_weather_map
    render_weather_map()

# Tab 4: 天氣警報
with tab4:
    st.markdown('### 特殊天氣警報')
    st.markdown('<br>', unsafe_allow_html=True)
    
    if warnings_data and len(warnings_data) > 0:
        # 顯示警報數量
        st.markdown(f'<div class="alert-card"><strong>⚠️ 目前有 {len(warnings_data)} 則天氣警報</strong></div>', 
                   unsafe_allow_html=True)
        
        from components.weather_warnings import display_warnings_list
        display_warnings_list(warnings_data)
    else:
        st.success('✅ 目前沒有特殊天氣警報')

# 頁尾
st.markdown('<br><br>', unsafe_allow_html=True)
st.markdown('---')

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.markdown('''
    <div style="text-align: center; color: rgba(255, 255, 255, 0.6);">
        <p>© 2025 WeatherWise Taiwan</p>
        <p style="font-size: 0.9rem;">資料來源：中央氣象署開放資料平台</p>
        <p style="font-size: 0.8rem;">Powered by Streamlit | Designed with Glassmorphism</p>
    </div>
    ''', unsafe_allow_html=True)
