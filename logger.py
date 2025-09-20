"""
Centralized logging configuration for Schedule-Agent.
Provides structured logging with different levels and handlers.
"""

import logging
import sys
from typing import Optional
from datetime import datetime
import json
from config import settings

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)

class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)

def setup_logger(name: str = "schedule_agent", level: Optional[str] = None) -> logging.Logger:
    """Set up a logger with appropriate handlers and formatters."""
    
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Set log level
    log_level = getattr(logging, (level or settings.log_level).upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    if settings.debug:
        console_formatter = ColoredFormatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
        )
    else:
        console_formatter = JSONFormatter()
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler for production
    if not settings.debug:
        file_handler = logging.FileHandler(f"{name}.log")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
    
    return logger

# Global logger instance
logger = setup_logger()

def log_function_call(func_name: str, **kwargs):
    """Log function calls with parameters."""
    logger.debug(f"Calling {func_name} with params: {kwargs}")

def log_api_call(service: str, operation: str, **kwargs):
    """Log API calls to external services."""
    logger.info(f"API call to {service}: {operation}", extra={
        "service": service,
        "operation": operation,
        **kwargs
    })

def log_error(error: Exception, context: str = ""):
    """Log errors with context."""
    logger.error(f"Error in {context}: {str(error)}", exc_info=True)

def log_performance(operation: str, duration: float, **kwargs):
    """Log performance metrics."""
    logger.info(f"Performance: {operation} took {duration:.2f}s", extra={
        "operation": operation,
        "duration": duration,
        **kwargs
    })
