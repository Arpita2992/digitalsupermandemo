"""
Enhanced performance monitoring utilities with caching and optimization
"""
import time
import functools
import threading
import os
from typing import Dict, Any, Optional
from collections import defaultdict, deque
import json

# Try to import psutil, fallback to basic implementation if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ psutil not available - using basic performance monitoring")

class PerformanceMonitor:
    def __init__(self, max_entries=1000):
        self.timings = defaultdict(deque)
        self.max_entries = max_entries
        self.cache_stats = {'hits': 0, 'misses': 0, 'size': 0}
        self.system_stats = {}
        self.lock = threading.Lock()
        
    def time_function(self, func_name: str):
        """Decorator to time function execution with enhanced metrics"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss / 1024 / 1024 if PSUTIL_AVAILABLE else 0  # MB
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                    error = None
                except Exception as e:
                    success = False
                    error = str(e)
                    raise
                finally:
                    end_time = time.time()
                    end_memory = psutil.Process().memory_info().rss / 1024 / 1024 if PSUTIL_AVAILABLE else 0  # MB
                    
                    execution_time = end_time - start_time
                    memory_delta = end_memory - start_memory
                    
                    with self.lock:
                        # Store timing data
                        timing_data = {
                            'time': execution_time,
                            'memory_delta': memory_delta,
                            'success': success,
                            'error': error,
                            'timestamp': time.time()
                        }
                        
                        self.timings[func_name].append(timing_data)
                        
                        # Limit deque size
                        if len(self.timings[func_name]) > self.max_entries:
                            self.timings[func_name].popleft()
                    
                    # Log performance
                    status = "✅" if success else "❌"
                    print(f"⏱️ {status} {func_name}: {execution_time:.2f}s, Mem: {memory_delta:+.1f}MB")
                
                return result
            return wrapper
        return decorator
    
    def record_cache_hit(self):
        """Record a cache hit"""
        with self.lock:
            self.cache_stats['hits'] += 1
    
    def record_cache_miss(self):
        """Record a cache miss"""
        with self.lock:
            self.cache_stats['misses'] += 1
    
    def update_cache_size(self, size: int):
        """Update cache size"""
        with self.lock:
            self.cache_stats['size'] = size
    
    def get_stats(self) -> Dict[str, Any]:
        """Get enhanced performance statistics"""
        with self.lock:
            stats = {}
            
            # Function timing stats
            for func_name, times in self.timings.items():
                if times:
                    recent_times = [t['time'] for t in times if t['success']]
                    recent_memory = [t['memory_delta'] for t in times if t['success']]
                    error_count = sum(1 for t in times if not t['success'])
                    
                    if recent_times:
                        stats[func_name] = {
                            'count': len(times),
                            'success_count': len(recent_times),
                            'error_count': error_count,
                            'avg_time': sum(recent_times) / len(recent_times),
                            'total_time': sum(recent_times),
                            'min_time': min(recent_times),
                            'max_time': max(recent_times),
                            'avg_memory_delta': sum(recent_memory) / len(recent_memory) if recent_memory else 0,
                            'success_rate': len(recent_times) / len(times) * 100
                        }
            
            # Cache statistics
            total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
            cache_hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            stats['cache'] = {
                'hits': self.cache_stats['hits'],
                'misses': self.cache_stats['misses'],
                'hit_rate': cache_hit_rate,
                'size': self.cache_stats['size']
            }
            
            # System statistics
            if PSUTIL_AVAILABLE:
                try:
                    stats['system'] = {
                        'cpu_percent': psutil.cpu_percent(),
                        'memory_percent': psutil.virtual_memory().percent,
                        'available_memory_mb': psutil.virtual_memory().available / 1024 / 1024,
                        'disk_usage_percent': psutil.disk_usage('.').percent
                    }
                except Exception as e:
                    stats['system'] = {
                        'cpu_percent': 0,
                        'memory_percent': 0,
                        'available_memory_mb': 0,
                        'disk_usage_percent': 0,
                        'error': str(e)
                    }
            else:
                stats['system'] = {
                    'cpu_percent': 0,
                    'memory_percent': 0,
                    'available_memory_mb': 0,
                    'disk_usage_percent': 0,
                    'note': 'psutil not available - install for system metrics'
                }
            
            return stats
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        stats = self.get_stats()
        
        # Determine health status
        health_issues = []
        
        # Check CPU usage
        if stats['system']['cpu_percent'] > 80:
            health_issues.append("High CPU usage")
        
        # Check memory usage
        if stats['system']['memory_percent'] > 85:
            health_issues.append("High memory usage")
        
        # Check disk usage
        if stats['system']['disk_usage_percent'] > 90:
            health_issues.append("High disk usage")
        
        # Check cache hit rate
        if stats['cache']['hit_rate'] < 50 and stats['cache']['hits'] + stats['cache']['misses'] > 10:
            health_issues.append("Low cache hit rate")
        
        # Check for recent errors
        error_functions = []
        for func_name, data in stats.items():
            if isinstance(data, dict) and 'error_count' in data and data['error_count'] > 0:
                error_functions.append(func_name)
        
        if error_functions:
            health_issues.append(f"Functions with errors: {', '.join(error_functions)}")
        
        return {
            'status': 'healthy' if not health_issues else 'warning',
            'issues': health_issues,
            'stats': stats,
            'uptime': time.time() - getattr(self, 'start_time', time.time())
        }
    
    def reset_stats(self):
        """Reset all statistics"""
        with self.lock:
            self.timings.clear()
            self.cache_stats = {'hits': 0, 'misses': 0, 'size': 0}
            self.start_time = time.time()

class OptimizedCache:
    """Simple in-memory cache with LRU eviction"""
    def __init__(self, max_size=1000, ttl=3600):
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
        self.ttl = ttl
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self.lock:
            if key in self.cache:
                # Check TTL
                if time.time() - self.access_times.get(key, 0) < self.ttl:
                    self.access_times[key] = time.time()
                    perf_monitor.record_cache_hit()
                    return self.cache[key]
                else:
                    # Expired
                    del self.cache[key]
                    del self.access_times[key]
            
            perf_monitor.record_cache_miss()
            return None
    
    def set(self, key: str, value: Any):
        """Set value in cache"""
        with self.lock:
            # Evict if at max size
            if len(self.cache) >= self.max_size:
                # Remove least recently used
                lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
                del self.cache[lru_key]
                del self.access_times[lru_key]
            
            self.cache[key] = value
            self.access_times[key] = time.time()
            perf_monitor.update_cache_size(len(self.cache))
    
    def clear(self):
        """Clear cache"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
            perf_monitor.update_cache_size(0)

# Global instances
perf_monitor = PerformanceMonitor()
cache = OptimizedCache()

# Initialize start time
perf_monitor.start_time = time.time()

def cache_result(key_func=None, ttl=3600):
    """Decorator to cache function results"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            
            return result
        return wrapper
    return decorator

# Performance utilities
def measure_execution_time(func):
    """Simple execution time measurement"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"🚀 {func.__name__} executed in {end - start:.2f}s")
        return result
    return wrapper

def log_memory_usage(func):
    """Log memory usage before and after function execution"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                before = process.memory_info().rss / 1024 / 1024  # MB
                result = func(*args, **kwargs)
                after = process.memory_info().rss / 1024 / 1024  # MB
                delta = after - before
                print(f"🧠 {func.__name__} memory delta: {delta:+.1f}MB")
                return result
            except Exception:
                pass
        
        # Fallback if psutil not available
        result = func(*args, **kwargs)
        print(f"🧠 {func.__name__} memory monitoring not available (psutil missing)")
        return result
    return wrapper
