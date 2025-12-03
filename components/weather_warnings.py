"""
天氣警特報元件 - 顯示天氣警報資訊
"""
import streamlit as st
import pandas as pd
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
from modules.cache_manager import cache_manager
from config.config import CWA_API_KEY, API_ENDPOINTS


def get_warnings_data() -> Optional[Dict[str, Any]]:
    """
    取得天氣警特報資料
    
    Returns:
        警特報資料
    """
    # 檢查快取
    cache_key = "warnings_data"
    cached_data = cache_manager.get(cache_key)
    
    if cached_data:
        return cached_data
    
    try:
        url = API_ENDPOINTS['warning']
        params = {'Authorization': CWA_API_KEY}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data and data.get('success') == 'true':
            # 存入快取（警報變動較快，設定較短的 TTL）
            cache_manager.set(cache_key, data, ttl=600)  # 10 分鐘
            return data
        
        return None
        
    except Exception as e:
        print(f"取得天氣警特報資料錯誤: {e}")
        import traceback
        traceback.print_exc()
        return None


def process_warnings_data(warnings_data: Dict[str, Any]) -> pd.DataFrame:
    """
    處理天氣警特報資料
    
    Args:
        warnings_data: 原始警特報資料
        
    Returns:
        處理後的 DataFrame
    """
    if not warnings_data or 'records' not in warnings_data:
        return pd.DataFrame()
    
    records = warnings_data['records']
    
    if 'location' not in records:
        return pd.DataFrame()
    
    locations = records['location']
    
    processed_data = []
    
    for location in locations:
        location_name = location.get('locationName', 'N/A')
        geocode = location.get('geocode', '')
        
        # 取得警報資訊
        hazard_conditions = location.get('hazardConditions', {})
        hazards = hazard_conditions.get('hazards', [])
        
        for hazard in hazards:
            info = hazard.get('info', {})
            valid_time = hazard.get('validTime', {})
            
            phenomena = info.get('phenomena', 'N/A')
            significance = info.get('significance', 'N/A')
            start_time = valid_time.get('startTime', 'N/A')
            end_time = valid_time.get('endTime', 'N/A')
            
            # 判斷警報等級（根據 phenomena 和 significance）
            severity = get_warning_severity(phenomena, significance)
            
            processed_data.append({
                '縣市': location_name,
                '警報類型': phenomena,
                '等級': significance,
                '嚴重程度': severity,
                '開始時間': start_time,
                '結束時間': end_time,
                '顏色': get_warning_color(severity)
            })
    
    df = pd.DataFrame(processed_data)
    
    # 按嚴重程度排序
    if not df.empty:
        severity_order = {'危險': 0, '警告': 1, '注意': 2, '特報': 3}
        df['sort_order'] = df['嚴重程度'].map(severity_order)
        df = df.sort_values(['sort_order', '縣市']).drop('sort_order', axis=1)
    
    return df


def get_warning_severity(phenomena: str, significance: str) -> str:
    """
    判斷警報嚴重程度
    
    Args:
        phenomena: 天氣現象
        significance: 警報等級
        
    Returns:
        嚴重程度
    """
    # 根據不同的警報類型判斷嚴重程度
    if '颱風' in phenomena:
        if '警報' in significance:
            return '危險'
        elif '特報' in significance:
            return '警告'
    elif '豪雨' in phenomena or '大雨' in phenomena:
        if '豪雨' in phenomena:
            return '警告'
        else:
            return '注意'
    elif '強風' in phenomena:
        return '注意'
    elif '低溫' in phenomena or '高溫' in phenomena:
        return '注意'
    else:
        return '特報'


def get_warning_color(severity: str) -> str:
    """
    取得警報顏色
    
    Args:
        severity: 嚴重程度
        
    Returns:
        顏色代碼
    """
    color_map = {
        '危險': '#FF0000',    # 紅色
        '警告': '#FF7E00',    # 橙色
        '注意': '#FFFF00',    # 黃色
        '特報': '#00BFFF'     # 藍色
    }
    return color_map.get(severity, '#808080')


def get_warning_icon(phenomena: str) -> str:
    """
    取得警報圖示
    
    Args:
        phenomena: 天氣現象
        
    Returns:
        Emoji 圖示
    """
    if '颱風' in phenomena:
        return '🌀'
    elif '豪雨' in phenomena or '大雨' in phenomena:
        return '🌧️'
    elif '強風' in phenomena:
        return '💨'
    elif '低溫' in phenomena:
        return '❄️'
    elif '高溫' in phenomena:
        return '🌡️'
    elif '雷雨' in phenomena:
        return '⛈️'
    else:
        return '⚠️'


