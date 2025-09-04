#!/usr/bin/env python3
"""
World Config Manager
Configuration management for the World AI Agent System
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """Configuration manager for World"""
    
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.config_dir = self.base_path / "config"
        self.config_file = self.config_dir / "system.json"
        self.config = {}
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.config = self._get_default_config()
        else:
            self.config = self._get_default_config()
            self.save_config()
        
        return self.config
    
    def save_config(self):
        """Save configuration to file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "system": {
                "name": "World AI Agent System",
                "version": "1.0.0",
                "mode": "development"
            },
            "api": {
                "port": 8000,
                "host": "localhost",
                "cors_origins": ["*"]
            },
            "agents": {
                "orchestrator": {"enabled": True},
                "coding": {"enabled": True},
                "data": {"enabled": True},
                "communication": {"enabled": True},
                "business": {"enabled": True},
                "analytics": {"enabled": True}
            },
            "services": {
                "database": {"type": "sqlite", "path": "data/world.db"},
                "redis": {"enabled": False},
                "logging": {"level": "INFO"}
            }
        }
