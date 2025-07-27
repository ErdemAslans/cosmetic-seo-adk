"""
🔄 SMART SESSION & PROXY MANAGEMENT - Production-Ready
Intelligent session management with proxy rotation, health monitoring, and cost optimization
Specifically designed for Turkish e-commerce scraping with advanced load balancing
"""

import asyncio
import json
import time
import random
import aiohttp
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import sqlite3
from pathlib import Path
from loguru import logger
import numpy as np
from urllib.parse import urlparse
import ssl
import certifi


@dataclass
class ProxyConfig:
    """Proxy configuration with metadata"""
    server: str
    username: Optional[str] = None
    password: Optional[str] = None
    proxy_type: str = "http"  # http, https, socks5
    country: str = "TR"
    city: Optional[str] = None
    provider: str = "unknown"
    cost_per_gb: float = 0.0
    monthly_cost: float = 0.0
    max_concurrent: int = 10


@dataclass
class ProxyMetrics:
    """Proxy performance metrics"""
    proxy_id: str
    success_count: int = 0
    failure_count: int = 0
    total_requests: int = 0
    avg_response_time: float = 0.0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    data_usage_mb: float = 0.0
    blocked_sites: Set[str] = None
    health_score: float = 1.0
    
    def __post_init__(self):
        if self.blocked_sites is None:
            self.blocked_sites = set()


@dataclass
class SessionInfo:
    """Browser session information"""
    session_id: str
    proxy_config: Optional[ProxyConfig]
    site_name: str
    created_at: datetime
    last_used: datetime
    request_count: int = 0
    success_rate: float = 1.0
    is_healthy: bool = True
    browser_context = None
    page = None
    user_agent: str = ""
    fingerprint_hash: str = ""


