"""
Trace Management System for Digital Superman
Tracks requests, performance metrics, and token usage
"""

import uuid
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import os
from dataclasses import dataclass, asdict
from threading import Lock
import sqlite3
from contextlib import contextmanager

@dataclass
class TraceEvent:
    trace_id: str
    event_type: str  # 'request_start', 'agent_start', 'agent_complete', 'agent_error', 'request_complete'
    agent_name: str
    timestamp: float
    duration_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    status: str = 'success'  # 'success', 'error', 'processing'
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class TraceMetrics:
    trace_id: str
    user_session: str
    start_time: float
    end_time: Optional[float] = None
    total_duration_ms: Optional[int] = None
    total_tokens: int = 0
    file_name: str = ""
    file_size: int = 0
    environment: str = "development"
    status: str = "processing"  # 'processing', 'completed', 'failed'
    agent_metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.agent_metrics is None:
            self.agent_metrics = {}

class TraceManager:
    def __init__(self, db_path: str = "traces.db"):
        self.db_path = db_path
        self.active_traces: Dict[str, TraceMetrics] = {}
        self.lock = Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for trace storage"""
        with self._get_db_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS traces (
                    trace_id TEXT PRIMARY KEY,
                    user_session TEXT,
                    start_time REAL,
                    end_time REAL,
                    total_duration_ms INTEGER,
                    total_tokens INTEGER,
                    file_name TEXT,
                    file_size INTEGER,
                    environment TEXT,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trace_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trace_id TEXT,
                    event_type TEXT,
                    agent_name TEXT,
                    timestamp REAL,
                    duration_ms INTEGER,
                    tokens_used INTEGER,
                    status TEXT,
                    error_message TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (trace_id) REFERENCES traces (trace_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trace_id TEXT,
                    agent_name TEXT,
                    start_time REAL,
                    end_time REAL,
                    duration_ms INTEGER,
                    tokens_used INTEGER,
                    status TEXT,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (trace_id) REFERENCES traces (trace_id)
                )
            """)
    
    @contextmanager
    def _get_db_connection(self):
        """Get database connection with proper error handling"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def create_trace(self, user_session: str = None, file_name: str = "", 
                    file_size: int = 0, environment: str = "development") -> str:
        """Create a new trace and return trace ID"""
        trace_id = str(uuid.uuid4())
        current_time = time.time()
        
        if user_session is None:
            user_session = str(uuid.uuid4())[:8]
        
        trace_metrics = TraceMetrics(
            trace_id=trace_id,
            user_session=user_session,
            start_time=current_time,
            file_name=file_name,
            file_size=file_size,
            environment=environment
        )
        
        with self.lock:
            self.active_traces[trace_id] = trace_metrics
        
        # Store in database
        with self._get_db_connection() as conn:
            conn.execute("""
                INSERT INTO traces (trace_id, user_session, start_time, file_name, 
                                  file_size, environment, status, total_tokens)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (trace_id, user_session, current_time, file_name, 
                  file_size, environment, 'processing', 0))
        
        print(f"🆔 New trace created: {trace_id}")
        return trace_id
    
    def update_trace_file_info(self, trace_id: str, file_name: str, file_size: int):
        """Update file information for an existing trace"""
        with self.lock:
            if trace_id in self.active_traces:
                trace = self.active_traces[trace_id]
                trace.file_name = file_name
                trace.file_size = file_size
                
                # Update database
                with self._get_db_connection() as conn:
                    conn.execute("""
                        UPDATE traces SET file_name = ?, file_size = ?
                        WHERE trace_id = ?
                    """, (file_name, file_size, trace_id))
                
                print(f"📁 Updated trace {trace_id} with file info: {file_name} ({file_size} bytes)")
            else:
                print(f"⚠️ Warning: Trace {trace_id} not found for file info update")
    
    def log_event(self, trace_id: str, event_type: str, agent_name: str, 
                 duration_ms: int = None, tokens_used: int = None, 
                 status: str = 'success', error_message: str = None, 
                 metadata: Dict[str, Any] = None):
        """Log a trace event"""
        if trace_id not in self.active_traces:
            print(f"⚠️ Warning: Trace {trace_id} not found in active traces")
            return
        
        event = TraceEvent(
            trace_id=trace_id,
            event_type=event_type,
            agent_name=agent_name,
            timestamp=time.time(),
            duration_ms=duration_ms,
            tokens_used=tokens_used,
            status=status,
            error_message=error_message,
            metadata=metadata
        )
        
        # Store event in database
        with self._get_db_connection() as conn:
            conn.execute("""
                INSERT INTO trace_events (trace_id, event_type, agent_name, timestamp,
                                        duration_ms, tokens_used, status, error_message, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (trace_id, event_type, agent_name, event.timestamp,
                  duration_ms, tokens_used, status, error_message, 
                  json.dumps(metadata) if metadata else None))
        
        # Update active trace metrics
        with self.lock:
            trace = self.active_traces[trace_id]
            if tokens_used:
                trace.total_tokens += tokens_used
            
            # Update agent metrics
            if agent_name not in trace.agent_metrics:
                trace.agent_metrics[agent_name] = {
                    'start_time': None,
                    'end_time': None,
                    'duration_ms': 0,
                    'tokens_used': 0,
                    'status': 'processing',
                    'error_message': None
                }
            
            agent_metric = trace.agent_metrics[agent_name]
            
            if event_type == 'agent_start':
                agent_metric['start_time'] = event.timestamp
                agent_metric['status'] = 'processing'
            elif event_type == 'agent_complete':
                agent_metric['end_time'] = event.timestamp
                agent_metric['status'] = 'completed'
                if duration_ms:
                    agent_metric['duration_ms'] = duration_ms
            elif event_type == 'agent_error':
                agent_metric['status'] = 'error'
                agent_metric['error_message'] = error_message
            
            if tokens_used:
                agent_metric['tokens_used'] += tokens_used
    
    def complete_trace(self, trace_id: str, status: str = 'completed'):
        """Mark a trace as complete"""
        if trace_id not in self.active_traces:
            print(f"⚠️ Warning: Trace {trace_id} not found in active traces")
            return
        
        with self.lock:
            trace = self.active_traces[trace_id]
            trace.end_time = time.time()
            trace.total_duration_ms = int((trace.end_time - trace.start_time) * 1000)
            trace.status = status
        
        # Update database
        with self._get_db_connection() as conn:
            conn.execute("""
                UPDATE traces 
                SET end_time = ?, total_duration_ms = ?, status = ?, total_tokens = ?
                WHERE trace_id = ?
            """, (trace.end_time, trace.total_duration_ms, status, 
                  trace.total_tokens, trace_id))
            
            # Store final agent metrics
            for agent_name, metrics in trace.agent_metrics.items():
                conn.execute("""
                    INSERT OR REPLACE INTO agent_metrics 
                    (trace_id, agent_name, start_time, end_time, duration_ms, 
                     tokens_used, status, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (trace_id, agent_name, metrics.get('start_time'),
                      metrics.get('end_time'), metrics.get('duration_ms', 0),
                      metrics.get('tokens_used', 0), metrics.get('status'),
                      metrics.get('error_message')))
        
        print(f"✅ Trace completed: {trace_id} ({trace.total_duration_ms}ms, {trace.total_tokens} tokens)")
    
    def get_trace_metrics(self, trace_id: str) -> Optional[TraceMetrics]:
        """Get metrics for a specific trace"""
        with self.lock:
            return self.active_traces.get(trace_id)
    
    def get_dashboard_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics for the performance dashboard"""
        cutoff_time = time.time() - (hours * 3600)
        
        with self._get_db_connection() as conn:
            # Get recent traces
            traces = conn.execute("""
                SELECT * FROM traces 
                WHERE start_time > ? 
                ORDER BY start_time DESC
                LIMIT 100
            """, (cutoff_time,)).fetchall()
            
            # Get agent performance
            agent_metrics = conn.execute("""
                SELECT agent_name, 
                       COUNT(*) as total_runs,
                       AVG(duration_ms) as avg_duration,
                       SUM(tokens_used) as total_tokens,
                       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as success_count
                FROM agent_metrics 
                WHERE start_time > ?
                GROUP BY agent_name
            """, (cutoff_time,)).fetchall()
            
            # Get recent activity
            recent_events = conn.execute("""
                SELECT te.*, t.file_name 
                FROM trace_events te
                JOIN traces t ON te.trace_id = t.trace_id
                WHERE te.timestamp > ?
                ORDER BY te.timestamp DESC
                LIMIT 50
            """, (cutoff_time,)).fetchall()
        
        # Calculate metrics
        total_requests = len(traces)
        successful_requests = sum(1 for t in traces if t['status'] == 'completed')
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        avg_response_time = sum(t['total_duration_ms'] or 0 for t in traces) / len(traces) if traces else 0
        total_tokens = sum(t['total_tokens'] for t in traces)
        
        # Agent performance
        agent_performance = {}
        for agent in agent_metrics:
            agent_performance[agent['agent_name']] = {
                'total_runs': agent['total_runs'],
                'avg_duration': int(agent['avg_duration'] or 0),
                'total_tokens': agent['total_tokens'],
                'success_rate': (agent['success_count'] / agent['total_runs'] * 100) if agent['total_runs'] > 0 else 0
            }
        
        # Recent activity
        activity_log = []
        for event in recent_events:
            activity_log.append({
                'timestamp': datetime.fromtimestamp(event['timestamp']).strftime('%H:%M:%S'),
                'function': event['agent_name'],
                'duration': event['duration_ms'] or 0,
                'status': event['status'],
                'tokens': event['tokens_used'] or 0,
                'file_name': event['file_name']
            })
        
        return {
            'total_requests': total_requests,
            'success_rate': round(success_rate, 1),
            'avg_response_time': int(avg_response_time),
            'total_tokens': total_tokens,
            'agent_performance': agent_performance,
            'recent_activity': activity_log,
            'estimated_cost': round(total_tokens * 0.00003, 4),  # Rough estimate
            'active_traces': len(self.active_traces)
        }
    
    def get_active_traces(self) -> List[Dict[str, Any]]:
        """Get all active traces"""
        with self.lock:
            return [asdict(trace) for trace in self.active_traces.values()]

# Global trace manager instance
trace_manager = TraceManager()
