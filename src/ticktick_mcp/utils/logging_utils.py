import logging
import functools
from typing import Callable

logger = logging.getLogger("ticktick_mcp")

SENSITIVE_PARAMS = {"client_secret", "client_id", "password", "api_key", "token"}

def log_interaction(func: Callable) -> Callable:
    """
    Decorator to wrap MCP tool interactions.
    Logs tool calls while redacting sensitive parameters.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        tool_name = func.__name__

        safe_kwargs = {
            k: "***" if k in SENSITIVE_PARAMS else v
            for k, v in kwargs.items()
        }
        logger.info(f"▶️ Tool Call: {tool_name} | Args: {args} | Kwargs: {safe_kwargs}")

        try:
            result = await func(*args, **kwargs)

            logger.info(f"✅ Tool Success: {tool_name}")
            return result

        except Exception as e:
            logger.error(f"❌ Tool Error [{tool_name}] | Error: {str(e)}")
            raise e

    return wrapper
