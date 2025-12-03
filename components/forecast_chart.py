"""
預報圖表元件 - 顯示一週天氣預報
"""
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
from modules.api_client import weather_api
from modules.cache_manager import cache_manager
from utils.helpers import get_weather_icon


def get_week_forecast_data(city: str) -> Optional[Dict[str, Any]]:
    """
    取得一週天氣預報資料
    
    Args:
        city: 縣市名稱
        
    Returns:
        一週預報資料
    """
    # 檢查快取
    cache_key = f"week_forecast_{city}"
    cached_data = cache_manager.get(cache_key)
    
    if cached_data:
        return cached_data
    
    try:
        # 取得 API 資料
        data = weather_api.get_week_forecast(city)
        
        if data:
            # 存入快取
            cache_manager.set(cache_key, data, ttl=3600)  # 1 小時
            return data
        
        return None
        
    except Exception as e:
        print(f"取得一週預報錯誤: {e}")
        return None


def parse_week_forecast(api_data: Dict[str, Any], city: str) -> Optional[pd.DataFrame]:
    """
    解析一週預報資料
    
    Args:
        api_data: API 原始資料
        city: 縣市名稱
        
    Returns:
        包含預報資料的 DataFrame
    """
    try:
        if not api_data or 'records' not in api_data:
            return None
        
        records = api_data['records']
        
        # 處理新的資料結構: records.Locations[0].Location
        locations = []
        if 'Locations' in records:
            # 新版 API 結構
            locations_list = records['Locations']
            if isinstance(locations_list, list) and len(locations_list) > 0:
                first_location_group = locations_list[0]
                if 'Location' in first_location_group:
                    locations = first_location_group['Location']
        elif 'location' in records:
            # 舊版 API 結構
            locations = records['location']
        
        if not locations:
            return None
        
        # 找到指定縣市
        location_data = None
        for loc in locations:
            if loc.get('LocationName') == city or loc.get('locationName') == city:
                location_data = loc
                break
        
        if not location_data:
            return None
        
        weather_elements = location_data.get('WeatherElement', [])
        
        # 建立資料字典
        data_dict = {}
        
        for element in weather_elements:
            element_name = element.get('ElementName')
            time_data = element.get('Time', [])
            
            for time_item in time_data:
                start_time = time_item.get('StartTime')
                end_time = time_item.get('EndTime')
                
                if start_time not in data_dict:
                    data_dict[start_time] = {
                        'start_time': start_time,
                        'end_time': end_time,
                    }
                
                # 根據元素名稱解析資料
                element_values = time_item.get('ElementValue', [])
                
                if element_name == '最低溫度':  # 最低溫
                    for ev in element_values:
                        if 'MinTemperature' in ev:
                            data_dict[start_time]['min_temp'] = float(ev['MinTemperature'])
                            break
                elif element_name == '最高溫度':  # 最高溫
                    for ev in element_values:
                        if 'MaxTemperature' in ev:
                            data_dict[start_time]['max_temp'] = float(ev['MaxTemperature'])
                            break
                elif element_name == '天氣現象':  # 天氣現象
                    for ev in element_values:
                        if 'Weather' in ev:
                            data_dict[start_time]['weather'] = ev['Weather']
                            break
                elif element_name == '降雨機率' or element_name == '12小時降雨機率':  # 降雨機率
                    for ev in element_values:
                        if 'ProbabilityOfPrecipitation' in ev:
                            try:
                                data_dict[start_time]['pop'] = int(ev['ProbabilityOfPrecipitation'])
                            except (ValueError, TypeError):
                                data_dict[start_time]['pop'] = 0
                            break
                elif element_name in ['舒適度', '舒適度指數', '最小舒適度指數', '最大舒適度指數']:  # 舒適度
                    for ev in element_values:
                        if 'MinComfortIndexDescription' in ev:
                            data_dict[start_time]['comfort'] = ev['MinComfortIndexDescription']
                            break
                        elif 'MaxComfortIndexDescription' in ev:
                            data_dict[start_time]['comfort'] = ev['MaxComfortIndexDescription']
                            break
        
        # 轉換為 DataFrame
        df = pd.DataFrame(list(data_dict.values()))
        
        if not df.empty:
            # 移除沒有必要資料的行
            df = df.dropna(subset=['start_time'])
            
            if not df.empty:
                df['date'] = pd.to_datetime(df['start_time']).dt.date
                df['date_str'] = pd.to_datetime(df['start_time']).dt.strftime('%m/%d')
                
                # 使用中文星期
                weekday_map = {
                    'Mon': '週一', 'Tue': '週二', 'Wed': '週三', 
                    'Thu': '週四', 'Fri': '週五', 'Sat': '週六', 'Sun': '週日'
                }
                df['weekday_en'] = pd.to_datetime(df['start_time']).dt.strftime('%a')
                df['weekday'] = df['weekday_en'].map(weekday_map)
        
        return df
        
    except Exception as e:
        print(f"解析一週預報錯誤: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_temperature_chart(df: pd.DataFrame) -> go.Figure:
    """
    建立溫度趨勢圖
    
    Args:
        df: 預報資料 DataFrame
        
    Returns:
        Plotly 圖表物件
    """
    # 按日期分組，取平均溫度
    daily_data = df.groupby('date_str').agg({
        'min_temp': 'min',
        'max_temp': 'max',
        'date': 'first',
        'weekday': 'first'
    }).reset_index()
    
    fig = go.Figure()
    
    # 最高溫線
    fig.add_trace(go.Scatter(
        x=daily_data['date_str'],
        y=daily_data['max_temp'],
        name='最高溫',
        mode='lines+markers+text',
        line=dict(color='#ff6b6b', width=3),
        marker=dict(size=10),
        text=[f"{temp}°C" for temp in daily_data['max_temp']],
        textposition='top center',
        textfont=dict(size=12, color='#ff6b6b')
    ))
    
    # 最低溫線
    fig.add_trace(go.Scatter(
        x=daily_data['date_str'],
        y=daily_data['min_temp'],
        name='最低溫',
        mode='lines+markers+text',
        line=dict(color='#4ecdc4', width=3),
        marker=dict(size=10),
        text=[f"{temp}°C" for temp in daily_data['min_temp']],
        textposition='bottom center',
        textfont=dict(size=12, color='#4ecdc4')
    ))
    
    # 填充區域
    fig.add_trace(go.Scatter(
        x=daily_data['date_str'],
        y=daily_data['max_temp'],
        fill=None,
        mode='lines',
        line=dict(width=0),
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_data['date_str'],
        y=daily_data['min_temp'],
        fill='tonexty',
        mode='lines',
        line=dict(width=0),
        fillcolor='rgba(78, 205, 196, 0.2)',
        showlegend=False
    ))
    
    fig.update_layout(
        title='一週溫度趨勢',
        xaxis_title='日期',
        yaxis_title='溫度 (°C)',
        hovermode='x unified',
        height=400,
        template='plotly_white'
    )
    
    return fig


def create_rain_prob_chart(df: pd.DataFrame) -> go.Figure:
    """
    建立降雨機率圖
    
    Args:
        df: 預報資料 DataFrame
        
    Returns:
        Plotly 圖表物件
    """
    # 按日期分組，取最大降雨機率
    daily_data = df.groupby('date_str').agg({
        'pop': 'max',
        'date': 'first'
    }).reset_index()
    
    # 根據降雨機率設定顏色
    colors = ['#3498db' if pop < 30 else '#f39c12' if pop < 60 else '#e74c3c' 
              for pop in daily_data['pop']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=daily_data['date_str'],
        y=daily_data['pop'],
        name='降雨機率',
        marker=dict(color=colors),
        text=[f"{pop}%" for pop in daily_data['pop']],
        textposition='outside',
    ))
    
    fig.update_layout(
        title='一週降雨機率',
        xaxis_title='日期',
        yaxis_title='降雨機率 (%)',
        yaxis=dict(range=[0, 110]),
        height=400,
        template='plotly_white',
        showlegend=False
    )
    
    return fig


