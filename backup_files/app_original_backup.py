"""
台灣氣象資料網站 - 主程式
"""
import streamlit as st
import time
from config.config import PAGE_TITLE, PAGE_ICON, LAYOUT
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
    layout=LAYOUT,
    initial_sidebar_state='expanded'
)

# 主標題
st.title(f'{PAGE_ICON} {PAGE_TITLE}')
st.markdown('---')

# 側邊欄 - 導覽選單
with st.sidebar:
    st.header('� 選單')
    
    # 頁面選擇
    page = st.radio(
        '選擇功能',
        ['🏠 縣市天氣', '🗺️ 全台地圖', '📅 一週預報', '💨 空氣品質', '📊 縣市總覽', '⚠️ 天氣警報'],
        index=0
    )
    
    st.markdown('---')
    
    # 縣市選擇器（在需要的頁面顯示）
    if page in ['🏠 縣市天氣', '📅 一週預報']:
        st.header('� 選擇縣市')
        selected_city = st.selectbox(
            '請選擇縣市',
            TAIWAN_CITIES,
            index=0
        )
    
    st.markdown('---')
    st.info('💡 資料來源：中央氣象署開放資料平台')
    
    # 快取資訊（開發模式）
    with st.expander('🔧 開發資訊'):
        cache_stats = cache_manager.get_stats()
        st.write(f"快取項目數: {cache_stats['valid_entries']}/{cache_stats['total_entries']}")
        st.write(f"快取大小: {cache_stats['size'] / 1024:.2f} KB")
        
        # 顯示快取命中率
        hit_rate = cache_manager.get_cache_hit_rate()
        st.write(f"快取命中率: {hit_rate * 100:.1f}%")
        
        if st.button('清空快取'):
            cache_manager.clear()
            st.success('快取已清空')
            time.sleep(1)
            st.rerun()
        
        # 效能統計
        if st.checkbox('顯示效能統計'):
            performance_monitor.display_stats()

# 根據選擇的頁面顯示不同內容
if page == '🏠 縣市天氣':
    # ===== 縣市天氣頁面 =====
    st.header(f'📍 {selected_city} 天氣資訊')
    
    # 載入天氣資料（使用快取）
    cache_key = f"forecast_{selected_city}"
    cached_data = cache_manager.get(cache_key)
    
    if cached_data:
        parsed_data = cached_data
        st.caption('📦 使用快取資料（載入更快）')
    else:
        try:
            with st.spinner(f'⏳ 載入 {selected_city} 天氣資料中...'):
                start_time = time.time()
                forecast_data = weather_api.get_forecast(selected_city)
                performance_monitor.track('get_forecast', start_time)
            
            if forecast_data:
                # 解析資料
                parsed_data = weather_processor.parse_forecast_data(forecast_data, selected_city)
                
                if parsed_data:
                    # 存入快取
                    cache_manager.set(cache_key, parsed_data)
                else:
                    st.error('❌ 資料解析失敗')
                    parsed_data = None
            else:
                st.error('❌ 無法取得天氣資料，請檢查 API 設定')
                parsed_data = None
        
        except Exception as e:
            show_error_with_details(e, f"載入 {selected_city} 天氣資料")
            parsed_data = None
    
    # 顯示天氣資料
    if parsed_data:
        # 取得今日天氣摘要
        today_summary = weather_processor.get_today_summary(parsed_data)
        
        # 今日天氣卡片
        st.subheader('🌤️ 今日天氣')
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="天氣狀況",
                value=today_summary['weather_summary'],
                delta=None
            )
            st.markdown(f"### {get_weather_icon(today_summary['weather_summary'])}")
        
        with col2:
            st.metric(
                label="溫度範圍",
                value=f"{today_summary['min_temp']}°C ~ {today_summary['max_temp']}°C",
                delta=None
            )
        
        with col3:
            st.metric(
                label="降雨機率",
                value=f"{int(today_summary['max_rain_prob'])}%",
                delta=None
            )
        
        with col4:
            if today_summary['periods'] and today_summary['periods'][0]['comfort']:
                st.metric(
                    label="舒適度",
                    value=today_summary['periods'][0]['comfort'],
                    delta=None
                )
        
        st.markdown('---')
        
        # 三時段天氣預報
        st.subheader('📅 分時段預報')
        
        if len(today_summary['periods']) >= 3:
            cols = st.columns(3)
            
            for idx, period in enumerate(today_summary['periods'][:3]):
                with cols[idx]:
                    time_label = weather_processor.format_time_period(
                        period['start_time'], 
                        period['end_time']
                    )
                    
                    st.markdown(f"### {time_label}")
                    st.markdown(f"## {get_weather_icon(period['weather'])}")
                    st.write(f"**{period['weather']}**")
                    
                    if period['min_temp'] and period['max_temp']:
                        st.write(f"🌡️ {period['min_temp']}°C ~ {period['max_temp']}°C")
                    
                    if period['pop'] is not None:
                        st.write(f"💧 降雨機率: {period['pop']}%")
                    
                    if period['comfort']:
                        st.write(f"😌 {period['comfort']}")
        
        st.markdown('---')
        
        # 詳細預報表格
        st.subheader('📊 詳細預報')
        forecast_df = weather_processor.create_forecast_dataframe(parsed_data)
        st.dataframe(forecast_df, width='stretch', hide_index=True)
        
        # 原始資料查看（開發階段）
        with st.expander('🔍 查看原始資料'):
            st.json(parsed_data)

elif page == '🗺️ 全台地圖':
    # ===== 全台天氣地圖頁面 =====
    from components.map_view import render_weather_map
    render_weather_map()

elif page == '📅 一週預報':
    # ===== 一週天氣預報頁面 =====
    from components.forecast_chart import render_week_forecast
    render_week_forecast(selected_city)

elif page == '💨 空氣品質':
    # ===== 空氣品質監測頁面 =====
    from components.air_quality import render_aqi_overview
    render_aqi_overview()

elif page == '📊 縣市總覽':
    # ===== 縣市預報總覽頁面 =====
    from components.weather_overview import render_overview_page
    render_overview_page()

elif page == '⚠️ 天氣警報':
    # ===== 天氣警特報頁面 =====
    from components.weather_warnings import render_warnings_page
    render_warnings_page()

# 頁尾
st.markdown('---')
st.caption('© 2025 台灣氣象資料網站 | Powered by Streamlit')
