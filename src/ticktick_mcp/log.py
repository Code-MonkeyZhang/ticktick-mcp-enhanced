import os
import logging
import sys
from datetime import datetime

def setup_logging(name: str = "ticktick_mcp"):
    """
    Configure logging based on MCP_LOG_ENABLE environment variable.
    
    - MCP_LOG_ENABLE=true: Log to logs/session_YYYYMMDD_HHMMSS.log, level INFO. No stderr.
    - Default: No logging (NullHandler).
    """
    # 1. Check Environment Variable
    log_enable = os.getenv("MCP_LOG_ENABLE", "").lower() == "true"
    
    root_logger = logging.getLogger()
    
    # Clear existing handlers to prevent duplication
    if root_logger.handlers:
        root_logger.handlers.clear()
        
    if not log_enable:
        # Case A: Logging Disabled (Default)
        # Set level to CRITICAL+1 to suppress almost everything
        root_logger.setLevel(logging.CRITICAL + 1)
        root_logger.addHandler(logging.NullHandler())
        return logging.getLogger(name)

    # Case B: Logging Enabled
    
    # 2. Determine log directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(current_dir)
    pkg_dir = os.path.dirname(src_dir)
    project_root = pkg_dir 
    
    log_dir = os.path.join(project_root, "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    # 3. Generate timestamped filename
    # Format: session_YYYYMMDD_HHMMSS.log
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"session_{timestamp}.log"
    log_file_path = os.path.join(log_dir, log_filename)
    
    # 4. Configure Root Logger
    root_logger.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File Handler (Standard FileHandler as requested for session logs)
    # We do not use RotatingFileHandler because we want one file per session.
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # 5. Suppress noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    return logging.getLogger(name)