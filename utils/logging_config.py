"""
Centralized logging configuration for Digital Superman
"""

import logging
import logging.handlers
import os
from datetime import datetime
import config


def setup_logging():
    """Configure application logging with proper handlers and formatting"""
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO if config.DEBUG else logging.WARNING)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # File handler - rotating daily
    file_handler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(log_dir, 'digital_superman.log'),
        when='midnight',
        interval=1,
        backupCount=30,  # Keep 30 days of logs
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Error file handler - for errors only
    error_handler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(log_dir, 'digital_superman_errors.log'),
        when='midnight',
        interval=1,
        backupCount=90,  # Keep 90 days of error logs
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # Security handler - for security events
    security_handler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(log_dir, 'security.log'),
        when='midnight',
        interval=1,
        backupCount=365,  # Keep 1 year of security logs
        encoding='utf-8'
    )
    security_handler.setLevel(logging.WARNING)
    security_handler.setFormatter(detailed_formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    
    # Configure specific loggers
    
    # Security logger
    security_logger = logging.getLogger('security')
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.WARNING)
    security_logger.propagate = False
    
    # Performance logger
    performance_logger = logging.getLogger('performance')
    performance_handler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(log_dir, 'performance.log'),
        when='midnight',
        interval=1,
        backupCount=7,  # Keep 1 week of performance logs
        encoding='utf-8'
    )
    performance_handler.setFormatter(detailed_formatter)
    performance_logger.addHandler(performance_handler)
    performance_logger.setLevel(logging.INFO)
    performance_logger.propagate = False
    
    # AI Agents logger
    ai_logger = logging.getLogger('ai_agents')
    ai_handler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(log_dir, 'ai_agents.log'),
        when='midnight',
        interval=1,
        backupCount=14,  # Keep 2 weeks of AI logs
        encoding='utf-8'
    )
    ai_handler.setFormatter(detailed_formatter)
    ai_logger.addHandler(ai_handler)
    ai_logger.setLevel(logging.INFO)
    ai_logger.propagate = False
    
    # Suppress noisy external libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('azure').setLevel(logging.WARNING)
    
    # Log startup information
    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info("Digital Superman Application Starting")
    logger.info(f"Environment: {config.ENV}")
    logger.info(f"Debug Mode: {config.DEBUG}")
    logger.info(f"Log Directory: {log_dir}")
    logger.info("=" * 50)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name"""
    return logging.getLogger(name)


def log_security_event(event_type: str, details: str, user_ip: str = None, filename: str = None):
    """Log security-related events"""
    security_logger = logging.getLogger('security')
    extra_info = []
    if user_ip:
        extra_info.append(f"IP: {user_ip}")
    if filename:
        extra_info.append(f"File: {filename}")
    
    extra_str = f" ({', '.join(extra_info)})" if extra_info else ""
    security_logger.warning(f"SECURITY EVENT - {event_type}: {details}{extra_str}")


def log_performance_metric(metric_name: str, value: float, unit: str = "seconds"):
    """Log performance metrics"""
    performance_logger = logging.getLogger('performance')
    performance_logger.info(f"METRIC - {metric_name}: {value:.4f} {unit}")


def log_ai_interaction(agent_name: str, action: str, duration: float = None, success: bool = True, error: str = None):
    """Log AI agent interactions"""
    ai_logger = logging.getLogger('ai_agents')
    status = "SUCCESS" if success else "FAILED"
    duration_str = f" ({duration:.2f}s)" if duration else ""
    error_str = f" - Error: {error}" if error else ""
    
    ai_logger.info(f"AI - {agent_name}: {action} - {status}{duration_str}{error_str}")


# Initialize logging when module is imported
setup_logging()
