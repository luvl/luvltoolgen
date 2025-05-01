from pathlib import Path
import os
from typing import Dict

class Config:
    def __init__(self):
        # Base paths
        self.app_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.logs_dir = self.app_dir / 'logs'
        self.saved_tools_dir = self.app_dir / 'saved_tools'
        self.resources_dir = self.app_dir / 'resources'

        # Default settings
        self.default_settings = {
            'OPENAI_API_KEY': '',
            'OPENAI_MODEL': 'gpt-3.5-turbo',
            'OPENAI_TEMPERATURE': '0.7',
            'SAVE_DIR': str(self.saved_tools_dir),
            'AUTO_TEST': 'false',
            'SHOW_HELP': 'true',
            'DARK_MODE': 'false',
            'DEBUG': 'false'
        }

        # Initialize in-memory settings
        self.settings = self.default_settings.copy()

        # Load any environment variables that match our settings
        self._load_from_environment()
        self.update_from_settings(self.settings)

    def _load_from_environment(self):
        """Load settings from environment variables if they exist"""
        for key in self.default_settings.keys():
            env_value = os.environ.get(key)
            if env_value is not None:
                self.settings[key] = env_value

    def save_settings(self, new_settings: Dict[str, str]) -> None:
        """Update in-memory settings"""
        self.settings = {**self.default_settings, **new_settings}
        self.update_from_settings(self.settings)

    def update_from_settings(self, settings: dict):
        """Update config from settings"""
        self.openai_api_key = settings.get('OPENAI_API_KEY', '')
        self.openai_model = settings.get('OPENAI_MODEL', 'gpt-3.5-turbo')
        self.openai_temperature = float(settings.get('OPENAI_TEMPERATURE', '0.7'))
        self.debug = settings.get('DEBUG', 'false').lower() == 'true'

    def get_setting(self, key: str, default: str = '') -> str:
        """Get a specific setting value"""
        return self.settings.get(key, default)

    def reset_settings(self):
        """Reset settings to defaults"""
        self.settings = self.default_settings.copy()
        self.update_from_settings(self.settings)

# Create global config instance
config = Config()
