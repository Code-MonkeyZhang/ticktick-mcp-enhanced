import logging
import functools
from typing import Any, Callable

logger = logging.getLogger("ticktick_mcp")

def log_interaction(func: Callable) -> Callable:
    """
    Decorator to wrap MCP tool interactions (formerly for logging, now just error propagation).
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        tool_name = func.__name__
        
        logger.info(f"▶️ Tool Call: {tool_name} | Args: {args} | Kwargs: {kwargs}")
            
        try:
            # Execute function
            result = await func(*args, **kwargs)
            
            logger.info(f"✅ Tool Success: {tool_name}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Tool Error [{tool_name}] | Error: {str(e)}")
            raise e
            
    return wrapper
