"""
快取管理模組 - 管理 API 資料快取
"""
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class CacheManager:
    """快取管理器"""
    
    def __init__(self, default_ttl: int = 1800):
        """
        初始化快取管理器
        
        Args:
            default_ttl: 預設快取過期時間（秒），預設 30 分鐘
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """
        從快取中取得資料
        
        Args:
            key: 快取鍵值
            
        Returns:
            快取的資料，如果不存在或已過期則回傳 None
        """
        if key not in self._cache:
            self._track_miss()
            return None
        
        cache_entry = self._cache[key]
        
        # 檢查是否過期
        if time.time() > cache_entry['expires_at']:
            del self._cache[key]
            self._track_miss()
            return None
        
        self._track_hit()
        return cache_entry['data']
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        """
        將資料存入快取
        
        Args:
            key: 快取鍵值
            data: 要快取的資料
            ttl: 快取過期時間（秒），如果為 None 則使用預設值
        """
        if ttl is None:
            ttl = self.default_ttl
        
        self._cache[key] = {
            'data': data,
            'expires_at': time.time() + ttl,
            'created_at': time.time()
        }
    
    def delete(self, key: str) -> bool:
        """
        刪除快取項目
        
        Args:
            key: 快取鍵值
            
        Returns:
            是否成功刪除
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """清空所有快取"""
        self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """
        清理所有過期的快取項目
        
        Returns:
            清理的項目數量
        """
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time > entry['expires_at']
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        取得快取統計資訊
        
        Returns:
            快取統計資訊字典
        """
        import sys
        
        current_time = time.time()
        valid_entries = sum(
            1 for entry in self._cache.values()
            if current_time <= entry['expires_at']
        )
        
        # 計算快取總大小
        total_size = sum(
            sys.getsizeof(entry['data'])
            for entry in self._cache.values()
        )
        
        return {
            'items': len(self._cache),  # 總項目數
            'total_entries': len(self._cache),
            'valid_entries': valid_entries,
            'expired_entries': len(self._cache) - valid_entries,
            'size': total_size,  # 總大小（bytes）
            'default_ttl': self.default_ttl
        }
    
    def get_cache_hit_rate(self) -> float:
        """
        取得快取命中率（需要追蹤 hits 和 misses）
        
        Returns:
            快取命中率（0-1之間）
        """
        if not hasattr(self, '_hits'):
            self._hits = 0
            self._misses = 0
        
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        
        return self._hits / total
    
    def _track_hit(self) -> None:
        """記錄快取命中"""
        if not hasattr(self, '_hits'):
            self._hits = 0
        self._hits += 1
    
    def _track_miss(self) -> None:
        """記錄快取未命中"""
        if not hasattr(self, '_misses'):
            self._misses = 0
        self._misses += 1


# 建立全域快取管理器實例
cache_manager = CacheManager()
