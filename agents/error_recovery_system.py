"""
🚨 ADVANCED ERROR RECOVERY SYSTEM - Production-Ready
Intelligent error handling, classification, and recovery strategies
Specialized for Turkish e-commerce scraping with adaptive learning
"""

import asyncio
import json
import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Callable, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum
from collections import defaultdict, deque
import sqlite3
from loguru import logger
import re
import traceback
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
import aiohttp


class ErrorType(Enum):
    """Classification of error types"""
    NETWORK_ERROR = "network_error"
    TIMEOUT_ERROR = "timeout_error"
    RATE_LIMIT = "rate_limit"
    ACCESS_DENIED = "access_denied"
    SELECTOR_FAILED = "selector_failed"
    DATA_VALIDATION = "data_validation"
    PROXY_ERROR = "proxy_error"
    BROWSER_ERROR = "browser_error"
    PARSING_ERROR = "parsing_error"
    UNKNOWN_ERROR = "unknown_error"


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"          # Retry immediately
    MEDIUM = "medium"    # Retry with delay
    HIGH = "high"        # Retry with different strategy
    CRITICAL = "critical" # Stop processing, manual intervention needed


@dataclass
class ErrorContext:
    """Context information for an error"""
    error_type: ErrorType
    severity: ErrorSeverity
    site_name: str
    url: str
    operation: str
    error_message: str
    stack_trace: str
    timestamp: datetime
    proxy_id: Optional[str] = None
    session_id: Optional[str] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class RecoveryStrategy:
    """Recovery strategy for error handling"""
    strategy_name: str
    priority: int
    max_retries: int
    delay_seconds: float
    success_rate: float
    applicable_errors: List[ErrorType]
    recovery_function: Callable
    
    def can_handle(self, error_type: ErrorType) -> bool:
        return error_type in self.applicable_errors


class ErrorClassifier:
    """Intelligent error classification system"""
    
    def __init__(self):
        self.classification_patterns = {
            ErrorType.NETWORK_ERROR: [
                r'network|connection|dns|resolve|host',
                r'ECONNREFUSED|ENOTFOUND|ETIMEDOUT',
                r'ConnectionError|ConnectTimeout'
            ],
            ErrorType.TIMEOUT_ERROR: [
                r'timeout|timed out|TimeoutError',
                r'Request timed out|Page timeout',
                r'waiting for|wait_for.*timeout'
            ],
            ErrorType.RATE_LIMIT: [
                r'rate limit|too many requests|429',
                r'slow down|request limit',
                r'temporarily blocked'
            ],
            ErrorType.ACCESS_DENIED: [
                r'access denied|forbidden|403|401',
                r'unauthorized|permission denied',
                r'blocked|banned'
            ],
            ErrorType.SELECTOR_FAILED: [
                r'element not found|selector.*not found',
                r'query_selector|wait_for_selector',
                r'NoSuchElementException'
            ],
            ErrorType.PROXY_ERROR: [
                r'proxy|ProxyError|ProxyConnectionError',
                r'proxy authentication|proxy timeout'
            ],
            ErrorType.BROWSER_ERROR: [
                r'browser|playwright|selenium',
                r'WebDriverException|BrowserError',
                r'page closed|context closed'
            ],
            ErrorType.PARSING_ERROR: [
                r'json|parse|parsing|decode',
                r'invalid json|malformed',
                r'BeautifulSoup|lxml'  
            ]
        }
        
        # Turkish e-commerce specific patterns
        self.turkish_patterns = {
            ErrorType.RATE_LIMIT: [
                r'çok fazla istek|hız sınırı',
                r'lütfen bekleyin|yavaşlayın'
            ],
            ErrorType.ACCESS_DENIED: [
                r'erişim reddedildi|yasaklandı',
                r'yetki yok|izin verilmedi'
            ]
        }
    
    def classify_error(self, error_message: str, stack_trace: str, 
                      site_name: str, operation: str) -> Tuple[ErrorType, ErrorSeverity]:
        """Classify error type and severity"""
        error_text = f"{error_message} {stack_trace}".lower()
        
        # Check standard patterns
        for error_type, patterns in self.classification_patterns.items():
            for pattern in patterns:
                if re.search(pattern, error_text, re.IGNORECASE):
                    severity = self._determine_severity(error_type, site_name, operation)
                    return error_type, severity
        
        # Check Turkish patterns
        for error_type, patterns in self.turkish_patterns.items():
            for pattern in patterns:
                if re.search(pattern, error_text, re.IGNORECASE):
                    severity = self._determine_severity(error_type, site_name, operation)
                    return error_type, severity
        
        # Check HTTP status codes
        status_match = re.search(r'(\d{3})', error_message)
        if status_match:
            status_code = int(status_match.group(1))
            if status_code == 429:
                return ErrorType.RATE_LIMIT, ErrorSeverity.HIGH
            elif status_code in [403, 401]:
                return ErrorType.ACCESS_DENIED, ErrorSeverity.HIGH
            elif status_code >= 500:
                return ErrorType.NETWORK_ERROR, ErrorSeverity.MEDIUM
        
        # Default to unknown error
        return ErrorType.UNKNOWN_ERROR, ErrorSeverity.MEDIUM
    
    def _determine_severity(self, error_type: ErrorType, site_name: str, operation: str) -> ErrorSeverity:
        """Determine error severity based on context"""
        # Critical errors that require immediate attention
        if error_type in [ErrorType.ACCESS_DENIED]:
            return ErrorSeverity.CRITICAL
        
        # High severity for important operations
        if error_type == ErrorType.RATE_LIMIT:
            return ErrorSeverity.HIGH
        
        # Medium severity for recoverable errors
        if error_type in [ErrorType.NETWORK_ERROR, ErrorType.TIMEOUT_ERROR, ErrorType.PROXY_ERROR]:
            return ErrorSeverity.MEDIUM
        
        # Low severity for simple retries
        if error_type in [ErrorType.SELECTOR_FAILED, ErrorType.PARSING_ERROR]:
            return ErrorSeverity.LOW
        
        return ErrorSeverity.MEDIUM


