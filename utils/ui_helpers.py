"""
載入指示器元件 - 提供統一的載入動畫和錯誤處理
"""
import streamlit as st
import time
from typing import Callable, Any, Optional
from functools import wraps


def with_loading_indicator(
    message: str = "載入中...",
    error_message: str = "載入失敗",
    retry_enabled: bool = True,
    max_retries: int = 3
):
    """
    裝飾器：為函數加入載入指示器和錯誤處理
    
    Args:
        message: 載入訊息
        error_message: 錯誤訊息
        retry_enabled: 是否啟用重試機制
        max_retries: 最大重試次數
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_retries):
                try:
                    with st.spinner(f'{message} {"" if attempt == 0 else f"(重試 {attempt}/{max_retries})"}'):
                        result = func(*args, **kwargs)
                    return result
                    
                except Exception as e:
                    if attempt < max_retries - 1 and retry_enabled:
                        time.sleep(1 * (attempt + 1))  # 指數退避
                        continue
                    else:
                        st.error(f'{error_message}: {str(e)}')
                        if retry_enabled:
                            if st.button('🔄 重試', key=f'retry_{func.__name__}_{time.time()}'):
                                st.rerun()
                        return None
            
            return None
        
        return wrapper
    return decorator


def show_loading_progress(total: int, current: int, text: str = "處理中"):
    """
    顯示進度條
    
    Args:
        total: 總數
        current: 當前進度
        text: 顯示文字
    """
    progress = current / total if total > 0 else 0
    st.progress(progress, text=f'{text}: {current}/{total} ({progress*100:.1f}%)')


def show_error_with_details(error: Exception, context: str = ""):
    """
    顯示友善的錯誤訊息
    
    Args:
        error: 錯誤物件
        context: 錯誤情境說明
    """
    st.error(f'❌ 發生錯誤{f": {context}" if context else ""}')
    
    error_type = type(error).__name__
    error_msg = str(error)
    
    with st.expander('📋 錯誤詳情'):
        st.code(f'{error_type}: {error_msg}', language='text')
        
        # 根據錯誤類型提供建議
        suggestions = get_error_suggestions(error)
        if suggestions:
            st.markdown('**💡 可能的解決方案:**')
            for suggestion in suggestions:
                st.markdown(f'- {suggestion}')


def get_error_suggestions(error: Exception) -> list:
    """
    根據錯誤類型提供解決建議
    
    Args:
        error: 錯誤物件
        
    Returns:
        建議列表
    """
    error_type = type(error).__name__
    error_msg = str(error).lower()
    
    suggestions = []
    
    if 'timeout' in error_msg or 'timed out' in error_msg:
        suggestions.append('網路連線逾時，請檢查網路連線')
        suggestions.append('稍後再試一次')
    
    elif 'connection' in error_msg or 'network' in error_msg:
        suggestions.append('無法連接到伺服器，請檢查網路連線')
        suggestions.append('確認 API 伺服器是否正常運作')
    
    elif 'api' in error_msg and 'key' in error_msg:
        suggestions.append('API 金鑰可能無效或已過期')
        suggestions.append('請檢查 .env 檔案中的 API 金鑰設定')
    
    elif '404' in error_msg:
        suggestions.append('請求的資源不存在')
        suggestions.append('請檢查 API 端點是否正確')
    
    elif '500' in error_msg or '502' in error_msg or '503' in error_msg:
        suggestions.append('伺服器暫時無法處理請求')
        suggestions.append('請稍後再試')
    
    elif 'json' in error_msg or 'decode' in error_msg:
        suggestions.append('資料格式錯誤')
        suggestions.append('API 回應可能不是有效的 JSON 格式')
    
    else:
        suggestions.append('請重新載入頁面')
        suggestions.append('如果問題持續，請聯繫系統管理員')
    
    return suggestions


def show_success_message(message: str, duration: int = 3):
    """
    顯示成功訊息
    
    Args:
        message: 成功訊息
        duration: 顯示時間（秒）
    """
    success_placeholder = st.empty()
    success_placeholder.success(f'✅ {message}')
    time.sleep(duration)
    success_placeholder.empty()


def rate_limiter(func: Callable, min_interval: float = 1.0) -> Callable:
    """
    速率限制裝飾器
    
    Args:
        func: 要限制的函數
        min_interval: 最小間隔時間（秒）
    """
    last_called = {'time': 0}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        current_time = time.time()
        elapsed = current_time - last_called['time']
        
        if elapsed < min_interval:
            wait_time = min_interval - elapsed
            time.sleep(wait_time)
        
        result = func(*args, **kwargs)
        last_called['time'] = time.time()
        return result
    
    return wrapper


class PerformanceMonitor:
    """效能監控器"""
    
    def __init__(self):
        self.metrics = {}
    
    def track(self, name: str, start_time: float):
        """
        追蹤效能指標
        
        Args:
            name: 指標名稱
            start_time: 開始時間
        """
        elapsed = time.time() - start_time
        
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append(elapsed)
    
    def get_stats(self, name: str) -> dict:
        """
        取得效能統計
        
        Args:
            name: 指標名稱
            
        Returns:
            統計資訊字典
        """
        if name not in self.metrics or not self.metrics[name]:
            return {}
        
        times = self.metrics[name]
        return {
            'count': len(times),
            'avg': sum(times) / len(times),
            'min': min(times),
            'max': max(times),
            'total': sum(times)
        }
    
    def display_stats(self):
        """顯示所有效能統計"""
        if not self.metrics:
            st.info('📊 尚無效能資料')
            return
        
        st.markdown('### ⚡ 效能統計')
        
        for name, times in self.metrics.items():
            stats = self.get_stats(name)
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(f'{name} - 平均', f"{stats['avg']:.3f}s")
            with col2:
                st.metric('最快', f"{stats['min']:.3f}s")
            with col3:
                st.metric('最慢', f"{stats['max']:.3f}s")
            with col4:
                st.metric('次數', stats['count'])


# 全域效能監控器
performance_monitor = PerformanceMonitor()
