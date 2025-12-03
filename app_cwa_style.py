"""
台灣氣象資料網站 - 中央氣象署風格設計
"""
import streamlit as st
from pathlib import Path
from config.config import PAGE_TITLE, PAGE_ICON
from modules.api_client import weather_api
from modules.data_processor import weather_processor
from utils.constants import TAIWAN_CITIES
from utils.helpers import get_weather_icon

# 頁面設定
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 載入 CSS
def load_css():
    css_file = Path(__file__).parent / "assets" / "styles" / "cwa_style.css"
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# Session State 初始化
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = '臺北市'
if 'active_view' not in st.session_state:
    st.session_state.active_view = None

# 載入資料
@st.cache_data(ttl=1800)
def get_weather_data(city):
    try:
        forecast_data = weather_api.get_forecast(city)
        if forecast_data:
            return weather_processor.parse_forecast_data(forecast_data, city)
    except:
        pass
    return None

@st.cache_data(ttl=3600)
def get_week_data(city):
    try:
        from components.forecast_chart import get_week_forecast_data, parse_week_forecast
        api_data = get_week_forecast_data(city)
        if api_data:
            return parse_week_forecast(api_data, city)
    except:
        pass
    return None

# ===== 頂部標題 =====
st.markdown('''
<div style="text-align: center; margin-bottom: 1.5rem;">
    <h1>☁️ 台灣氣象資料網站</h1>
    <p style="color: white; font-size: 1rem; margin-top: 0.5rem;">即時天氣 · 精準預報 · 一目了然</p>
</div>
''', unsafe_allow_html=True)

# 縣市選擇
col1, col2, col3 = st.columns([1.5, 1, 1.5])
with col2:
    selected_city = st.selectbox(
        '選擇縣市',
        TAIWAN_CITIES,
        index=TAIWAN_CITIES.index(st.session_state.selected_city),
        key='city_select',
        label_visibility='collapsed'
    )
    st.session_state.selected_city = selected_city

st.markdown('<br>', unsafe_allow_html=True)

# 載入當前縣市資料
parsed_data = get_weather_data(selected_city)
week_df = get_week_data(selected_city)