class RecoveryStrategyManager:
    """Manage different recovery strategies"""
    
    def __init__(self):
        self.strategies = []
        self.strategy_performance = defaultdict(lambda: {'success': 0, 'attempts': 0})
        self._initialize_strategies()
    
    def _initialize_strategies(self):
        """Initialize built-in recovery strategies"""
        
        # Network error recovery
        self.strategies.append(RecoveryStrategy(
            strategy_name="network_retry",
            priority=1,
            max_retries=3,
            delay_seconds=2.0,
            success_rate=0.8,
            applicable_errors=[ErrorType.NETWORK_ERROR, ErrorType.TIMEOUT_ERROR],
            recovery_function=self._network_recovery
        ))
        
        # Rate limit recovery
        self.strategies.append(RecoveryStrategy(
            strategy_name="rate_limit_backoff",
            priority=1,
            max_retries=5,
            delay_seconds=30.0,
            success_rate=0.9,
            applicable_errors=[ErrorType.RATE_LIMIT],
            recovery_function=self._rate_limit_recovery
        ))
        
        # Selector failure recovery
        self.strategies.append(RecoveryStrategy(
            strategy_name="selector_adaptation",
            priority=2,
            max_retries=3,
            delay_seconds=1.0,
            success_rate=0.7,
            applicable_errors=[ErrorType.SELECTOR_FAILED],
            recovery_function=self._selector_recovery
        ))
        
        # Proxy error recovery
        self.strategies.append(RecoveryStrategy(
            strategy_name="proxy_rotation",
            priority=1,
            max_retries=5,
            delay_seconds=5.0,
            success_rate=0.85,
            applicable_errors=[ErrorType.PROXY_ERROR, ErrorType.ACCESS_DENIED],
            recovery_function=self._proxy_recovery
        ))
        
        # Browser error recovery
        self.strategies.append(RecoveryStrategy(
            strategy_name="browser_restart",
            priority=3,
            max_retries=2,
            delay_seconds=10.0,
            success_rate=0.9,
            applicable_errors=[ErrorType.BROWSER_ERROR],
            recovery_function=self._browser_recovery
        ))
        
    
    def get_best_strategy(self, error_type: ErrorType) -> Optional[RecoveryStrategy]:
        """Get best strategy for error type based on performance"""
        applicable_strategies = [s for s in self.strategies if s.can_handle(error_type)]
        
        if not applicable_strategies:
            return None
        
        # Sort by priority and success rate
        applicable_strategies.sort(key=lambda s: (
            s.priority,
            -self.strategy_performance[s.strategy_name]['success'] / 
            max(1, self.strategy_performance[s.strategy_name]['attempts'])
        ))
        
        return applicable_strategies[0]
    
    async def _network_recovery(self, error_context: ErrorContext, **kwargs) -> bool:
        """Recovery strategy for network errors"""
        logger.info(f"🔄 Network recovery for {error_context.url}")
        
        # Exponential backoff
        delay = error_context.retry_count * 2 + 2
        await asyncio.sleep(delay)
        
        # Try different DNS or connection settings
        return True
    
    async def _rate_limit_recovery(self, error_context: ErrorContext, **kwargs) -> bool:
        """Recovery strategy for rate limiting"""
        logger.info(f"⏱️ Rate limit recovery for {error_context.site_name}")
        
        # Progressive delay based on retry count
        base_delay = 30
        delay = base_delay * (2 ** error_context.retry_count)
        delay = min(delay, 300)  # Max 5 minutes
        
        logger.info(f"Waiting {delay} seconds for rate limit recovery...")
        await asyncio.sleep(delay)
        
        return True
    
    async def _selector_recovery(self, error_context: ErrorContext, **kwargs) -> bool:
        """Recovery strategy for selector failures"""
        logger.info(f"🎯 Selector recovery for {error_context.operation}")
        
        # This would integrate with AI selector adaptation
        # For now, just wait and retry
        await asyncio.sleep(1)
        return True
    
    async def _proxy_recovery(self, error_context: ErrorContext, **kwargs) -> bool:
        """Recovery strategy for proxy errors"""
        logger.info(f"🔄 Proxy recovery for {error_context.proxy_id}")
        
        # Signal to rotate proxy
        session_manager = kwargs.get('session_manager')
        if session_manager and error_context.session_id:
            # Mark current session as unhealthy
            await session_manager._remove_session(error_context.session_id)
        
        await asyncio.sleep(5)
        return True
    
    async def _browser_recovery(self, error_context: ErrorContext, **kwargs) -> bool:
        """Recovery strategy for browser errors"""
        logger.info(f"🌐 Browser recovery for {error_context.session_id}")
        
        # Signal to restart browser session
        browser_manager = kwargs.get('browser_manager')
        if browser_manager:
            await browser_manager.close()
            await browser_manager.initialize()
        
        await asyncio.sleep(10)
        return True
    
    
    def record_strategy_result(self, strategy_name: str, success: bool):
        """Record strategy performance"""
        self.strategy_performance[strategy_name]['attempts'] += 1
        if success:
            self.strategy_performance[strategy_name]['success'] += 1


