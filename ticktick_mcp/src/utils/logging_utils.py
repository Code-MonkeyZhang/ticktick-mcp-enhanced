import logging
import functools
from typing import Any, Callable

logger = logging.getLogger("ticktick_mcp")

def log_interaction(func: Callable) -> Callable:
    """
    Decorator to log MCP tool interactions (arguments and return values).
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        tool_name = func.__name__
        
        # Log invocation
        # Filter out sensitive or overly long arguments if necessary
        log_args = kwargs.copy()
        if args:
            log_args['_args'] = args
            
        logger.info(f"🤖 Tool Call [{tool_name}] | Args: {log_args}")
        
        try:
            # Execute function
            result = await func(*args, **kwargs)
            
            # Log result (truncated if too long)
            result_str = str(result)
            if len(result_str) > 500:
                result_str = result_str[:500] + "... (truncated)"
                
            logger.info(f"✅ Tool Success [{tool_name}] | Result: {result_str}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Tool Error [{tool_name}] | Error: {str(e)}")
            raise e
            
    return wrapper
