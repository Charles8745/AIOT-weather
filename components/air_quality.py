"""
空氣品質元件 - 顯示空氣品質監測資料
"""
import streamlit as st
import pandas as pd
import requests
from typing import Dict, List, Any, Optional
from utils.helpers import get_aqi_info
from modules.cache_manager import cache_manager


def get_aqi_data() -> Optional[List[Dict[str, Any]]]:
    """
    取得空氣品質資料
    
    Returns:
        空氣品質資料列表
    """
    # 檢查快取
    cache_key = "aqi_data"
    cached_data = cache_manager.get(cache_key)
    
    if cached_data:
        return cached_data
    
    try:
        # 使用環保署開放資料平台 API
        url = "https://data.moenv.gov.tw/api/v2/aqx_p_432"
        
        from config.config import MOENV_API_KEY
        
        if not MOENV_API_KEY:
            print("⚠️ 未設定環保署 API key，請在 .env 檔案中設定 MOENV_API_KEY")
            return None
        
        params = {
            'limit': 1000,
            'api_key': MOENV_API_KEY,
            'format': 'json'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # 檢查多種可能的資料結構
        records = None
        if isinstance(data, dict):
            if 'records' in data:
                records = data['records']
            elif 'data' in data:
                records = data['data']
            elif 'result' in data:
                records = data['result']
        elif isinstance(data, list):
            records = data
        
        if records:
            # 存入快取
            cache_manager.set(cache_key, records, ttl=1800)  # 30 分鐘
            return records
        
        return None
        
    except Exception as e:
        print(f"取得空氣品質資料錯誤: {e}")
        import traceback
        traceback.print_exc()
        return None


def process_aqi_data(aqi_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    處理空氣品質資料
    
    Args:
        aqi_data: 原始 AQI 資料
        
    Returns:
        處理後的 DataFrame
    """
    if not aqi_data:
        return pd.DataFrame()
    
    processed_data = []
    
    for record in aqi_data:
        try:
            aqi_value = record.get('aqi', '')
            
            # 跳過空值
            if not aqi_value or aqi_value == '':
                continue
            
            aqi_int = int(aqi_value)
            aqi_info = get_aqi_info(aqi_int)
            
            processed_data.append({
                '測站': record.get('sitename', 'N/A'),
                '縣市': record.get('county', 'N/A'),
                'AQI': aqi_int,
                '狀態': aqi_info['label'],
                'PM2.5': record.get('pm2.5', 'N/A'),
                'PM10': record.get('pm10', 'N/A'),
                '發布時間': record.get('publishtime', 'N/A'),
                '顏色': aqi_info['color']
            })
        except (ValueError, TypeError):
            continue
    
    df = pd.DataFrame(processed_data)
    
    # 按 AQI 值排序
    if not df.empty:
        df = df.sort_values('AQI', ascending=False)
    
    return df


def render_aqi_card(county: str, aqi_df: pd.DataFrame):
    """
    渲染單一縣市的 AQI 卡片
    
    Args:
        county: 縣市名稱
        aqi_df: 空氣品質 DataFrame
    """
    county_data = aqi_df[aqi_df['縣市'] == county]
    
    if county_data.empty:
        st.info(f'📍 {county} 目前無空氣品質監測資料')
        return
    
    # 計算平均 AQI
    avg_aqi = int(county_data['AQI'].mean())
    aqi_info = get_aqi_info(avg_aqi)
    
    # 顯示卡片
    st.markdown(f"""
    <div style="
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid {aqi_info['color']};
        background-color: rgba(255, 255, 255, 0.05);
        margin: 10px 0;
    ">
        <h3 style="margin: 0 0 10px 0;">📍 {county}</h3>
        <div style="display: flex; align-items: center; gap: 20px;">
            <div style="
                font-size: 48px;
                font-weight: bold;
                color: {aqi_info['color']};
            ">{avg_aqi}</div>
            <div>
                <p style="margin: 5px 0; font-size: 18px;"><b>{aqi_info['label']}</b></p>
                <p style="margin: 5px 0; color: #888;">監測站數: {len(county_data)}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 顯示各測站詳細資料
    with st.expander(f'🔍 查看 {county} 各測站詳細資料'):
        display_df = county_data[['測站', 'AQI', '狀態', 'PM2.5', 'PM10', '發布時間']].copy()
        st.dataframe(display_df, width='stretch', hide_index=True)


def render_aqi_overview():
    """渲染空氣品質總覽頁面"""
    st.subheader('💨 空氣品質監測')
    
    with st.spinner('載入空氣品質資料中...'):
        aqi_data = get_aqi_data()
    
    if not aqi_data:
        st.error('❌ 無法取得空氣品質資料')
        return
    
    # 處理資料
    aqi_df = process_aqi_data(aqi_data)
    
    if aqi_df.empty:
        st.warning('⚠️ 目前無有效的空氣品質資料')
        return
    
    # 統計資訊
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="監測站總數",
            value=len(aqi_df),
            delta=None
        )
    
    with col2:
        avg_aqi = int(aqi_df['AQI'].mean())
        aqi_info = get_aqi_info(avg_aqi)
        st.metric(
            label="全國平均 AQI",
            value=avg_aqi,
            delta=aqi_info['label']
        )
    
    with col3:
        max_aqi = int(aqi_df['AQI'].max())
        max_station = aqi_df.loc[aqi_df['AQI'].idxmax(), '測站']
        st.metric(
            label="最高 AQI",
            value=max_aqi,
            delta=max_station
        )
    
    with col4:
        min_aqi = int(aqi_df['AQI'].min())
        min_station = aqi_df.loc[aqi_df['AQI'].idxmin(), '測站']
        st.metric(
            label="最低 AQI",
            value=min_aqi,
            delta=min_station
        )
    
    st.markdown('---')
    
    # AQI 等級說明
    st.markdown('#### 📊 AQI 指標說明')
    
    cols = st.columns(6)
    aqi_levels = [
        ('良好', '0-50', '#00E400'),
        ('普通', '51-100', '#FFFF00'),
        ('對敏感族群不健康', '101-150', '#FF7E00'),
        ('不健康', '151-200', '#FF0000'),
        ('非常不健康', '201-300', '#8F3F97'),
        ('危害', '301+', '#7E0023'),
    ]
    
    for idx, (label, range_text, color) in enumerate(aqi_levels):
        with cols[idx]:
            st.markdown(f"""
            <div style="
                text-align: center;
                padding: 10px;
                border-radius: 5px;
                background-color: {color};
                color: white;
                font-weight: bold;
            ">
                {label}<br>{range_text}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('---')
    
    # 選擇縣市查看
    from utils.constants import TAIWAN_CITIES
    
    tab1, tab2 = st.tabs(['📍 依縣市查看', '📊 完整列表'])
    
    with tab1:
        selected_county = st.selectbox(
            '選擇縣市',
            ['全部'] + sorted(aqi_df['縣市'].unique().tolist()),
            key='aqi_county_select'
        )
        
        if selected_county == '全部':
            # 顯示所有縣市
            counties = sorted(aqi_df['縣市'].unique())
            for county in counties:
                render_aqi_card(county, aqi_df)
        else:
            render_aqi_card(selected_county, aqi_df)
    
    with tab2:
        # 顯示完整表格
        st.dataframe(
            aqi_df[['縣市', '測站', 'AQI', '狀態', 'PM2.5', 'PM10', '發布時間']],
            width='stretch',
            hide_index=True
        )
        
        # 下載按鈕
        csv = aqi_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 下載 CSV",
            data=csv,
            file_name="aqi_data.csv",
            mime="text/csv",
        )