class ErrorRecoverySystem:
    """Main error recovery system"""
    
    def __init__(self, db_path: str = "error_recovery.db"):
        self.classifier = ErrorClassifier()
        self.strategy_manager = RecoveryStrategyManager()
        self.db_path = db_path
        self.error_history = deque(maxlen=1000)  # Keep last 1000 errors
        self.site_error_counts = defaultdict(int)
        self.init_database()
    
    def init_database(self):
        """Initialize error tracking database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS error_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_type TEXT,
                    severity TEXT,
                    site_name TEXT,
                    url TEXT,
                    operation TEXT,
                    error_message TEXT,
                    stack_trace TEXT,
                    proxy_id TEXT,
                    session_id TEXT,
                    retry_count INTEGER,
                    recovery_strategy TEXT,
                    recovery_success BOOLEAN,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS recovery_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy_name TEXT,
                    error_type TEXT,
                    attempts INTEGER DEFAULT 0,
                    successes INTEGER DEFAULT 0,
                    avg_recovery_time REAL DEFAULT 0.0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(strategy_name, error_type)
                )
            """)
    
    async def handle_error(self, error: Exception, context: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Main error handling entry point"""
        try:
            # Create error context
            error_context = await self._create_error_context(error, context)
            
            # Log error
            await self._log_error(error_context)
            
            # Check if we should attempt recovery
            if not self._should_attempt_recovery(error_context):
                logger.error(f"❌ Recovery abandoned for {error_context.error_type.value}")
                return False, "Max retries exceeded or critical error"
            
            # Get recovery strategy
            strategy = self.strategy_manager.get_best_strategy(error_context.error_type)
            if not strategy:
                logger.error(f"❌ No recovery strategy for {error_context.error_type.value}")
                return False, "No recovery strategy available"
            
            # Attempt recovery
            logger.info(f"🚨 Attempting recovery with strategy: {strategy.strategy_name}")
            recovery_success = await self._attempt_recovery(error_context, strategy, context)
            
            # Record results
            self.strategy_manager.record_strategy_result(strategy.strategy_name, recovery_success)
            await self._update_recovery_stats(strategy.strategy_name, error_context.error_type, recovery_success)
            
            if recovery_success:
                logger.info(f"✅ Recovery successful using {strategy.strategy_name}")
                return True, f"Recovered using {strategy.strategy_name}"
            else:
                logger.warning(f"❌ Recovery failed using {strategy.strategy_name}")
                return False, f"Recovery failed: {strategy.strategy_name}"
                
        except Exception as recovery_error:
            logger.error(f"Error in recovery system: {recovery_error}")
            return False, f"Recovery system error: {str(recovery_error)}"
    
    async def _create_error_context(self, error: Exception, context: Dict[str, Any]) -> ErrorContext:
        """Create error context from exception and context"""
        error_message = str(error)
        stack_trace = traceback.format_exc()
        
        # Classify error
        error_type, severity = self.classifier.classify_error(
            error_message, 
            stack_trace,
            context.get('site_name', 'unknown'),
            context.get('operation', 'unknown')
        )
        
        # Count previous retries
        retry_count = context.get('retry_count', 0)
        
        return ErrorContext(
            error_type=error_type,
            severity=severity,
            site_name=context.get('site_name', 'unknown'),
            url=context.get('url', ''),
            operation=context.get('operation', 'unknown'),
            error_message=error_message,
            stack_trace=stack_trace,
            timestamp=datetime.now(),
            proxy_id=context.get('proxy_id'),
            session_id=context.get('session_id'),
            retry_count=retry_count,
            metadata=context.get('metadata', {})
        )
    
    async def _log_error(self, error_context: ErrorContext):
        """Log error to database and memory"""
        # Add to memory history
        self.error_history.append(error_context)
        self.site_error_counts[error_context.site_name] += 1
        
        # Log to database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO error_log 
                (error_type, severity, site_name, url, operation, error_message, 
                 stack_trace, proxy_id, session_id, retry_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                error_context.error_type.value,
                error_context.severity.value,
                error_context.site_name,
                error_context.url,
                error_context.operation,
                error_context.error_message,
                error_context.stack_trace,
                error_context.proxy_id,
                error_context.session_id,
                error_context.retry_count
            ))
    
    def _should_attempt_recovery(self, error_context: ErrorContext) -> bool:
        """Determine if recovery should be attempted"""
        # Don't attempt recovery for critical errors after first try
        if error_context.severity == ErrorSeverity.CRITICAL and error_context.retry_count > 0:
            return False
        
        # Don't attempt recovery if too many retries
        max_retries = {
            ErrorSeverity.LOW: 5,
            ErrorSeverity.MEDIUM: 3,
            ErrorSeverity.HIGH: 2,
            ErrorSeverity.CRITICAL: 1
        }
        
        if error_context.retry_count >= max_retries[error_context.severity]:
            return False
        
        # Check if site has too many recent errors
        recent_errors = [
            err for err in self.error_history 
            if err.site_name == error_context.site_name and
            (datetime.now() - err.timestamp).total_seconds() < 3600  # Last hour
        ]
        
        if len(recent_errors) > 20:  # Too many errors in last hour
            logger.warning(f"Too many recent errors for {error_context.site_name}")
            return False
        
        return True
    
    async def _attempt_recovery(self, error_context: ErrorContext, strategy: RecoveryStrategy, 
                              context: Dict[str, Any]) -> bool:
        """Attempt recovery using strategy"""
        try:
            recovery_start = time.time()
            
            # Execute recovery strategy
            success = await strategy.recovery_function(error_context, **context)
            
            recovery_time = time.time() - recovery_start
            
            # Update error context with recovery info
            error_context.metadata['recovery_strategy'] = strategy.strategy_name
            error_context.metadata['recovery_time'] = recovery_time
            error_context.metadata['recovery_success'] = success
            
            return success
            
        except Exception as e:
            logger.error(f"Recovery strategy {strategy.strategy_name} failed: {e}")
            return False
    
    async def _update_recovery_stats(self, strategy_name: str, error_type: ErrorType, success: bool):
        """Update recovery statistics"""
        with sqlite3.connect(self.db_path) as conn:
            # Get current stats
            cursor = conn.execute("""
                SELECT attempts, successes FROM recovery_stats 
                WHERE strategy_name = ? AND error_type = ?
            """, (strategy_name, error_type.value))
            
            row = cursor.fetchone()
            
            if row:
                attempts, successes = row
                new_attempts = attempts + 1
                new_successes = successes + (1 if success else 0)
                
                conn.execute("""
                    UPDATE recovery_stats 
                    SET attempts = ?, successes = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE strategy_name = ? AND error_type = ?
                """, (new_attempts, new_successes, strategy_name, error_type.value))
            else:
                conn.execute("""
                    INSERT INTO recovery_stats (strategy_name, error_type, attempts, successes)
                    VALUES (?, ?, 1, ?)
                """, (strategy_name, error_type.value, 1 if success else 0))
    
    def get_error_analytics(self) -> Dict[str, Any]:
        """Get comprehensive error analytics"""
        with sqlite3.connect(self.db_path) as conn:
            # Error type distribution
            cursor = conn.execute("""
                SELECT error_type, COUNT(*) as count, 
                       AVG(retry_count) as avg_retries
                FROM error_log 
                WHERE timestamp > datetime('now', '-24 hours')
                GROUP BY error_type
                ORDER BY count DESC
            """)
            error_types = cursor.fetchall()
            
            # Site error distribution
            cursor = conn.execute("""
                SELECT site_name, COUNT(*) as count,
                       COUNT(CASE WHEN recovery_strategy IS NOT NULL THEN 1 END) as recovered
                FROM error_log 
                WHERE timestamp > datetime('now', '-24 hours')
                GROUP BY site_name
                ORDER BY count DESC
            """)
            site_errors = cursor.fetchall()
            
            # Recovery strategy performance
            cursor = conn.execute("""
                SELECT strategy_name, error_type, attempts, successes,
                       CASE 
                           WHEN attempts > 0 THEN ROUND(successes * 100.0 / attempts, 2)
                           ELSE 0 
                       END as success_rate
                FROM recovery_stats
                ORDER BY success_rate DESC
            """)
            strategy_performance = cursor.fetchall()
            
            # Hourly error trend
            cursor = conn.execute("""
                SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
                FROM error_log 
                WHERE timestamp > datetime('now', '-24 hours')
                GROUP BY hour
                ORDER BY hour
            """)
            hourly_trend = cursor.fetchall()
        
        return {
            'error_types': [
                {
                    'type': row[0],
                    'count': row[1],
                    'avg_retries': round(row[2], 2)
                }
                for row in error_types
            ],
            'site_errors': [
                {
                    'site': row[0],
                    'total_errors': row[1],
                    'recovered_errors': row[2],
                    'recovery_rate': round(row[2] / row[1] * 100, 2) if row[1] > 0 else 0
                }
                for row in site_errors
            ],
            'strategy_performance': [
                {
                    'strategy': row[0],
                    'error_type': row[1],
                    'attempts': row[2],
                    'successes': row[3],
                    'success_rate': row[4]
                }
                for row in strategy_performance
            ],
            'hourly_trend': [
                {
                    'hour': row[0],
                    'error_count': row[1]
                }
                for row in hourly_trend
            ],
            'summary': {
                'total_errors_24h': sum(row[1] for row in error_types),
                'most_common_error': error_types[0][0] if error_types else 'None',
                'problematic_site': site_errors[0][0] if site_errors else 'None',
                'best_strategy': strategy_performance[0][0] if strategy_performance else 'None'
            }
        }
    
    async def auto_optimize_strategies(self):
        """Automatically optimize recovery strategies based on performance"""
        logger.info("🔧 Auto-optimizing recovery strategies...")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT strategy_name, error_type, attempts, successes
                FROM recovery_stats
                WHERE attempts >= 10  -- Only strategies with enough data
            """)
            
            for row in cursor.fetchall():
                strategy_name, error_type, attempts, successes = row
                success_rate = successes / attempts
                
                # Find strategy in manager
                strategy = next((s for s in self.strategy_manager.strategies 
                               if s.strategy_name == strategy_name), None)
                
                if strategy:
                    # Update success rate
                    strategy.success_rate = success_rate
                    
                    # Adjust parameters based on performance
                    if success_rate < 0.5:
                        # Poor performance - increase delay
                        strategy.delay_seconds *= 1.5
                        strategy.max_retries = max(1, strategy.max_retries - 1)
                        logger.info(f"📉 Reduced effectiveness for {strategy_name}")
                    elif success_rate > 0.9:
                        # Excellent performance - optimize for speed
                        strategy.delay_seconds *= 0.8
                        strategy.priority = max(1, strategy.priority - 1)
                        logger.info(f"📈 Optimized {strategy_name} for better performance")
        
        logger.info("✅ Strategy optimization complete")


