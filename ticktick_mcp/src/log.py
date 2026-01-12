import os
import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logging(name: str = "ticktick_mcp"):
    """
    配置统一的日志记录
    将日志同时输出到 logs/mcp.log 文件和 stderr
    """
    # 1. 确定日志目录路径
    # src/log.py -> src -> ticktick_mcp -> root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(current_dir)
    pkg_dir = os.path.dirname(src_dir)
    project_root = pkg_dir # ticktick-mcp-enhanced/
    
    log_dir = os.path.join(project_root, "logs")
    
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file = os.path.join(log_dir, "mcp.log")
    
    # 2. 配置 Root Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 清除现有的 handlers，防止重复
    if root_logger.handlers:
        root_logger.handlers.clear()
        
    # 3. Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 4. File Handler (Rotating)
    # 最大 5MB，保留 3 个备份
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # 5. Console Handler (stderr)
    # MCP Server 的 stdout 被占用，只能用 stderr
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 6. 抑制第三方库噪音
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    return logging.getLogger(name)
