"""
台灣氣象資料網站 - Glassmorphism 風格一頁式設計
"""
import streamlit as st
import base64
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

# 載入背景圖片為 base64
@st.cache_data
def get_base64_image():
    """將背景圖片轉換為 base64"""
    img_path = Path(__file__).parent / "_MMO2513.jpg"
    with open(img_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# 載入 CSS 並注入背景圖片
def load_css_with_background():
    css_file = Path(__file__).parent / "assets" / "styles" / "glassmorphism.css"
    with open(css_file) as f:
        css_content = f.read()
    
    # 注入背景圖片
    img_base64 = get_base64_image()
    
    background_css = f"""
    <style>
    {css_content}
    
    /* 注入背景圖片 */
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
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 100% !important;
    }}
    
    /* 確保內容不超出視窗 */
    .element-container {{
        max-height: none !important;
    }}
    </style>
    """
    
    st.markdown(background_css, unsafe_allow_html=True)

load_css_with_background()

# Session State
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = '臺北市'

# 載入天氣資料
@st.cache_data(ttl=1800)
def get_weather_data(city):
    """獲取天氣資料"""
    try:
        forecast_data = weather_api.get_forecast(city)
        if forecast_data:
            return weather_processor.parse_forecast_data(forecast_data, city)
    except:
        pass
    return None

# ===== 頂部區域：標題 + 縣市選擇 =====
col_left, col_center, col_right = st.columns([1, 2, 1])
with col_center:
    st.markdown('''
    <div style="text-align: center; margin-bottom: 0.5rem;">
        <h1 style="font-size: 2.5rem; font-weight: 300; color: white; 
                   text-shadow: 0 2px 10px rgba(0,0,0,0.5); margin: 0;">
            ☁️ WeatherWise Taiwan
        </h1>
    </div>
    ''', unsafe_allow_html=True)

# 縣市選擇
col1, col2, col3 = st.columns([1.5, 1, 1.5])
with col2:
    selected_city = st.selectbox(
        '',
        TAIWAN_CITIES,
        index=TAIWAN_CITIES.index(st.session_state.selected_city) if st.session_state.selected_city in TAIWAN_CITIES else 0,
        label_visibility='collapsed'
    )
    st.session_state.selected_city = selected_city

# 載入資料
parsed_data = get_weather_data(selected_city)

if parsed_data:
    today_summary = weather_processor.get_today_summary(parsed_data)
    
    # ===== 主要內容：左側側邊欄 + 中央大型顯示 + 右側資訊 =====
    left_col, main_col, right_col = st.columns([0.8, 1.4, 0.8])
    
    # 左側：狀態卡片
    with left_col:
        st.markdown(f'''
        <div class="glass-card" style="margin-top: 1rem; padding: 1.5rem;">
            <div style="text-align: center;">
                <div style="font-size: 0.9rem; color: rgba(255,255,255,0.7); margin-bottom: 1rem;">狀態</div>
                <div style="font-size: 2.5rem; margin: 1rem 0;">
                    {get_weather_icon(today_summary["weather_summary"])}
                </div>
                <div style="font-size: 0.95rem; color: rgba(255,255,255,0.9); margin-bottom: 1rem;">
                    {today_summary["weather_summary"]}
                </div>
                <div style="border-top: 1px solid rgba(255,255,255,0.2); padding-top: 1rem; margin-top: 1rem;">
                    <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                        <span style="color: rgba(255,255,255,0.7); font-size: 0.85rem;">舒適度</span>
                        <span style="color: white; font-size: 0.85rem; font-weight: 500;">
                            {today_summary['periods'][0].get('comfort', '舒適') if today_summary['periods'] else '舒適'}
                        </span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 0.5rem 0;">
                        <span style="color: rgba(255,255,255,0.7); font-size: 0.85rem;">降雨機率</span>
                        <span style="color: white; font-size: 0.85rem; font-weight: 500;">
                            {int(today_summary["max_rain_prob"])}%
                        </span>
                    </div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # 一週預報小卡片
        st.markdown('''
        <div class="glass-card" style="margin-top: 1rem; padding: 1.2rem;">
            <div style="font-size: 0.85rem; color: rgba(255,255,255,0.7); margin-bottom: 0.8rem; text-align: center;">
                本週天氣趨勢
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # 顯示一週簡化版（3天）
        try:
            from components.forecast_chart import get_week_forecast_data, parse_week_forecast
            week_api_data = get_week_forecast_data(selected_city)
            if week_api_data:
                week_df = parse_week_forecast(week_api_data, selected_city)
                if week_df is not None and not week_df.empty:
                    daily_data = week_df.groupby('date').agg({
                        'min_temp': 'min',
                        'max_temp': 'max',
                        'weather': 'first',
                        'weekday': 'first'
                    }).reset_index().head(3)
                    
                    for _, day in daily_data.iterrows():
                        weekday = day.get('weekday', '')
                        weather = day.get('weather', '')
                        icon = get_weather_icon(weather)
                        min_t = day.get('min_temp', 0)
                        max_t = day.get('max_temp', 0)
                        
                        st.markdown(f'''
                        <div style="background: rgba(255,255,255,0.05); border-radius: 12px; 
                                    padding: 0.8rem; margin: 0.5rem 0; 
                                    display: flex; justify-content: space-between; align-items: center;">
                            <div style="flex: 1; text-align: left;">
                                <div style="color: rgba(255,255,255,0.9); font-size: 0.85rem;">{weekday}</div>
                            </div>
                            <div style="flex: 1; text-align: center; font-size: 1.3rem;">{icon}</div>
                            <div style="flex: 1; text-align: right;">
                                <span style="color: white; font-weight: 600; font-size: 0.9rem;">{max_t:.0f}°</span>
                                <span style="color: rgba(255,255,255,0.6); font-size: 0.85rem;"> {min_t:.0f}°</span>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
        except:
            pass
    
    # 中央：大型溫度顯示
    with main_col:
        st.markdown(f'''
        <div class="weather-hero" style="height: auto; min-height: 400px; display: flex; 
             flex-direction: column; justify-content: center; margin-top: 1rem;">
            <div class="location" style="font-size: 1rem; margin-bottom: 0.5rem;">
                📍 {selected_city}
            </div>
            <div style="display: flex; align-items: baseline; justify-content: center; margin: 1rem 0;">
                <div class="temperature" style="font-size: 8rem; line-height: 1;">
                    {today_summary["max_temp"]}°
                </div>
                <div style="margin-left: 1.5rem; text-align: left;">
                    <div style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">H {today_summary["max_temp"]}°</div>
                    <div style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">L {today_summary["min_temp"]}°</div>
                </div>
            </div>
            <div class="description" style="font-size: 1.5rem; margin-top: 0.5rem;">
                {today_summary["weather_summary"]}
            </div>
            <div style="font-size: 4rem; margin-top: 1.5rem; opacity: 0.9;">
                {get_weather_icon(today_summary["weather_summary"])}
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    # 右側：其他資訊卡片
    with right_col:
        # 空氣品質卡片（簡化版）
        st.markdown('''
        <div class="glass-card" style="margin-top: 1rem; padding: 1.5rem;">
            <div style="text-align: center;">
                <div style="font-size: 0.9rem; color: rgba(255,255,255,0.7); margin-bottom: 1rem;">空氣品質</div>
                <div style="font-size: 2rem; margin: 1rem 0;">💨</div>
        ''', unsafe_allow_html=True)
        
        try:
            from components.air_quality import get_aqi_data, process_aqi_data
            aqi_data = get_aqi_data()
            if aqi_data:
                aqi_df = process_aqi_data(aqi_data)
                if not aqi_df.empty:
                    city_aqi = aqi_df[aqi_df['縣市'].str.contains(selected_city.replace('台', '臺').replace('臺', '台')[:2])]
                    if not city_aqi.empty:
                        avg_aqi = city_aqi['AQI'].mean()
                        aqi_level = "良好" if avg_aqi <= 50 else "普通" if avg_aqi <= 100 else "不良"
                        st.markdown(f'''
                        <div style="font-size: 1.5rem; color: white; font-weight: 600; margin: 0.5rem 0;">
                            {int(avg_aqi)}
                        </div>
                        <div style="font-size: 0.9rem; color: rgba(255,255,255,0.8);">
                            {aqi_level}
                        </div>
                        ''', unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="color: rgba(255,255,255,0.6); font-size: 0.85rem;">暫無資料</div>', unsafe_allow_html=True)
        except:
            st.markdown('<div style="color: rgba(255,255,255,0.6); font-size: 0.85rem;">載入中...</div>', unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        
        # 警報卡片
        st.markdown('''
        <div class="glass-card" style="margin-top: 1rem; padding: 1.5rem;">
            <div style="text-align: center;">
                <div style="font-size: 0.9rem; color: rgba(255,255,255,0.7); margin-bottom: 1rem;">天氣警報</div>
                <div style="font-size: 2rem; margin: 1rem 0;">⚠️</div>
        ''', unsafe_allow_html=True)
        
        try:
            from components.weather_warnings import get_warnings_data
            warnings = get_warnings_data()
            if warnings and 'records' in warnings:
                records = warnings['records']
                if 'record' in records and len(records['record']) > 0:
                    count = len(records['record'])
                    st.markdown(f'''
                    <div style="font-size: 1.2rem; color: #F5A623; font-weight: 600; margin: 0.5rem 0;">
                        {count} 則警報
                    </div>
                    <div style="font-size: 0.85rem; color: rgba(255,255,255,0.7);">
                        點擊下方查看詳情
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="color: rgba(126, 211, 33, 0.9); font-size: 0.9rem; font-weight: 500;">無特殊警報 ✓</div>', unsafe_allow_html=True)
        except:
            st.markdown('<div style="color: rgba(255,255,255,0.6); font-size: 0.85rem;">載入中...</div>', unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
else:
    st.error('⚠️ 無法載入天氣資料')

# 底部：簡化的資訊
st.markdown('''
<div style="text-align: center; margin-top: 2rem; padding: 1rem;">
    <div style="color: rgba(255,255,255,0.5); font-size: 0.85rem;">
        資料來源：中央氣象署 | Powered by Streamlit
    </div>
</div>
''', unsafe_allow_html=True)