class ProxyHealthMonitor:
    """Monitor proxy health and performance"""
    
    def __init__(self, db_path: str = "proxy_metrics.db"):
        self.db_path = db_path
        self.metrics = {}
        self.init_database()
        
    def init_database(self):
        """Initialize proxy metrics database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS proxy_metrics (
                    proxy_id TEXT PRIMARY KEY,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    total_requests INTEGER DEFAULT 0,
                    avg_response_time REAL DEFAULT 0.0,
                    last_success TIMESTAMP,
                    last_failure TIMESTAMP,
                    consecutive_failures INTEGER DEFAULT 0,
                    data_usage_mb REAL DEFAULT 0.0,
                    blocked_sites TEXT DEFAULT '[]',
                    health_score REAL DEFAULT 1.0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS proxy_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proxy_id TEXT,
                    site_name TEXT,
                    url TEXT,
                    success BOOLEAN,
                    response_time REAL,
                    status_code INTEGER,
                    error_message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def load_metrics(self) -> Dict[str, ProxyMetrics]:
        """Load proxy metrics from database"""
        metrics = {}
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM proxy_metrics")
            
            for row in cursor.fetchall():
                blocked_sites = set(json.loads(row[9])) if row[9] else set()
                
                metrics[row[0]] = ProxyMetrics(
                    proxy_id=row[0],
                    success_count=row[1],
                    failure_count=row[2], 
                    total_requests=row[3],
                    avg_response_time=row[4],
                    last_success=datetime.fromisoformat(row[5]) if row[5] else None,
                    last_failure=datetime.fromisoformat(row[6]) if row[6] else None,
                    consecutive_failures=row[7],
                    data_usage_mb=row[8],
                    blocked_sites=blocked_sites,
                    health_score=row[10]
                )
        
        return metrics
    
    def save_metrics(self, metrics: Dict[str, ProxyMetrics]):
        """Save proxy metrics to database"""
        with sqlite3.connect(self.db_path) as conn:
            for proxy_id, metric in metrics.items():
                blocked_sites_json = json.dumps(list(metric.blocked_sites))
                
                conn.execute("""
                    INSERT OR REPLACE INTO proxy_metrics 
                    (proxy_id, success_count, failure_count, total_requests, avg_response_time,
                     last_success, last_failure, consecutive_failures, data_usage_mb, 
                     blocked_sites, health_score, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    proxy_id, metric.success_count, metric.failure_count, metric.total_requests,
                    metric.avg_response_time, 
                    metric.last_success.isoformat() if metric.last_success else None,
                    metric.last_failure.isoformat() if metric.last_failure else None,
                    metric.consecutive_failures, metric.data_usage_mb,
                    blocked_sites_json, metric.health_score
                ))
    
    def record_request(self, proxy_id: str, site_name: str, url: str, 
                      success: bool, response_time: float, status_code: int = 200,
                      error_message: str = ""):
        """Record a proxy request"""
        # Update in-memory metrics
        if proxy_id not in self.metrics:
            self.metrics[proxy_id] = ProxyMetrics(proxy_id=proxy_id)
        
        metric = self.metrics[proxy_id]
        metric.total_requests += 1
        
        if success:
            metric.success_count += 1
            metric.last_success = datetime.now()
            metric.consecutive_failures = 0
        else:
            metric.failure_count += 1
            metric.last_failure = datetime.now()
            metric.consecutive_failures += 1
            
            # Mark site as potentially blocked if multiple consecutive failures
            if metric.consecutive_failures >= 3:
                metric.blocked_sites.add(site_name)
        
        # Update average response time
        if metric.total_requests > 1:
            metric.avg_response_time = (
                (metric.avg_response_time * (metric.total_requests - 1) + response_time) / 
                metric.total_requests
            )
        else:
            metric.avg_response_time = response_time
        
        # Calculate health score
        metric.health_score = self._calculate_health_score(metric)
        
        # Save to database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO proxy_requests 
                (proxy_id, site_name, url, success, response_time, status_code, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (proxy_id, site_name, url, success, response_time, status_code, error_message))
    
    def _calculate_health_score(self, metric: ProxyMetrics) -> float:
        """Calculate proxy health score (0.0 to 1.0)"""
        if metric.total_requests == 0:
            return 1.0
        
        # Base success rate (0.0 to 0.6)
        success_rate = metric.success_count / metric.total_requests
        score = success_rate * 0.6
        
        # Response time factor (0.0 to 0.2)
        if metric.avg_response_time > 0:
            # Penalize slow responses (>5 seconds)
            time_factor = max(0, 1 - (metric.avg_response_time / 10))
            score += time_factor * 0.2
        
        # Recency factor (0.0 to 0.1)
        if metric.last_success:
            hours_since_success = (datetime.now() - metric.last_success).total_seconds() / 3600
            recency_factor = max(0, 1 - (hours_since_success / 24))  # Decay over 24 hours
            score += recency_factor * 0.1
        
        # Consecutive failure penalty (0.0 to -0.3)
        failure_penalty = min(0.3, metric.consecutive_failures * 0.1)
        score -= failure_penalty
        
        # Blocked sites penalty
        blocked_penalty = len(metric.blocked_sites) * 0.05
        score -= blocked_penalty
        
        return max(0.0, min(1.0, score))
    
    def get_best_proxies(self, site_name: str, count: int = 5) -> List[str]:
        """Get best performing proxies for a site"""
        site_scores = []
        
        for proxy_id, metric in self.metrics.items():
            # Skip if blocked for this site
            if site_name in metric.blocked_sites:
                continue
            
            # Calculate site-specific score
            site_score = metric.health_score
            
            # Bonus for recent success on this site
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM proxy_requests 
                    WHERE proxy_id = ? AND site_name = ? AND success = 1 
                    AND timestamp > datetime('now', '-24 hours')
                """, (proxy_id, site_name))
                
                recent_successes = cursor.fetchone()[0]
                site_score += min(0.2, recent_successes * 0.05)
            
            site_scores.append((site_score, proxy_id))
        
        # Sort by score and return top proxies
        site_scores.sort(key=lambda x: x[0], reverse=True)
        return [proxy_id for score, proxy_id in site_scores[:count]]


class LoadBalancer:
    """Intelligent load balancing for proxies and sessions"""
    
    def __init__(self):
        self.proxy_loads = defaultdict(int)  # Current load per proxy
        self.proxy_capacities = {}  # Max concurrent requests per proxy
        self.request_queue = deque()
        self.active_requests = {}
        
    def register_proxy(self, proxy_id: str, max_concurrent: int = 10):
        """Register a proxy with its capacity"""
        self.proxy_capacities[proxy_id] = max_concurrent
        self.proxy_loads[proxy_id] = 0
    
    def get_least_loaded_proxy(self, available_proxies: List[str]) -> Optional[str]:
        """Get the proxy with lowest current load"""
        best_proxy = None
        min_load_ratio = float('inf')
        
        for proxy_id in available_proxies:
            if proxy_id not in self.proxy_capacities:
                continue
                
            current_load = self.proxy_loads[proxy_id]
            max_capacity = self.proxy_capacities[proxy_id]
            
            if current_load >= max_capacity:
                continue  # Proxy at capacity
            
            load_ratio = current_load / max_capacity
            if load_ratio < min_load_ratio:
                min_load_ratio = load_ratio
                best_proxy = proxy_id
        
        return best_proxy
    
    def allocate_request(self, proxy_id: str, request_id: str):
        """Allocate a request to a proxy"""
        self.proxy_loads[proxy_id] += 1
        self.active_requests[request_id] = proxy_id
    
    def release_request(self, request_id: str):
        """Release a request from a proxy"""
        if request_id in self.active_requests:
            proxy_id = self.active_requests[request_id]
            self.proxy_loads[proxy_id] = max(0, self.proxy_loads[proxy_id] - 1)
            del self.active_requests[request_id]
    
    def get_load_stats(self) -> Dict[str, Any]:
        """Get current load statistics"""
        stats = {}
        total_capacity = sum(self.proxy_capacities.values())
        total_load = sum(self.proxy_loads.values())
        
        for proxy_id in self.proxy_capacities:
            load = self.proxy_loads[proxy_id]
            capacity = self.proxy_capacities[proxy_id]
            stats[proxy_id] = {
                'load': load,
                'capacity': capacity,
                'utilization': load / capacity if capacity > 0 else 0,
                'available': capacity - load
            }
        
        return {
            'proxy_stats': stats,
            'total_utilization': total_load / total_capacity if total_capacity > 0 else 0,
            'available_capacity': total_capacity - total_load
        }


class SmartSessionManager:
    """Main session management system"""
    
    def __init__(self, proxy_configs: List[ProxyConfig]):
        self.proxy_configs = {self._get_proxy_id(config): config for config in proxy_configs}
        self.health_monitor = ProxyHealthMonitor()
        self.load_balancer = LoadBalancer()
        self.active_sessions = {}
        self.session_pools = defaultdict(list)  # Site-specific session pools
        self.session_rotation_interval = timedelta(hours=2)
        self.cost_tracker = CostTracker()
        
        # Initialize components
        self._initialize_load_balancer()
        self.health_monitor.metrics = self.health_monitor.load_metrics()
        
    def _initialize_load_balancer(self):
        """Initialize load balancer with proxy capacities"""
        for proxy_id, config in self.proxy_configs.items():
            self.load_balancer.register_proxy(proxy_id, config.max_concurrent)
    
    def _get_proxy_id(self, config: ProxyConfig) -> str:
        """Generate unique proxy ID"""
        return hashlib.md5(f"{config.server}:{config.username}".encode()).hexdigest()[:12]
    
    async def get_optimal_session(self, site_name: str) -> SessionInfo:
        """Get optimal session for a site with intelligent selection"""
        # Check for healthy existing sessions
        existing_session = self._find_healthy_session(site_name)
        if existing_session:
            existing_session.last_used = datetime.now()
            existing_session.request_count += 1
            return existing_session
        
        # Create new session
        return await self._create_new_session(site_name)
    
    def _find_healthy_session(self, site_name: str) -> Optional[SessionInfo]:
        """Find healthy existing session for site"""
        site_sessions = self.session_pools.get(site_name, [])
        
        for session in site_sessions:
            if (session.is_healthy and 
                session.request_count < 100 and  # Max requests per session
                datetime.now() - session.created_at < self.session_rotation_interval):
                return session
        
        return None
    
    async def _create_new_session(self, site_name: str) -> SessionInfo:
        """Create new optimized session"""
        # Get best proxies for this site
        best_proxies = self.health_monitor.get_best_proxies(site_name, 5)
        
        # Use load balancing to select optimal proxy
        optimal_proxy_id = self.load_balancer.get_least_loaded_proxy(best_proxies)
        
        proxy_config = None
        if optimal_proxy_id:
            proxy_config = self.proxy_configs[optimal_proxy_id]
        
        # Generate session ID
        session_id = f"{site_name}_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Create session info
        session = SessionInfo(
            session_id=session_id,
            proxy_config=proxy_config,
            site_name=site_name,
            created_at=datetime.now(),
            last_used=datetime.now(),
            user_agent=self._generate_user_agent(),
            fingerprint_hash=self._generate_fingerprint_hash()
        )
        
        # Allocate in load balancer
        if optimal_proxy_id:
            self.load_balancer.allocate_request(optimal_proxy_id, session_id)
        
        # Store session
        self.active_sessions[session_id] = session
        self.session_pools[site_name].append(session)
        
        logger.info(f"🚀 Created new session {session_id} for {site_name} with proxy {optimal_proxy_id}")
        return session
    
    def _generate_user_agent(self) -> str:
        """Generate realistic Turkish user agent"""
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]
        return random.choice(agents)
    
    def _generate_fingerprint_hash(self) -> str:
        """Generate unique fingerprint hash"""
        fingerprint_data = {
            'timestamp': int(time.time()),
            'random': random.randint(10000, 99999),
            'screen': random.choice(['1920x1080', '1366x768', '1440x900'])
        }
        return hashlib.md5(json.dumps(fingerprint_data).encode()).hexdigest()[:16]
    
    async def record_request_result(self, session_id: str, url: str, success: bool, 
                                  response_time: float, status_code: int = 200,
                                  error_message: str = ""):
        """Record the result of a request"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        
        # Update session metrics
        if success:
            session.success_rate = (session.success_rate * session.request_count + 1) / (session.request_count + 1)
        else:
            session.success_rate = (session.success_rate * session.request_count) / (session.request_count + 1)
            # Mark session as unhealthy if success rate drops too low
            if session.success_rate < 0.3:
                session.is_healthy = False
        
        # Record in proxy health monitor
        if session.proxy_config:
            proxy_id = self._get_proxy_id(session.proxy_config)
            self.health_monitor.record_request(
                proxy_id, session.site_name, url, success, response_time, status_code, error_message
            )
            
            # Track cost
            self.cost_tracker.record_request(proxy_id, session.proxy_config, len(url))
    
    async def cleanup_stale_sessions(self):
        """Clean up old and unhealthy sessions"""
        current_time = datetime.now()
        sessions_to_remove = []
        
        for session_id, session in self.active_sessions.items():
            # Remove if too old or unhealthy
            if (current_time - session.created_at > self.session_rotation_interval or
                not session.is_healthy or
                session.request_count > 200):
                
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            await self._remove_session(session_id)
        
        logger.info(f"🧹 Cleaned up {len(sessions_to_remove)} stale sessions")
    
    async def _remove_session(self, session_id: str):
        """Remove a session and clean up resources"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        
        # Close browser resources if any
        if session.page:
            try:
                await session.page.close()
            except:
                pass
        
        if session.browser_context:
            try:
                await session.browser_context.close()
            except:
                pass
        
        # Release from load balancer
        self.load_balancer.release_request(session_id)
        
        # Remove from session pools
        site_sessions = self.session_pools.get(session.site_name, [])
        if session in site_sessions:
            site_sessions.remove(session)
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        logger.debug(f"🗑️ Removed session {session_id}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        # Session metrics
        total_sessions = len(self.active_sessions)
        healthy_sessions = sum(1 for s in self.active_sessions.values() if s.is_healthy)
        
        site_session_counts = defaultdict(int)
        for session in self.active_sessions.values():
            site_session_counts[session.site_name] += 1
        
        # Load balancer metrics
        load_stats = self.load_balancer.get_load_stats()
        
        # Cost metrics
        cost_stats = self.cost_tracker.get_cost_summary()
        
        # Proxy health metrics
        proxy_health = {}
        for proxy_id, metric in self.health_monitor.metrics.items():
            proxy_health[proxy_id] = {
                'health_score': metric.health_score,
                'success_rate': metric.success_count / max(metric.total_requests, 1),
                'total_requests': metric.total_requests,
                'blocked_sites': list(metric.blocked_sites)
            }
        
        return {
            'session_metrics': {
                'total_sessions': total_sessions,
                'healthy_sessions': healthy_sessions,
                'health_rate': healthy_sessions / max(total_sessions, 1),
                'sessions_per_site': dict(site_session_counts)
            },
            'load_balancer': load_stats,
            'cost_tracking': cost_stats,
            'proxy_health': proxy_health,
            'timestamp': datetime.now().isoformat()
        }
    
    async def save_metrics(self):
        """Save all metrics to persistent storage"""
        self.health_monitor.save_metrics(self.health_monitor.metrics)
        await self.cost_tracker.save_costs()
        logger.info("💾 Session metrics saved to database")


class CostTracker:
    """Track and optimize proxy usage costs"""
    
    def __init__(self):
        self.daily_costs = defaultdict(float)
        self.proxy_usage = defaultdict(float)  # Data usage in MB
        self.request_counts = defaultdict(int)
        
    def record_request(self, proxy_id: str, proxy_config: ProxyConfig, data_size: int):
        """Record a request for cost tracking"""
        data_mb = data_size / (1024 * 1024)  # Convert to MB
        self.proxy_usage[proxy_id] += data_mb
        self.request_counts[proxy_id] += 1
        
        # Calculate cost
        if proxy_config.cost_per_gb > 0:
            cost = (data_mb / 1024) * proxy_config.cost_per_gb
            today = datetime.now().date()
            self.daily_costs[f"{proxy_id}_{today}"] += cost
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost summary"""
        today = datetime.now().date()
        total_today = sum(cost for key, cost in self.daily_costs.items() if str(today) in key)
        
        proxy_costs = {}
        for proxy_id in self.proxy_usage:
            proxy_today_cost = sum(
                cost for key, cost in self.daily_costs.items() 
                if key.startswith(f"{proxy_id}_{today}")
            )
            proxy_costs[proxy_id] = {
                'daily_cost': proxy_today_cost,
                'data_usage_mb': self.proxy_usage[proxy_id],
                'request_count': self.request_counts[proxy_id]
            }
        
        return {
            'total_daily_cost': total_today,
            'proxy_breakdown': proxy_costs,
            'date': str(today)
        }
    
    async def save_costs(self):
        """Save cost data (implement as needed)"""
        # Could save to database or file for persistent tracking
        pass