def render_warning_card(warning: pd.Series):
    """
    渲染單一警報卡片
    
    Args:
        warning: 警報資料
    """
    icon = get_warning_icon(warning['警報類型'])
    color = warning['顏色']
    
    st.markdown(f"""
    <div style="
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid {color};
        background-color: rgba(255, 255, 255, 0.05);
        margin: 10px 0;
    ">
        <div style="display: flex; align-items: center; gap: 15px;">
            <div style="font-size: 36px;">{icon}</div>
            <div style="flex: 1;">
                <h3 style="margin: 0 0 5px 0;">{warning['縣市']}</h3>
                <p style="margin: 5px 0; font-size: 18px; font-weight: bold; color: {color};">
                    {warning['警報類型']} - {warning['等級']}
                </p>
                <p style="margin: 5px 0; color: #888; font-size: 14px;">
                    ⏰ {warning['開始時間']} ~ {warning['結束時間']}
                </p>
            </div>
            <div style="
                padding: 8px 16px;
                border-radius: 5px;
                background-color: {color};
                color: white;
                font-weight: bold;
            ">
                {warning['嚴重程度']}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def display_warnings_list(warnings_data: Dict[str, Any]):
    """
    顯示警報列表（用於一頁式設計）
    
    Args:
        warnings_data: 警報資料
    """
    # 處理資料
    warnings_df = process_warnings_data(warnings_data)
    
    if warnings_df.empty:
        st.info('✅ 目前無天氣警特報')
        return
    
    # 顯示警報卡片
    for _, warning in warnings_df.iterrows():
        render_warning_card(warning)


def render_warnings_page():
    """渲染天氣警特報頁面"""
    st.subheader('⚠️ 天氣警特報')
    
    with st.spinner('載入天氣警特報資料中...'):
        warnings_data = get_warnings_data()
    
    if not warnings_data:
        st.info('✅ 目前無天氣警特報')
        st.markdown("""
        ---
        ### 📋 警報類型說明
        
        本系統顯示中央氣象署發布的各類天氣警特報，包括：
        
        - 🌀 **颱風警報**: 颱風接近或影響台灣時發布
        - 🌧️ **豪雨特報**: 短時間內累積雨量達豪雨標準
        - 💨 **強風特報**: 平均風力達6級以上或陣風達8級以上
        - ❄️ **低溫特報**: 氣溫明顯偏低可能造成影響
        - 🌡️ **高溫特報**: 氣溫明顯偏高可能造成影響
        - ⛈️ **雷雨特報**: 可能發生劇烈天氣現象
        
        ### 🎨 警報等級顏色
        
        - 🔴 **危險**: 颱風警報等最嚴重警報
        - 🟠 **警告**: 豪雨特報等需特別注意
        - 🟡 **注意**: 強風、大雨等一般性警報
        - 🔵 **特報**: 其他天氣特報資訊
        """)
        return
    
    # 處理資料
    warnings_df = process_warnings_data(warnings_data)
    
    if warnings_df.empty:
        st.info('✅ 目前無天氣警特報')
        return
    
    # 統計資訊
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="警報總數",
            value=len(warnings_df),
            delta=None
        )
    
    with col2:
        affected_cities = warnings_df['縣市'].nunique()
        st.metric(
            label="影響縣市",
            value=affected_cities,
            delta=None
        )
    
    with col3:
        warning_types = warnings_df['警報類型'].nunique()
        st.metric(
            label="警報類型",
            value=warning_types,
            delta=None
        )
    
    with col4:
        severity_counts = warnings_df['嚴重程度'].value_counts()
        highest_severity = severity_counts.index[0] if len(severity_counts) > 0 else 'N/A'
        st.metric(
            label="最高等級",
            value=highest_severity,
            delta=None
        )
    
    st.markdown('---')
    
    # 顯示警報
    tab1, tab2, tab3 = st.tabs(['🗺️ 依縣市查看', '📊 依類型查看', '📋 完整列表'])
    
    with tab1:
        # 依縣市查看
        selected_city = st.selectbox(
            '選擇縣市',
            ['全部'] + sorted(warnings_df['縣市'].unique().tolist()),
            key='warning_city_select'
        )
        
        if selected_city == '全部':
            for _, warning in warnings_df.iterrows():
                render_warning_card(warning)
        else:
            city_warnings = warnings_df[warnings_df['縣市'] == selected_city]
            
            if city_warnings.empty:
                st.info(f'{selected_city} 目前無警特報')
            else:
                for _, warning in city_warnings.iterrows():
                    render_warning_card(warning)
    
    with tab2:
        # 依類型查看
        warning_types_list = sorted(warnings_df['警報類型'].unique().tolist())
        
        for warning_type in warning_types_list:
            type_warnings = warnings_df[warnings_df['警報類型'] == warning_type]
            icon = get_warning_icon(warning_type)
            
            with st.expander(f'{icon} {warning_type} ({len(type_warnings)} 個縣市)', expanded=True):
                affected_cities = ', '.join(sorted(type_warnings['縣市'].tolist()))
                st.write(f"**影響縣市**: {affected_cities}")
                
                st.dataframe(
                    type_warnings[['縣市', '等級', '嚴重程度', '開始時間', '結束時間']],
                    width='stretch',
                    hide_index=True
                )
    
    with tab3:
        # 完整表格
        st.dataframe(
            warnings_df[['縣市', '警報類型', '等級', '嚴重程度', '開始時間', '結束時間']],
            width='stretch',
            hide_index=True
        )
        
        # 下載按鈕
        csv = warnings_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 下載 CSV",
            data=csv,
            file_name=f"weather_warnings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )
    
    # 更新時間
    st.markdown('---')
    st.caption(f'📅 資料更新時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    st.caption('💡 警特報資料每 10 分鐘自動更新')
