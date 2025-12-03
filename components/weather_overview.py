"""
縣市總覽元件 - 顯示所有縣市預報總覽
"""
import streamlit as st
import pandas as pd
from typing import Dict, List, Any
from modules.api_client import weather_api
from modules.data_processor import weather_processor
from modules.cache_manager import cache_manager
from utils.constants import TAIWAN_CITIES
from utils.helpers import get_weather_icon


def get_all_cities_forecast() -> Dict[str, Any]:
    """
    取得所有縣市的預報資料
    
    Returns:
        所有縣市預報資料字典
    """
    # 檢查快取
    cache_key = "all_cities_forecast"
    cached_data = cache_manager.get(cache_key)
    
    if cached_data:
        return cached_data
    
    all_data = {}
    
    with st.spinner('載入所有縣市預報資料中...'):
        progress_bar = st.progress(0)
        total = len(TAIWAN_CITIES)
        
        for idx, city in enumerate(TAIWAN_CITIES):
            try:
                # 檢查個別快取
                city_cache_key = f"forecast_{city}"
                city_data = cache_manager.get(city_cache_key)
                
                if not city_data:
                    forecast_data = weather_api.get_forecast(city)
                    if forecast_data:
                        city_data = weather_processor.parse_forecast_data(forecast_data, city)
                        if city_data:
                            cache_manager.set(city_cache_key, city_data)
                
                if city_data:
                    all_data[city] = city_data
                    
            except Exception as e:
                print(f"取得 {city} 資料錯誤: {e}")
            
            progress_bar.progress((idx + 1) / total)
        
        progress_bar.empty()
    
    # 存入快取
    if all_data:
        cache_manager.set(cache_key, all_data, ttl=1800)  # 30 分鐘
    
    return all_data


def create_overview_dataframe(all_data: Dict[str, Any]) -> pd.DataFrame:
    """
    建立總覽 DataFrame
    
    Args:
        all_data: 所有縣市資料
        
    Returns:
        總覽 DataFrame
    """
    overview_data = []
    
    for city, data in all_data.items():
        if not data or 'periods' not in data or not data['periods']:
            continue
        
        # 取得當前時段
        current = data['periods'][0]
        
        # 計算今日溫度範圍
        all_temps = []
        for period in data['periods'][:3]:  # 今日三個時段
            if period.get('min_temp'):
                all_temps.append(period['min_temp'])
            if period.get('max_temp'):
                all_temps.append(period['max_temp'])
        
        # 計算最大降雨機率
        rain_probs = [p.get('pop', 0) for p in data['periods'][:3] if p.get('pop') is not None]
        
        overview_data.append({
            '縣市': city,
            '天氣': current.get('weather', 'N/A'),
            '圖示': get_weather_icon(current.get('weather', '')),
            '最低溫': min(all_temps) if all_temps else None,
            '最高溫': max(all_temps) if all_temps else None,
            '降雨機率': max(rain_probs) if rain_probs else 0,
            '舒適度': current.get('comfort', 'N/A')
        })
    
    df = pd.DataFrame(overview_data)
    return df