if parsed_data:
    today_summary = weather_processor.get_today_summary(parsed_data)
    
    # ===== 主要三欄佈局 =====
    left_col, center_col, right_col = st.columns([1, 1.4, 1])
    
    # ========== 左側欄：狀態 + 週預報 ==========
    with left_col:
        st.markdown(f'''
        <div class="weather-card">
            <div style="text-align: center;">
                <h3 style="color: #4A90E2; margin-bottom: 1rem; font-size: 1.1rem;">📊 目前狀態</h3>
                <div style="font-size: 3.5rem; margin: 1.5rem 0;">
                    {get_weather_icon(today_summary["weather_summary"])}
                </div>
                <div style="font-size: 1.3rem; color: #2C3E50; font-weight: 600; margin-bottom: 1.5rem;">
                    {today_summary["weather_summary"]}
                </div>
                <div style="border-top: 2px solid #E8EEF2; padding-top: 1rem; margin-top: 1rem;">
                    <div style="display: flex; justify-content: space-between; margin: 0.8rem 0;">
                        <span style="color: #7F8C8D; font-size: 0.95rem;">舒適度</span>
                        <span style="color: #2C3E50; font-size: 0.95rem; font-weight: 600;">
                            {today_summary['periods'][0].get('comfort', '舒適') if today_summary['periods'] else '舒適'}
                        </span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 0.8rem 0;">
                        <span style="color: #7F8C8D; font-size: 0.95rem;">降雨機率</span>
                        <span style="color: #4A90E2; font-size: 0.95rem; font-weight: 700;">
                            {int(today_summary["max_rain_prob"])}%
                        </span>
                    </div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # 本週預報
        st.markdown('''
        <div class="weather-card" style="margin-top: 1rem;">
            <h3 style="color: #4A90E2; margin-bottom: 1rem; font-size: 1.1rem;">📅 本週預報</h3>
        ''', unsafe_allow_html=True)
        
        if week_df is not None and not week_df.empty:
            daily_data = week_df.groupby('date').agg({
                'min_temp': 'min',
                'max_temp': 'max',
                'weather': 'first',
                'weekday': 'first'
            }).reset_index().head(5)
            
            for _, day in daily_data.iterrows():
                weekday = day.get('weekday', '')
                weather = day.get('weather', '')
                icon = get_weather_icon(weather)
                min_t = day.get('min_temp', 0)
                max_t = day.get('max_temp', 0)
                
                st.markdown(f'''
                <div class="week-forecast-item">
                    <div style="flex: 1; text-align: left; color: #2C3E50; font-weight: 600; font-size: 0.95rem;">
                        {weekday}
                    </div>
                    <div style="flex: 1; text-align: center; font-size: 1.8rem;">{icon}</div>
                    <div style="flex: 1; text-align: right;">
                        <span style="color: #E74C3C; font-weight: 700; font-size: 1rem;">{max_t:.0f}°</span>
                        <span style="color: #7F8C8D; font-size: 0.9rem;"> / {min_t:.0f}°</span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== 中央欄：大型溫度顯示 ==========
    with center_col:
        st.markdown(f'''
        <div class="main-weather-card">
            <div style="font-size: 1.1rem; color: #7F8C8D; margin-bottom: 1rem; font-weight: 500;">
                📍 {selected_city}
            </div>
            <div style="display: flex; align-items: center; justify-content: center; margin: 2rem 0;">
                <div class="temperature-display">
                    {today_summary["max_temp"]}°
                </div>
                <div style="margin-left: 2.5rem; text-align: left;">
                    <div style="color: #E74C3C; font-size: 1.2rem; margin: 0.5rem 0; font-weight: 600;">
                        ▲ {today_summary["max_temp"]}°
                    </div>
                    <div style="color: #3498DB; font-size: 1.2rem; margin: 0.5rem 0; font-weight: 600;">
                        ▼ {today_summary["min_temp"]}°
                    </div>
                </div>
            </div>
            <div class="weather-description">
                {today_summary["weather_summary"]}
            </div>
            <div class="weather-icon-large">
                {get_weather_icon(today_summary["weather_summary"])}
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # 三時段預報
        if len(today_summary['periods']) >= 3:
            st.markdown('<div class="weather-card" style="margin-top: 1rem;">', unsafe_allow_html=True)
            st.markdown('<h3 style="color: #4A90E2; margin-bottom: 1rem; font-size: 1.1rem; text-align: center;">⏰ 分時段預報</h3>', unsafe_allow_html=True)
            
            cols = st.columns(3)
            time_labels = ['今日白天', '今晚明晨', '明日白天']
            
            for idx, (period, label) in enumerate(zip(today_summary['periods'][:3], time_labels)):
                with cols[idx]:
                    icon = get_weather_icon(period['weather'])
                    temp_range = f"{period['min_temp']}° ~ {period['max_temp']}°" if period['min_temp'] and period['max_temp'] else "--"
                    pop = f"{period['pop']}%" if period['pop'] is not None else "--"
                    
                    st.markdown(f'''
                    <div class="time-period-card">
                        <div class="time-label">{label}</div>
                        <div class="icon">{icon}</div>
                        <div class="temp">{temp_range}</div>
                        <div style="color: #3498DB; font-size: 0.9rem; font-weight: 600; margin-top: 0.5rem;">
                            💧 {pop}
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== 右側欄：空氣品質 + 警報 ==========
    with right_col:
        # 空氣品質
        st.markdown('''
        <div class="weather-card">
            <div style="text-align: center;">
                <h3 style="color: #4A90E2; margin-bottom: 1rem; font-size: 1.1rem;">💨 空氣品質</h3>
                <div style="font-size: 3rem; margin: 1rem 0;">🌬️</div>
        ''', unsafe_allow_html=True)
        
        try:
            from components.air_quality import get_aqi_data, process_aqi_data
            aqi_df = get_aqi_data()
            if aqi_df:
                aqi_df = process_aqi_data(aqi_df)
                if not aqi_df.empty:
                    city_aqi = aqi_df[aqi_df['縣市'].str.contains(selected_city[:2])]
                    if not city_aqi.empty:
                        avg_aqi = int(city_aqi['AQI'].mean())
                        if avg_aqi <= 50:
                            level, color, bg = "良好", "#28A745", "#D4EDDA"
                        elif avg_aqi <= 100:
                            level, color, bg = "普通", "#FFC107", "#FFF3CD"
                        else:
                            level, color, bg = "不良", "#DC3545", "#F8D7DA"
                        
                        st.markdown(f'''
                        <div style="font-size: 3rem; color: {color}; font-weight: 700; margin: 1rem 0;">
                            {avg_aqi}
                        </div>
                        <div class="status-badge" style="background: {bg}; color: {color}; border-color: {color};">
                            {level}
                        </div>
                        <div style="font-size: 0.8rem; color: #7F8C8D; margin-top: 1rem;">
                            資料來源：環保署
                        </div>
                        ''', unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="color: #7F8C8D; font-size: 0.95rem;">暫無資料</div>', unsafe_allow_html=True)
        except:
            st.markdown('<div style="color: #7F8C8D; font-size: 0.95rem;">載入中...</div>', unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        
        # 天氣警報
        st.markdown('''
        <div class="weather-card" style="margin-top: 1rem;">
            <div style="text-align: center;">
                <h3 style="color: #4A90E2; margin-bottom: 1rem; font-size: 1.1rem;">⚠️ 天氣警報</h3>
                <div style="font-size: 3rem; margin: 1rem 0;">🚨</div>
        ''', unsafe_allow_html=True)
        
        try:
            from components.weather_warnings import get_warnings_data
            warnings = get_warnings_data()
            if warnings and 'records' in warnings:
                records = warnings['records']
                if 'record' in records and len(records['record']) > 0:
                    count = len(records['record'])
                    st.markdown(f'''
                    <div style="font-size: 2.5rem; color: #FFC107; font-weight: 700; margin: 1rem 0;">
                        {count}
                    </div>
                    <div class="status-badge status-moderate">則警報生效中</div>
                    ''', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="status-badge status-good" style="font-size: 1rem; padding: 0.6rem 1.2rem;">✓ 無特殊警報</div>', unsafe_allow_html=True)
        except:
            st.markdown('<div style="color: #7F8C8D; font-size: 0.95rem;">載入中...</div>', unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)

else:
    st.error('⚠️ 無法載入天氣資料，請稍後再試')

# ===== 功能按鈕區（使用單選按鈕避免累積） =====
st.markdown('<br><br>', unsafe_allow_html=True)
st.markdown('<div class="weather-card" style="padding: 1.5rem;">', unsafe_allow_html=True)
st.markdown('<h3 style="color: #4A90E2; text-align: center; margin-bottom: 1rem;">📱 更多功能</h3>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button('🗺️ 全台地圖', key='btn_map', use_container_width=True):
        st.session_state.active_view = 'map' if st.session_state.active_view != 'map' else None

with col2:
    if st.button('📊 縣市總覽', key='btn_overview', use_container_width=True):
        st.session_state.active_view = 'overview' if st.session_state.active_view != 'overview' else None

with col3:
    if st.button('📈 完整預報', key='btn_week', use_container_width=True):
        st.session_state.active_view = 'week' if st.session_state.active_view != 'week' else None

with col4:
    if st.button('💨 空品詳情', key='btn_aqi', use_container_width=True):
        st.session_state.active_view = 'aqi' if st.session_state.active_view != 'aqi' else None

st.markdown('</div>', unsafe_allow_html=True)

# ===== 顯示選中的內容（只顯示一個）=====
if st.session_state.active_view:
    st.markdown('<div class="weather-card" style="margin-top: 1rem; padding: 2rem;">', unsafe_allow_html=True)
    
    if st.session_state.active_view == 'map':
        st.markdown('<h2 style="color: #4A90E2; text-align: center; margin-bottom: 1.5rem;">🗺️ 全台天氣地圖</h2>', unsafe_allow_html=True)
        from components.map_view import render_weather_map
        render_weather_map()
    
    elif st.session_state.active_view == 'overview':
        st.markdown('<h2 style="color: #4A90E2; text-align: center; margin-bottom: 1.5rem;">📊 全台縣市總覽</h2>', unsafe_allow_html=True)
        from components.weather_overview import render_overview_content
        render_overview_content()
    
    elif st.session_state.active_view == 'week':
        st.markdown(f'<h2 style="color: #4A90E2; text-align: center; margin-bottom: 1.5rem;">📈 {selected_city} 完整預報</h2>', unsafe_allow_html=True)
        from components.forecast_chart import render_week_forecast
        render_week_forecast(selected_city)
    
    elif st.session_state.active_view == 'aqi':
        st.markdown('<h2 style="color: #4A90E2; text-align: center; margin-bottom: 1.5rem;">💨 空氣品質監測</h2>', unsafe_allow_html=True)
        from components.air_quality import render_aqi_overview
        render_aqi_overview()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ===== 頁尾 =====
st.markdown('''
<div style="text-align: center; margin-top: 3rem; padding: 2rem; color: white;">
    <div style="font-size: 0.9rem; margin-bottom: 0.5rem;">
        © 2025 台灣氣象資料網站 | WeatherWise Taiwan
    </div>
    <div style="font-size: 0.85rem; opacity: 0.8;">
        資料來源：中央氣象署開放資料平台 | Powered by Streamlit
    </div>
</div>
''', unsafe_allow_html=True)
