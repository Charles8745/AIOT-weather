"""
API 請求限速器 - 控制 API 請求頻率
"""
import time
from typing import Dict, Callable, Any
from functools import wraps
import threading


class RateLimiter:
    """API 請求限速器"""
    
    def __init__(self, calls_per_minute: int = 60):
        """
        初始化限速器
        
        Args:
            calls_per_minute: 每分鐘允許的請求次數
        """
        self.calls_per_minute = calls_per_minute
        self.min_interval = 60.0 / calls_per_minute
        self.last_calls: Dict[str, float] = {}
        self.lock = threading.Lock()
    
    def wait_if_needed(self, key: str) -> float:
        """
        如果需要，等待直到可以發出請求
        
        Args:
            key: 請求識別鍵
            
        Returns:
            等待時間（秒）
        """
        with self.lock:
            current_time = time.time()
            
            if key in self.last_calls:
                elapsed = current_time - self.last_calls[key]
                
                if elapsed < self.min_interval:
                    wait_time = self.min_interval - elapsed
                    time.sleep(wait_time)
                    self.last_calls[key] = time.time()
                    return wait_time
            
            self.last_calls[key] = current_time
            return 0.0
    
    def __call__(self, func: Callable) -> Callable:
        """
        裝飾器：為函數加入限速功能
        
        Args:
            func: 要限速的函數
            
        Returns:
            包裝後的函數
        """
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 使用函數名稱作為鍵
            key = func.__name__
            
            # 等待（如果需要）
            wait_time = self.wait_if_needed(key)
            
            if wait_time > 0:
                print(f"⏳ 請求限速：等待 {wait_time:.2f} 秒")
            
            # 執行函數
            return func(*args, **kwargs)
        
        return wrapper


# 全域限速器實例
# 中央氣象署 API 限制建議每分鐘不超過 60 次
api_rate_limiter = RateLimiter(calls_per_minute=60)


def rate_limited_request(func: Callable) -> Callable:
    """
    便利裝飾器：為 API 請求加入限速
    
    Args:
        func: API 請求函數
        
    Returns:
        包裝後的函數
    """
    return api_rate_limiter(func)