def render_week_forecast(city: str):
    """
    渲染一週天氣預報
    
    Args:
        city: 縣市名稱
    """
    st.subheader(f'📅 {city} 一週天氣預報')
    
    with st.spinner('載入一週預報資料中...'):
        api_data = get_week_forecast_data(city)
    
    if not api_data:
        st.error('❌ 無法取得一週預報資料')
        return
    
    # 解析資料
    df = parse_week_forecast(api_data, city)
    
    if df is None or df.empty:
        st.warning('⚠️ 目前無一週預報資料')
        return
    
    # 顯示圖表
    tab1, tab2, tab3 = st.tabs(['📈 溫度趨勢', '🌧️ 降雨機率', '📋 詳細資料'])
    
    with tab1:
        temp_chart = create_temperature_chart(df)
        st.plotly_chart(temp_chart, use_container_width=True)
    
    with tab2:
        rain_chart = create_rain_prob_chart(df)
        st.plotly_chart(rain_chart, use_container_width=True)
    
    with tab3:
        # 每日摘要卡片
        daily_summary = df.groupby(['date', 'date_str', 'weekday']).agg({
            'min_temp': 'min',
            'max_temp': 'max',
            'pop': 'max',
            'weather': 'first',
            'comfort': 'first'
        }).reset_index()
        
        for _, row in daily_summary.iterrows():
            weather_icon = get_weather_icon(row['weather'])
            
            col1, col2, col3, col4 = st.columns([1, 2, 2, 2])
            
            with col1:
                st.markdown(f"### {weather_icon}")
            
            with col2:
                st.markdown(f"**{row['date_str']} ({row['weekday']})**")
                st.write(row['weather'])
            
            with col3:
                st.write(f"🌡️ {row['min_temp']}°C ~ {row['max_temp']}°C")
                st.write(f"💧 降雨機率: {row['pop']}%")
            
            with col4:
                if row['comfort']:
                    st.write(f"😌 {row['comfort']}")
            
            st.markdown('---')
        
        # 詳細表格
        with st.expander('🔍 查看完整時段資料'):
            display_df = df[['date_str', 'start_time', 'weather', 'min_temp', 'max_temp', 'pop', 'comfort']].copy()
            display_df.columns = ['日期', '時間', '天氣', '最低溫', '最高溫', '降雨機率', '舒適度']
            st.dataframe(display_df, width='stretch', hide_index=True)