# Factory function
def create_smart_session_manager(proxy_configs: List[Dict[str, Any]]) -> SmartSessionManager:
    """Create smart session manager with proxy configurations"""
    configs = []
    for config_dict in proxy_configs:
        config = ProxyConfig(**config_dict)
        configs.append(config)
    
    return SmartSessionManager(configs)


# Usage example
if __name__ == "__main__":
    async def test_session_manager():
        """Test the session manager"""
        # Example proxy configurations
        proxy_configs = [
            {
                'server': 'http://proxy1.example.com:8080',
                'username': 'user1',
                'password': 'pass1',
                'country': 'TR',
                'city': 'Istanbul',
                'provider': 'IPRoyal',
                'cost_per_gb': 7.0,
                'max_concurrent': 10
            },
            {
                'server': 'http://proxy2.example.com:8080', 
                'username': 'user2',
                'password': 'pass2',
                'country': 'TR',
                'city': 'Ankara',
                'provider': 'Smartproxy',
                'cost_per_gb': 8.5,
                'max_concurrent': 15
            }
        ]
        
        manager = create_smart_session_manager(proxy_configs)
        
        # Test session creation
        session = await manager.get_optimal_session('trendyol')
        logger.info(f"🧪 Created test session: {session.session_id}")
        
        # Simulate request
        await manager.record_request_result(
            session.session_id, 
            'https://www.trendyol.com/test',
            True, 
            1.5
        )
        
        # Get metrics
        metrics = manager.get_performance_metrics()
        logger.info(f"📊 Performance metrics: {json.dumps(metrics, indent=2, default=str)}")
        
        # Cleanup
        await manager.cleanup_stale_sessions()
        await manager.save_metrics()
    
    asyncio.run(test_session_manager())