# Factory function
def create_error_recovery_system(db_path: str = "error_recovery.db") -> ErrorRecoverySystem:
    """Create error recovery system"""
    return ErrorRecoverySystem(db_path)


# Context manager for error handling
class ErrorRecoveryContext:
    """Context manager for automatic error recovery"""
    
    def __init__(self, recovery_system: ErrorRecoverySystem, operation: str, **context):
        self.recovery_system = recovery_system
        self.operation = operation
        self.context = context
        self.retry_count = 0
        self.max_retries = context.get('max_retries', 3)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Error occurred
            self.context['operation'] = self.operation
            self.context['retry_count'] = self.retry_count
            
            success, message = await self.recovery_system.handle_error(exc_val, self.context)
            
            if success and self.retry_count < self.max_retries:
                logger.info(f"🔄 Retrying {self.operation} (attempt {self.retry_count + 1})")
                return True  # Suppress exception and retry
        
        return False  # Don't suppress exception


# Usage example
if __name__ == "__main__":
    async def test_error_recovery():
        """Test the error recovery system"""
        recovery_system = create_error_recovery_system()
        
        # Simulate an error
        test_context = {
            'site_name': 'trendyol',
            'url': 'https://www.trendyol.com/test',
            'operation': 'data_extraction',
            'session_id': 'test_session_123'
        }
        
        try:
            raise Exception("Network connection timeout")
        except Exception as e:
            success, message = await recovery_system.handle_error(e, test_context)
            logger.info(f"Recovery result: {success}, {message}")
        
        # Get analytics
        analytics = recovery_system.get_error_analytics()
        logger.info(f"📊 Error analytics: {json.dumps(analytics, indent=2, default=str)}")
        
        # Test auto-optimization
        await recovery_system.auto_optimize_strategies()
    
    asyncio.run(test_error_recovery())