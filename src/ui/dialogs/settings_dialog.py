from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QFormLayout, QGroupBox,
    QCheckBox, QSpinBox, QMessageBox
)
from ...utils.config import config
from ...utils.logger import logger

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)

        # Load current settings
        self.current_settings = config.settings

        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # OpenAI Settings
        openai_group = QGroupBox("OpenAI Settings")
        openai_layout = QFormLayout()

        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        openai_layout.addRow("API Key:", self.api_key_edit)

        self.model_edit = QLineEdit()
        openai_layout.addRow("Model:", self.model_edit)

        self.temperature_spin = QSpinBox()
        self.temperature_spin.setRange(0, 20)  # 0.0 to 2.0
        self.temperature_spin.setSingleStep(1)
        openai_layout.addRow("Temperature (x0.1):", self.temperature_spin)

        openai_group.setLayout(openai_layout)
        layout.addWidget(openai_group)

        # Tool Settings
        tool_group = QGroupBox("Tool Settings")
        tool_layout = QFormLayout()

        self.save_dir_edit = QLineEdit()
        tool_layout.addRow("Save Directory:", self.save_dir_edit)

        self.auto_test_check = QCheckBox("Auto-test after generation")
        tool_layout.addRow("", self.auto_test_check)

        tool_group.setLayout(tool_layout)
        layout.addWidget(tool_group)

        # UI Settings
        ui_group = QGroupBox("UI Settings")
        ui_layout = QFormLayout()

        self.show_help_check = QCheckBox("Show help text")
        ui_layout.addRow("", self.show_help_check)

        self.dark_mode_check = QCheckBox("Dark mode")
        ui_layout.addRow("", self.dark_mode_check)

        ui_group.setLayout(ui_layout)
        layout.addWidget(ui_group)

        # Buttons
        button_layout = QHBoxLayout()

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def load_settings(self):
        """Load current settings into UI"""
        self.api_key_edit.setText(config.get_setting('OPENAI_API_KEY', ''))
        self.model_edit.setText(config.get_setting('OPENAI_MODEL', 'gpt-3.5-turbo'))
        self.temperature_spin.setValue(int(float(config.get_setting('OPENAI_TEMPERATURE', '0.7')) * 10))
        self.save_dir_edit.setText(config.get_setting('SAVE_DIR', 'saved_tools'))
        self.auto_test_check.setChecked(config.get_setting('AUTO_TEST', 'false').lower() == 'true')
        self.show_help_check.setChecked(config.get_setting('SHOW_HELP', 'true').lower() == 'true')
        self.dark_mode_check.setChecked(config.get_setting('DARK_MODE', 'false').lower() == 'true')

    def save_settings(self):
        """Save settings and close dialog"""
        try:
            settings = {
                'OPENAI_API_KEY': self.api_key_edit.text(),
                'OPENAI_MODEL': self.model_edit.text(),
                'OPENAI_TEMPERATURE': str(self.temperature_spin.value() / 10.0),
                'SAVE_DIR': self.save_dir_edit.text(),
                'AUTO_TEST': str(self.auto_test_check.isChecked()).lower(),
                'SHOW_HELP': str(self.show_help_check.isChecked()).lower(),
                'DARK_MODE': str(self.dark_mode_check.isChecked()).lower()
            }

            config.save_settings(settings)

            # Try to initialize the client with new settings
            try:
                if hasattr(self.parent(), 'schema_generator'):
                    self.parent().schema_generator._initialize_client()
                    self.parent().status_bar.showMessage("Settings saved and API connection verified", 3000)
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "API Connection Warning",
                    f"Settings saved but API connection failed: {str(e)}\n"
                    "Please verify your API key."
                )

            self.accept()

        except Exception as e:
            logger.error(f"Failed to save settings: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save settings: {str(e)}"
            )
