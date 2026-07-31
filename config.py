#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator
import logging

# Chargement des variables d'environnement
load_dotenv()

class AgentCapabilities(BaseModel):
    """Capabilités de l'agent"""
    system_modification: bool = Field(default=True)
    apk_install: bool = Field(default=True)
    account_creation: bool = Field(default=True)
    file_modification: bool = Field(default=True)
    terminal_access: bool = Field(default=True)
    root_operations: bool = Field(default=False)  # Par défaut désactivé
    network_access: bool = Field(default=True)
    app_control: bool = Field(default=True)

class SecurityConfig(BaseModel):
    """Configuration de sécurité"""
    allowed_targets: List[str] = Field(default=["localhost", "127.0.0.1", "*.local", "*.test"])
    blocked_commands: List[str] = Field(default=[
        "rm -rf /", "dd if=", "mkfs", "format",
        "chown -R", "chmod -R 777", "mount",
        "systemctl stop", "kill -9"
    ])
    require_confirmation: bool = Field(default=True)
    confirmation_timeout: int = Field(default=30)
    max_retries: int = Field(default=3)
    audit_log_enabled: bool = Field(default=True)

class AgentConfig(BaseModel):
    """Configuration principale de l'agent"""
    
    # API
    api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    api_url: str = Field(default=os.getenv("API_URL", "https://openrouter.ai/api/v1/chat/completions"))
    model: str = Field(default=os.getenv("MODEL", "gpt-4"))
    max_tokens: int = Field(default=int(os.getenv("MAX_TOKENS", "4000")))
    temperature: float = Field(default=float(os.getenv("TEMPERATURE", "0.7")))
    
    # Agent
    name: str = Field(default=os.getenv("AGENT_NAME", "SecurityAgentV1"))
    version: str = Field(default=os.getenv("AGENT_VERSION", "1.0.0"))
    mode: str = Field(default=os.getenv("MODE", "COMPLETE"))
    
    # Capacités
    capabilities: AgentCapabilities = Field(default_factory=AgentCapabilities)
    
    # Sécurité
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    
    # Chemins
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent)
    reports_dir: Path = Field(default_factory=lambda: Path(__file__).parent / "reports")
    logs_dir: Path = Field(default_factory=lambda: Path(__file__).parent / "logs")
    backups_dir: Path = Field(default_factory=lambda: Path(__file__).parent / "backups")
    database_path: Path = Field(default_factory=lambda: Path(__file__).parent / "database" / "memory.sqlite")
    
    # Android
    termux_home: Path = Field(default=Path(os.getenv("TERMUX_HOME", "/data/data/com.termux/files/home")))
    storage_path: Path = Field(default=Path(os.getenv("STORAGE_PATH", "/storage/emulated/0")))
    root_path: Path = Field(default=Path(os.getenv("SYSTEM_ROOT_PATH", "/")))
    
    # Logging
    log_level: str = Field(default=os.getenv("LOG_LEVEL", "DEBUG"))
    log_all_actions: bool = Field(default=os.getenv("LOG_ALL_ACTIONS", "true").lower() == "true")
    save_logs: bool = Field(default=os.getenv("SAVE_LOGS", "true").lower() == "true")
    
    @validator('mode')
    def validate_mode(cls, v):
        if v not in ['COMPLETE', 'AUDIT_ONLY', 'SAFE']:
            raise ValueError(f"Mode invalide: {v}. Doit être COMPLETE, AUDIT_ONLY ou SAFE")
        return v
    
    @validator('api_key')
    def validate_api_key(cls, v):
        if not v or len(v) < 10:
            raise ValueError("Clé API invalide ou manquante")
        return v
    
    class Config:
        arbitrary_types_allowed = True

# Instance de configuration
config = AgentConfig()

# Création des dossiers
config.reports_dir.mkdir(exist_ok=True)
config.logs_dir.mkdir(exist_ok=True)
config.backups_dir.mkdir(exist_ok=True)
config.database_path.parent.mkdir(exist_ok=True)

# Configuration du logging
def setup_logging():
    from loguru import logger
    import sys
    
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
        level=config.log_level
    )
    logger.add(
        config.logs_dir / "agent.log",
        rotation="500 MB",
        retention="10 days",
        format="{time} | {level} | {name} - {message}",
        level=config.log_level
    )
    return logger

logger = setup_logging()