def render_overview_page():
    """渲染縣市預報總覽頁面"""
    st.subheader('📊 全台縣市預報總覽')
    
    # 取得所有縣市資料
    all_data = get_all_cities_forecast()
    
    if not all_data:
        st.error('❌ 無法載入縣市資料')
        return
    
    # 建立總覽表格
    df = create_overview_dataframe(all_data)
    
    if df.empty:
        st.warning('⚠️ 目前無可用資料')
        return
    
    # 統計資訊
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="縣市總數",
            value=len(df),
            delta=None
        )
    
    with col2:
        avg_max_temp = df['最高溫'].mean()
        st.metric(
            label="平均最高溫",
            value=f"{avg_max_temp:.1f}°C",
            delta=None
        )
    
    with col3:
        avg_min_temp = df['最低溫'].mean()
        st.metric(
            label="平均最低溫",
            value=f"{avg_min_temp:.1f}°C",
            delta=None
        )
    
    with col4:
        avg_rain = df['降雨機率'].mean()
        st.metric(
            label="平均降雨機率",
            value=f"{avg_rain:.0f}%",
            delta=None
        )
    
    st.markdown('---')
    
    # 搜尋與篩選
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_text = st.text_input('🔍 搜尋縣市', placeholder='輸入縣市名稱...')
    
    with col2:
        sort_by = st.selectbox(
            '排序方式',
            ['縣市', '最高溫', '最低溫', '降雨機率'],
            index=0
        )
    
    with col3:
        sort_order = st.selectbox(
            '排序順序',
            ['遞增 ↑', '遞減 ↓'],
            index=0
        )
    
    # 應用篩選
    filtered_df = df.copy()
    
    if search_text:
        filtered_df = filtered_df[filtered_df['縣市'].str.contains(search_text)]
    
    # 應用排序
    ascending = sort_order == '遞增 ↑'
    filtered_df = filtered_df.sort_values(sort_by, ascending=ascending)
    
    # 顯示方式選擇
    view_mode = st.radio(
        '顯示方式',
        ['📋 表格檢視', '🎴 卡片檢視'],
        horizontal=True
    )
    
    st.markdown('---')
    
    if view_mode == '📋 表格檢視':
        # 表格顯示
        display_df = filtered_df.copy()
        display_df['溫度範圍'] = display_df.apply(
            lambda x: f"{x['最低溫']}°C ~ {x['最高溫']}°C", axis=1
        )
        display_df['降雨機率'] = display_df['降雨機率'].apply(lambda x: f"{x}%")
        
        st.dataframe(
            display_df[['圖示', '縣市', '天氣', '溫度範圍', '降雨機率', '舒適度']],
            width='stretch',
            hide_index=True
        )
        
        # 下載按鈕
        csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 下載 CSV",
            data=csv,
            file_name="weather_overview.csv",
            mime="text/csv",
        )
        
    else:
        # 卡片顯示
        cols_per_row = 3
        rows = [filtered_df.iloc[i:i+cols_per_row] for i in range(0, len(filtered_df), cols_per_row)]
        
        for row_df in rows:
            cols = st.columns(cols_per_row)
            
            for idx, (_, city_data) in enumerate(row_df.iterrows()):
                with cols[idx]:
                    # 根據降雨機率決定邊框顏色
                    rain_prob = city_data['降雨機率']
                    if rain_prob >= 70:
                        border_color = '#3498db'  # 藍色
                    elif rain_prob >= 40:
                        border_color = '#f39c12'  # 橙色
                    else:
                        border_color = '#2ecc71'  # 綠色
                    
                    st.markdown(f"""
                    <div style="
                        padding: 15px;
                        border-radius: 10px;
                        border: 2px solid {border_color};
                        background-color: rgba(255, 255, 255, 0.05);
                        margin: 10px 0;
                        text-align: center;
                    ">
                        <h3 style="margin: 0;">{city_data['圖示']}</h3>
                        <h4 style="margin: 10px 0;">{city_data['縣市']}</h4>
                        <p style="margin: 5px 0; font-size: 14px;">{city_data['天氣']}</p>
                        <p style="margin: 5px 0; font-size: 18px; font-weight: bold;">
                            {city_data['最低溫']}°C ~ {city_data['最高溫']}°C
                        </p>
                        <p style="margin: 5px 0; color: {border_color}; font-weight: bold;">
                            💧 {city_data['降雨機率']}%
                        </p>
                        <p style="margin: 5px 0; font-size: 12px; color: #888;">
                            {city_data['舒適度']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # 天氣分布統計
    st.markdown('---')
    st.subheader('📈 天氣分布統計')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 天氣狀況統計
        weather_counts = filtered_df['天氣'].value_counts()
        st.markdown('#### 天氣狀況分布')
        for weather, count in weather_counts.items():
            icon = get_weather_icon(weather)
            percentage = (count / len(filtered_df)) * 100
            st.write(f"{icon} {weather}: {count} 個縣市 ({percentage:.1f}%)")
    
    with col2:
        # 溫度分布
        st.markdown('#### 溫度分布')
        temp_ranges = {
            '寒冷 (<15°C)': len(filtered_df[filtered_df['最高溫'] < 15]),
            '涼爽 (15-20°C)': len(filtered_df[(filtered_df['最高溫'] >= 15) & (filtered_df['最高溫'] < 20)]),
            '舒適 (20-25°C)': len(filtered_df[(filtered_df['最高溫'] >= 20) & (filtered_df['最高溫'] < 25)]),
            '溫暖 (25-30°C)': len(filtered_df[(filtered_df['最高溫'] >= 25) & (filtered_df['最高溫'] < 30)]),
            '炎熱 (≥30°C)': len(filtered_df[filtered_df['最高溫'] >= 30]),
        }
        
        for range_name, count in temp_ranges.items():
            if count > 0:
                percentage = (count / len(filtered_df)) * 100
                st.write(f"{range_name}: {count} 個縣市 ({percentage:.1f}%)")
