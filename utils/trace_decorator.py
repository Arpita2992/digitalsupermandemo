"""
Trace decorator for automatic performance tracking
"""

import functools
import time
from typing import Any, Callable
from utils.trace_manager import trace_manager

def trace_agent(agent_name: str):
    """Decorator to automatically trace agent performance"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Try to get trace_id from kwargs, args, or context
            trace_id = kwargs.get('trace_id')
            if not trace_id and len(args) > 0:
                # Check if first argument has trace_id attribute
                if hasattr(args[0], 'current_trace_id'):
                    trace_id = args[0].current_trace_id
                elif isinstance(args[0], dict) and 'trace_id' in args[0]:
                    trace_id = args[0]['trace_id']
            
            if not trace_id:
                # No trace_id found, execute without tracing
                return func(*args, **kwargs)
            
            # Log agent start
            start_time = time.time()
            trace_manager.log_event(
                trace_id=trace_id,
                event_type='agent_start',
                agent_name=agent_name,
                status='processing'
            )
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Calculate duration
                end_time = time.time()
                duration_ms = int((end_time - start_time) * 1000)
                
                # Extract token usage if available
                tokens_used = 0
                if isinstance(result, dict):
                    tokens_used = result.get('tokens_used', 0)
                elif hasattr(result, 'get'):
                    tokens_used = result.get('tokens_used', 0)
                
                # Log successful completion
                trace_manager.log_event(
                    trace_id=trace_id,
                    event_type='agent_complete',
                    agent_name=agent_name,
                    duration_ms=duration_ms,
                    tokens_used=tokens_used,
                    status='success'
                )
                
                return result
                
            except Exception as e:
                # Calculate duration for error case
                end_time = time.time()
                duration_ms = int((end_time - start_time) * 1000)
                
                # Log error
                trace_manager.log_event(
                    trace_id=trace_id,
                    event_type='agent_error',
                    agent_name=agent_name,
                    duration_ms=duration_ms,
                    status='error',
                    error_message=str(e)
                )
                
                raise e
        
        return wrapper
    return decorator

def get_current_trace_id():
    """Get the current trace ID from context (if available)"""
    # This would need to be implemented based on your context management
    # For now, return None
    return None

def set_trace_context(trace_id: str):
    """Set trace context for the current request"""
    # This would set the trace_id in thread-local storage or similar
    # For now, we'll handle this in the main application
    pass
