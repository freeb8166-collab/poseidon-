#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from rich.console import Console
from rich.logging import RichHandler
from config import config

console = Console()

class SecurityLogger:
    """Logger personnalisé pour l'agent de sécurité"""
    
    def __init__(self, name: str = "SecurityAgent"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, config.log_level))
        
        handler = RichHandler(rich_tracebacks=True)
        handler.setLevel(getattr(logging, config.log_level))
        
        formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.history = []
        
    def info(self, message: str):
        self.logger.info(message)
        self.history.append({"level": "INFO", "message": message, "time": datetime.now()})
        
    def debug(self, message: str):
        self.logger.debug(message)
        self.history.append({"level": "DEBUG", "message": message, "time": datetime.now()})
        
    def error(self, message: str):
        self.logger.error(f"❌ {message}")
        self.history.append({"level": "ERROR", "message": message, "time": datetime.now()})
        
    def warning(self, message: str):
        self.logger.warning(f"⚠️ {message}")
        self.history.append({"level": "WARNING", "message": message, "time": datetime.now()})
        
    def success(self, message: str):
        self.logger.info(f"✅ {message}")
        self.history.append({"level": "SUCCESS", "message": message, "time": datetime.now()})
