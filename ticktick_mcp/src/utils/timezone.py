"""
Timezone handling utilities for TickTick MCP.

This module provides functions for converting UTC times to local times,
normalizing ISO date formats, and handling timezone-aware date operations.
"""

import os
import re
import logging
from datetime import datetime, date
from zoneinfo import ZoneInfo

# Set up logging
logger = logging.getLogger(__name__)

# Default timezone configuration
DEFAULT_TIMEZONE = os.getenv("TICKTICK_DISPLAY_TIMEZONE", "Local")


def convert_utc_to_local(utc_time_str: str, target_timezone: str = None) -> str:
    """
    将UTC时间字符串转换为指定时区或本地时区的时间
    
    Args:
        utc_time_str: UTC时间字符串，格式如 "2019-11-13T03:00:00+0000"
        target_timezone: 目标时区，如 "Asia/Shanghai"，None表示使用系统本地时区
        
    Returns:
        转换后的时间字符串，包含原始UTC时间和本地时间
    """
    if not utc_time_str:
        return utc_time_str
    
    try:
        # 解析UTC时间
        normalized_date = normalize_iso_date(utc_time_str)
        utc_dt = datetime.fromisoformat(normalized_date)
        
        # 确定目标时区：任务时区 > 配置时区 > 本地时区
        if not target_timezone and DEFAULT_TIMEZONE != "Local":
            target_timezone = DEFAULT_TIMEZONE
        
        # 转换为目标时区
        if target_timezone:
            # 如果指定了时区，尝试使用zoneinfo（Python 3.9+）
            try:
                local_dt = utc_dt.astimezone(ZoneInfo(target_timezone))
                timezone_name = target_timezone
            except (ImportError, Exception):
                # 降级到系统本地时区
                local_dt = utc_dt.astimezone()
                timezone_name = "Local"
        else:
            # 使用系统本地时区
            local_dt = utc_dt.astimezone()
            timezone_name = "Local"
        
        # 格式化返回
        local_time_str = local_dt.strftime("%Y-%m-%d %H:%M:%S")
        return f"{local_time_str} ({timezone_name}) [UTC: {utc_time_str}]"
        
    except (ValueError, TypeError) as e:
        # 如果转换失败，返回原始时间
        logger.warning(f"Failed to convert timezone for {utc_time_str}: {e}")
        return f"{utc_time_str} (UTC)"


def normalize_iso_date(date_str: str) -> str:
    """
    Normalize ISO date string to a format that Python's fromisoformat() can parse.
    
    Handles:
    - "Z" suffix → "+00:00"
    - "+0000" or "-0000" (no colon) → "+00:00" or "-00:00" (with colon)
    - Already correct formats remain unchanged
    
    Args:
        date_str: ISO date string in various formats
        
    Returns:
        Normalized ISO date string that fromisoformat() can parse
    """
    if not date_str:
        return date_str
    
    # Replace "Z" with "+00:00"
    normalized = date_str.replace("Z", "+00:00")
    
    # Handle "+0000" or "-0000" format (add colon before last 2 digits)
    # Match pattern: ends with +HHMM or -HHMM (4 digits after + or -)
    # Pattern: ends with + or - followed by exactly 4 digits
    pattern = r'([+-])(\d{2})(\d{2})$'
    match = re.search(pattern, normalized)
    if match:
        # Replace with format: +HH:MM
        normalized = re.sub(pattern, r'\1\2:\3', normalized)
    
    return normalized


def to_ticktick_date_format(date_str: str) -> str:
    """
    Convert ISO date string to TickTick API format.
    
    TickTick API requires timezone offset WITHOUT colon: +0800, not +08:00
    This is the reverse of normalize_iso_date().
    
    Handles:
    - "Z" suffix → "+0000"
    - "+08:00" (with colon) → "+0800" (without colon)
    - Already correct formats (+0800) remain unchanged
    
    Args:
        date_str: ISO date string in various formats
        
    Returns:
        Date string in TickTick API format (timezone offset without colon)
    """
    if not date_str:
        return date_str
    
    # Replace "Z" with "+0000"
    result = date_str.replace("Z", "+0000")
    
    # Remove colon from timezone offset: +08:00 -> +0800, -05:30 -> -0530
    # Match pattern: ends with +HH:MM or -HH:MM
    pattern = r'([+-])(\d{2}):(\d{2})$'
    result = re.sub(pattern, r'\1\2\3', result)
    
    return result


def get_user_timezone_today() -> date:
    """Get today's date in the user's timezone."""
    if DEFAULT_TIMEZONE and DEFAULT_TIMEZONE != "Local":
        try:
            user_tz = ZoneInfo(DEFAULT_TIMEZONE)
            return datetime.now(user_tz).date()
        except Exception:
            # Fallback to local timezone if user timezone is invalid
            pass
    return datetime.now().date()
