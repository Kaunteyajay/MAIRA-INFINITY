"""
Configuration Management

TOML-based configuration with defaults, validation, and secure key storage.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional
import tomllib as tomli
import tomli_w

logger = logging.getLogger(__name__)

class Config:
    """Application configuration manager."""
    
    def __init__(self, config_path: Optional[Path] = None, data_dir: Optional[Path] = None):
        # Default paths
        self.data_dir = data_dir or Path.home() / ".maira"
        self.config_path = config_path or self.data_dir / "config.toml"
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration data
        self._config: Dict[str, Any] = {}
        self._defaults = self._get_defaults()
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "general": {
                "language": "auto",
                "start_minimized": False,
                "enable_telemetry": True
            },
            "llm": {
                "default_provider": "claude",
                "fallback": ["openai", "ollama"],
                "keys": {
                    # Keys stored in OS keyring, not in config file
                }
            },
            "voice": {
                "stt_model": "small",
                "tts_voice": "en-IN-NeerjaNeural",
                "push_to_talk_key": "ctrl+space",
                "wake_word": "",
                "enable_barge_in": True
            },
            "avatar": {
                "style": "default",
                "animation_quality": "high",
                "enable_emotions": True,
                "enable_particles": True
            },
            "permissions": {
                "file_scopes": [],
                "system_control": "ask",
                "code_execution": "allow_in_scope",
                "web_search": "allow",
                "internet_control": "ask"
            },
            "ui": {
                "theme": "neon-blue",
                "reduce_motion": False,
                "scale": 1.0,
                "opacity": 0.95
            }
        }
    
    async def load(self) -> None:
        """Load configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, "rb") as f:
                    self._config = tomli.load(f)
                logger.info(f"Loaded config from {self.config_path}")
            else:
                self._config = {}
                logger.info("Using default configuration")
            
            # Merge with defaults
            self._config = self._merge_with_defaults(self._config, self._defaults)
            
            # Save to ensure file exists with defaults
            await self.save()
            
        except Exception as e:
            logger.warning(f"Error loading config: {e}, using defaults")
            self._config = self._defaults.copy()
    
    async def save(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_path, "wb") as f:
                tomli_w.dump(self._config, f)
            logger.debug(f"Saved config to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation (e.g., 'llm.default_provider')."""
        keys = key.split(".")
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by dot notation."""
        keys = key.split(".")
        config = self._config
        
        # Navigate to parent
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set value
        config[keys[-1]] = value
    
    def _merge_with_defaults(self, config: Dict, defaults: Dict) -> Dict:
        """Recursively merge config with defaults."""
        result = defaults.copy()
        
        for key, value in config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_with_defaults(value, result[key])
            else:
                result[key] = value
        
        return result
    
    @property
    def dev_mode(self) -> bool:
        """Check if development mode is enabled."""
        return self.get("general.dev_mode", False)