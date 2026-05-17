import logging
import sys
import time
import functools
import inspect

def setup_logger(name: str):
    # Configure and return a standardized logger with console output and custom formatting
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(relativeCreated).2f ms] - %(message)s'
    )

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(handler)
        
    return logger

logger = setup_logger("agentic_profiler")

def log_execution_time(func):
    # Decorator to automatically log the start, completion, and duration of both sync and async functions
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"STARTED: {func.__name__}")
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"COMPLETED: {func.__name__} in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"FAILED: {func.__name__} after {duration:.2f}s with error: {e}")
            raise

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"STARTED: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"COMPLETED: {func.__name__} in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"FAILED: {func.__name__} after {duration:.2f}s with error: {e}")
            raise

    if inspect.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper
