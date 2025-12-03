"""
台灣氣象資料網站 - 完整功能 Glassmorphism 設計
參考中央氣象署 APP 佈局
"""
import streamlit as st
import base64
from pathlib import Path
from config.config import PAGE_TITLE, PAGE_ICON
from modules.api_client import weather_api
from modules.data_processor import weather_processor
from utils.constants import TAIWAN_CITIES
from utils.helpers import get_weather_icon
import datetime

# 頁面設定
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 載入背景圖片為 base64
@st.cache_data
def get_base64_image():
    """將背景圖片轉換為 base64"""
    img_path = Path(__file__).parent / "_MMO2513.jpg"
    with open(img_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# 載入 CSS
def load_css_with_background():
    css_file = Path(__file__).parent / "assets" / "styles" / "glassmorphism.css"
    with open(css_file) as f:
        css_content = f.read()
    
    img_base64 = get_base64_image()
    
    background_css = f"""
    <style>
    {css_content}
    
    section[data-testid="stAppViewContainer"] {{
        background: url('data:image/jpeg;base64,{img_base64}') center/cover fixed no-repeat !important;
    }}
    
    section[data-testid="stAppViewContainer"]::after {{
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(20, 30, 50, 0.65);
        backdrop-filter: blur(3px);
        z-index: 0;
        pointer-events: none;
    }}
    
    .main .block-container {{
        position: relative;
        z-index: 1;
        padding: 1rem 2rem !important;
        max-width: 100% !important;
    }}
    </style>
    """
    
    st.markdown(background_css, unsafe_allow_html=True)

load_css_with_background()

# Session State
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = '臺北市'

# 載入資料函數
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

@st.cache_data(ttl=600)
def get_aqi_data_cached():
    try:
        from components.air_quality import get_aqi_data, process_aqi_data
        aqi_data = get_aqi_data()
        if aqi_data:
            return process_aqi_data(aqi_data)
    except:
        pass
    return None

@st.cache_data(ttl=600)
def get_warnings_cached():
    try:
        from components.weather_warnings import get_warnings_data
        return get_warnings_data()
    except:
        pass
    return None

# ===== 頂部標題 =====
st.markdown('''
<div style="text-align: center; margin-bottom: 1rem;">
    <h1 style="font-size: 2.8rem; font-weight: 300; color: white; 
               text-shadow: 0 2px 15px rgba(0,0,0,0.7); margin: 0;">
        ☁️ WeatherWise Taiwan
    </h1>
</div>
''', unsafe_allow_html=True)

# 縣市選擇
col1, col2, col3 = st.columns([1.5, 1, 1.5])
with col2:
    selected_city = st.selectbox(
        '選擇縣市',
        TAIWAN_CITIES,
        index=TAIWAN_CITIES.index(st.session_state.selected_city),
        label_visibility='collapsed'
    )
    st.session_state.selected_city = selected_city

st.markdown('<br>', unsafe_allow_html=True)

# 載入資料
parsed_data = get_weather_data(selected_city)
week_df = get_week_data(selected_city)
aqi_df = get_aqi_data_cached()
warnings_data = get_warnings_cached()

if parsed_data:
    today_summary = weather_processor.get_today_summary(parsed_data)
    
    # ===== 主要三欄佈局 =====
    left_col, center_col, right_col = st.columns([1, 1.2, 1])
    
    # ========== 左側欄 ==========
    with left_col:
        # 狀態卡片
        st.markdown(f'''
        <div class="glass-card" style="padding: 1.5rem; margin-bottom: 1rem;">
            <div style="text-align: center;">
                <div style="font-size: 0.95rem; color: rgba(255,255,255,0.7); margin-bottom: 1rem;">狀態</div>
                <div style="font-size: 3rem; margin: 1rem 0;">
                    {get_weather_icon(today_summary["weather_summary"])}
                </div>
                <div style="font-size: 1.1rem; color: white; margin-bottom: 1.5rem; font-weight: 500;">
                    {today_summary["weather_summary"]}
                </div>
                <div style="border-top: 1px solid rgba(255,255,255,0.15); padding-top: 1rem;">
                    <div style="display: flex; justify-content: space-between; margin: 0.6rem 0;">
                        <span style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">舒適度</span>
                        <span style="color: white; font-size: 0.9rem; font-weight: 500;">
                            {today_summary['periods'][0].get('comfort', '舒適') if today_summary['periods'] else '舒適'}
                        </span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 0.6rem 0;">
                        <span style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">降雨機率</span>
                        <span style="color: white; font-size: 0.9rem; font-weight: 500;">
                            {int(today_summary["max_rain_prob"])}%
                        </span>
                    </div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # 本週天氣趨勢
        st.markdown('''
        <div class="glass-card" style="padding: 1.2rem; margin-bottom: 1rem;">
            <div style="font-size: 0.95rem; color: rgba(255,255,255,0.8); margin-bottom: 1rem; font-weight: 500;">
                本週天氣趨勢
            </div>
        ''', unsafe_allow_html=True)
        
        if week_df is not None and not week_df.empty:
            daily_data = week_df.groupby('date').agg({
                'min_temp': 'min',
                'max_temp': 'max',
                'weather': 'first',
                'weekday': 'first'
            }).reset_index().head(4)
            
            for _, day in daily_data.iterrows():
                weekday = day.get('weekday', '')
                weather = day.get('weather', '')
                icon = get_weather_icon(weather)
                min_t = day.get('min_temp', 0)
                max_t = day.get('max_temp', 0)
                
                st.markdown(f'''
                <div style="background: rgba(255,255,255,0.06); border-radius: 10px; 
                            padding: 0.8rem 1rem; margin: 0.5rem 0;
                            display: flex; justify-content: space-between; align-items: center;">
                    <div style="flex: 1; text-align: left; color: rgba(255,255,255,0.85); font-size: 0.9rem;">
                        {weekday}
                    </div>
                    <div style="flex: 1; text-align: center; font-size: 1.5rem;">{icon}</div>
                    <div style="flex: 1; text-align: right;">
                        <span style="color: white; font-weight: 600; font-size: 0.95rem;">{max_t:.0f}°</span>
                        <span style="color: rgba(255,255,255,0.6); font-size: 0.85rem;"> {min_t:.0f}°</span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== 中央欄 - 大型溫度顯示 ==========
    with center_col:
        st.markdown(f'''
        <div class="weather-hero" style="padding: 2.5rem 2rem; margin-bottom: 1rem;">
            <div style="font-size: 1rem; color: rgba(255,255,255,0.9); margin-bottom: 0.5rem;">
                📍 {selected_city}
            </div>
            <div style="display: flex; align-items: center; justify-content: center; margin: 1.5rem 0;">
                <div style="font-size: 8rem; font-weight: 200; color: white; 
                           text-shadow: 0 4px 20px rgba(0,0,0,0.5); line-height: 1; letter-spacing: -5px;">
                    {today_summary["max_temp"]}°
                </div>
                <div style="margin-left: 2rem; text-align: left;">
                    <div style="color: rgba(255,255,255,0.8); font-size: 1rem; margin: 0.3rem 0;">
                        H {today_summary["max_temp"]}°
                    </div>
                    <div style="color: rgba(255,255,255,0.8); font-size: 1rem; margin: 0.3rem 0;">
                        L {today_summary["min_temp"]}°
                    </div>
                </div>
            </div>
            <div style="font-size: 1.8rem; color: white; margin: 1rem 0; font-weight: 300;">
                {today_summary["weather_summary"]}
            </div>
            <div style="font-size: 4.5rem; margin-top: 1rem; opacity: 0.95;">
                {get_weather_icon(today_summary["weather_summary"])}
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # 三時段預報
        if len(today_summary['periods']) >= 3:
            st.markdown('''
            <div class="glass-card" style="padding: 1rem;">
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem;">
            ''', unsafe_allow_html=True)
            
            time_labels = ['今日白天', '今晚明晨', '明日白天']
            for idx, (period, label) in enumerate(zip(today_summary['periods'][:3], time_labels)):
                icon = get_weather_icon(period['weather'])
                temp_range = f"{period['min_temp']}° - {period['max_temp']}°" if period['min_temp'] and period['max_temp'] else "--"
                pop = f"{period['pop']}%" if period['pop'] is not None else "--"
                
                st.markdown(f'''
                <div style="text-align: center; padding: 0.8rem; background: rgba(255,255,255,0.05); border-radius: 12px;">
                    <div style="font-size: 0.85rem; color: rgba(255,255,255,0.7); margin-bottom: 0.5rem;">{label}</div>
                    <div style="font-size: 2rem; margin: 0.5rem 0;">{icon}</div>
                    <div style="font-size: 0.9rem; color: white; font-weight: 500; margin: 0.3rem 0;">{temp_range}</div>
                    <div style="font-size: 0.85rem; color: rgba(255,255,255,0.7);">💧 {pop}</div>
                </div>
                ''', unsafe_allow_html=True)
            
            st.markdown('</div></div>', unsafe_allow_html=True)
    
    # ========== 右側欄 ==========
    with right_col:
        # 空氣品質
        st.markdown('''
        <div class="glass-card" style="padding: 1.5rem; margin-bottom: 1rem;">
            <div style="text-align: center;">
                <div style="font-size: 0.95rem; color: rgba(255,255,255,0.7); margin-bottom: 1rem;">空氣品質</div>
                <div style="font-size: 3rem; margin: 1rem 0;">💨</div>
        ''', unsafe_allow_html=True)
        
        if aqi_df is not None and not aqi_df.empty:
            city_name_variants = [selected_city, selected_city.replace('台', '臺'), selected_city.replace('臺', '台')]
            city_aqi = aqi_df[aqi_df['縣市'].isin(city_name_variants) | 
                             aqi_df['縣市'].str.contains(selected_city[:2])]
            
            if not city_aqi.empty:
                avg_aqi = int(city_aqi['AQI'].mean())
                if avg_aqi <= 50:
                    level, color = "良好", "#7ED321"
                elif avg_aqi <= 100:
                    level, color = "普通", "#F5A623"
                else:
                    level, color = "不良", "#E94B3C"
                
                st.markdown(f'''
                <div style="font-size: 2.5rem; color: white; font-weight: 600; margin: 0.8rem 0;">
                    {avg_aqi}
                </div>
                <div style="font-size: 1.1rem; color: {color}; font-weight: 500; margin-bottom: 1rem;">
                    {level}
                </div>
                <div style="font-size: 0.85rem; color: rgba(255,255,255,0.6);">
                    資料來源：環保署 (12/03 09:00:00)
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown('<div style="color: rgba(255,255,255,0.5); font-size: 0.9rem;">暫無資料</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color: rgba(255,255,255,0.5); font-size: 0.9rem;">暫無資料</div>', unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        
        # 天氣警報
        st.markdown('''
        <div class="glass-card" style="padding: 1.5rem;">
            <div style="text-align: center;">
                <div style="font-size: 0.95rem; color: rgba(255,255,255,0.7); margin-bottom: 1rem;">天氣警報</div>
                <div style="font-size: 3rem; margin: 1rem 0;">⚠️</div>
        ''', unsafe_allow_html=True)
        
        if warnings_data and 'records' in warnings_data:
            records = warnings_data['records']
            if 'record' in records and len(records['record']) > 0:
                count = len(records['record'])
                st.markdown(f'''
                <div style="font-size: 2rem; color: #F5A623; font-weight: 600; margin: 0.8rem 0;">
                    {count} 則警報
                </div>
                <div style="font-size: 0.9rem; color: rgba(255,255,255,0.7); margin-bottom: 0.5rem;">
                    點擊下方查看詳情
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown('''
                <div style="color: #7ED321; font-size: 1.1rem; font-weight: 500; margin: 1rem 0;">
                    無特殊警報 ✓
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div style="color: #7ED321; font-size: 1.1rem; font-weight: 500; margin: 1rem 0;">
                無特殊警報 ✓
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)

# ===== 下方功能按鈕區 =====
st.markdown('<br>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button('📊 縣市預報總覽', use_container_width=True):
        st.session_state.show_overview = True

with col2:
    if st.button('🗺️ 全台天氣地圖', use_container_width=True):
        st.session_state.show_map = True

with col3:
    if st.button('📅 一週天氣預報', use_container_width=True):
        st.session_state.show_week = True

with col4:
    if st.button('💨 空氣品質監測', use_container_width=True):
        st.session_state.show_aqi = True

# 顯示額外內容
if st.session_state.get('show_overview'):
    with st.expander('📊 縣市預報總覽', expanded=True):
        from components.weather_overview import render_overview_content
        render_overview_content()

if st.session_state.get('show_map'):
    with st.expander('🗺️ 全台天氣地圖', expanded=True):
        from components.map_view import render_weather_map
        render_weather_map()

if st.session_state.get('show_week'):
    with st.expander('📅 一週天氣預報', expanded=True):
        from components.forecast_chart import render_week_forecast
        render_week_forecast(selected_city)

if st.session_state.get('show_aqi'):
    with st.expander('💨 空氣品質監測', expanded=True):
        from components.air_quality import render_aqi_overview
        render_aqi_overview()

# 頁尾
st.markdown('''
<div style="text-align: center; margin-top: 2rem; padding: 1rem;">
    <div style="color: rgba(255,255,255,0.4); font-size: 0.85rem;">
        © 2025 WeatherWise Taiwan | 資料來源：中央氣象署開放資料平台
    </div>
</div>
''', unsafe_allow_html=True)
