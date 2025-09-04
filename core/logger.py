#!/usr/bin/env python3
"""
World Logger
Enhanced logging system for the World AI Agent System
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

class WorldLogger:
    """Enhanced logging system for World"""
    
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.log_dir = self.base_path / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging configuration"""
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        
        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # File handler for detailed logs
        file_handler = logging.FileHandler(
            self.log_dir / "world_system.log"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
        
        # Console handler for simple output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
        
        # Create specific loggers
        self.system_logger = logging.getLogger("world.system")
        self.agent_logger = logging.getLogger("world.agents")
        self.api_logger = logging.getLogger("world.api")
        self.data_logger = logging.getLogger("world.data")
        
    def info(self, message: str, logger: str = "system"):
        """Log info message"""
        getattr(self, f"{logger}_logger").info(message)
    
    def error(self, message: str, logger: str = "system"):
        """Log error message"""
        getattr(self, f"{logger}_logger").error(message)
    
    def warning(self, message: str, logger: str = "system"):
        """Log warning message"""
        getattr(self, f"{logger}_logger").warning(message)
    
    def debug(self, message: str, logger: str = "system"):
        """Log debug message"""
        getattr(self, f"{logger}_logger").debug(message)
    
    def log_agent_action(self, agent_name: str, action: str, result: str = ""):
        """Log agent action"""
        message = f"Agent {agent_name}: {action}"
        if result:
            message += f" - {result}"
        self.agent_logger.info(message)
    
    def log_api_request(self, endpoint: str, method: str, status: int, duration: float):
        """Log API request"""
        message = f"{method} {endpoint} - {status} ({duration:.3f}s)"
        self.api_logger.info(message)
    
    def log_data_operation(self, operation: str, source: str, records: int):
        """Log data operation"""
        message = f"{operation} from {source} - {records} records"
        self.data_logger.info(message)
