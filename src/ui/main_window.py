from typing import Any, Dict
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QToolBar, QStatusBar, QSplitter,
    QProgressDialog, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon
import json
import traceback

from ..utils.resources import ICON_DIR
from ..core.schema_generator import SchemaGenerator
from ..utils.logger import logger
from ..utils.async_utils import HAS_QASYNC, asyncSlot
from .panels.description_panel import DescriptionPanel
from .panels.schema_panel import SchemaPanel
from .panels.test_panel import TestPanel
from .formatters import format_test_result
from ..core.tool_manager import ToolManager
from .dialogs.settings_dialog import SettingsDialog
from ..utils.config import config


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("Initializing main window")
        self.setWindowTitle("LuvlToolGen ❤️")
        self.setMinimumSize(1200, 800)
        self.current_schema = None
        self.tool_manager = ToolManager()

        # Set application and window icon
        icon_path = ICON_DIR / 'luvltoolgen.svg'
        if icon_path.exists():
            icon = QIcon(str(icon_path))
            self.setWindowIcon(icon)
            # Set the application-wide icon
            QApplication.setWindowIcon(icon)
        else:
            logger.warning(f"Icon not found at {icon_path}")

        self._check_dependencies()
        self._initialize_ui()

    def _check_dependencies(self):
        if not HAS_QASYNC:
            logger.warning("qasync not installed - some features may be limited")
            QMessageBox.warning(
                self,
                "Missing Dependency",
                "qasync is not installed. Some features might not work properly.\n"
                "Please install it using: pip install qasync"
            )

    def _initialize_ui(self):
        try:
            # Initialize services
            self.schema_generator = SchemaGenerator()

            # Initialize central widget
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
            self.main_layout = QHBoxLayout(self.central_widget)

            # Setup UI components
            self.setup_menu()
            self.setup_toolbars()
            self.setup_panels()

            # Set status bar
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)

            # Check if API key is set
            if not config.openai_api_key:
                self.status_bar.showMessage("Please set your OpenAI API key in settings", 5000)
                # Show settings dialog
                QMessageBox.information(
                    self,
                    "Welcome to LuvlToolGen",
                    "Welcome! To get started, please set your OpenAI API key in the settings."
                )
                self.on_settings_clicked()
            else:
                self.status_bar.showMessage("Ready")

            # Connect signals
            self._connect_signals()

            logger.info("Main window initialized successfully")

        except Exception as e:
            logger.critical(f"Failed to initialize main window: {str(e)}")
            logger.debug(f"Initialization error details: {traceback.format_exc()}")
            raise

    def _connect_signals(self):
        """Connect all panel signals"""
        self.description_panel.generate_button.clicked.connect(self.on_generate_clicked)
        self.test_panel.test_button.clicked.connect(self.on_test_clicked)

    def setup_menu(self):
        """Setup the main menu bar"""
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&File")

        # New Tool
        new_action = QAction("&New Tool", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.on_new_tool)
        file_menu.addAction(new_action)

        # Save Tool
        save_action = QAction("&Save Tool", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.on_save_tool)
        file_menu.addAction(save_action)

        # Load Tool
        load_action = QAction("&Load Tool", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.on_load_tool)
        file_menu.addAction(load_action)

        file_menu.addSeparator()
        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")

        # Test Function
        test_action = QAction("&Test Function", self)
        test_action.setShortcut("F5")
        test_action.triggered.connect(self.on_test_clicked)
        edit_menu.addAction(test_action)

        # Clear All
        clear_action = QAction("&Clear All", self)
        clear_action.setShortcut("Ctrl+L")
        clear_action.triggered.connect(self.on_clear_all)
        edit_menu.addAction(clear_action)

        # Copy Schema
        copy_schema_action = QAction("Copy &Schema", self)
        copy_schema_action.setShortcut("Ctrl+C")
        copy_schema_action.triggered.connect(self.on_copy_schema)
        edit_menu.addAction(copy_schema_action)

        # Help Menu
        help_menu = menubar.addMenu("&Help")

        # Documentation
        docs_action = QAction("&Documentation", self)
        docs_action.setShortcut("F1")
        docs_action.triggered.connect(self.on_show_docs)
        help_menu.addAction(docs_action)

        # About
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.on_show_about)
        help_menu.addAction(about_action)

    def setup_toolbars(self):
        """Setup the main toolbar"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        # Add toolbar actions with icons
        new_tool_action = QAction(QIcon(str(ICON_DIR / 'new.svg')), "New", self)
        new_tool_action.setStatusTip("Create new tool")
        new_tool_action.triggered.connect(self.on_new_tool)
        toolbar.addAction(new_tool_action)

        generate_action = QAction(QIcon(str(ICON_DIR / 'generate.svg')), "Generate", self)
        generate_action.setStatusTip("Generate schema from description")
        generate_action.triggered.connect(self.on_generate_clicked)
        toolbar.addAction(generate_action)

        test_action = QAction(QIcon(str(ICON_DIR / 'test.svg')), "Test", self)
        test_action.setStatusTip("Test the function")
        test_action.triggered.connect(self.on_test_clicked)
        toolbar.addAction(test_action)

        toolbar.addSeparator()

        settings_action = QAction(QIcon(str(ICON_DIR / 'settings.svg')), "Settings", self)
        settings_action.setStatusTip("Open settings")
        settings_action.triggered.connect(self.on_settings_clicked)
        toolbar.addAction(settings_action)

    def setup_panels(self):
        """Setup the three main panels"""
        splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(splitter)

        # Initialize panels
        self.description_panel = DescriptionPanel()
        self.schema_panel = SchemaPanel()
        self.test_panel = TestPanel()

        # Add panels to splitter
        splitter.addWidget(self.description_panel)
        splitter.addWidget(self.schema_panel)
        splitter.addWidget(self.test_panel)

        # Set initial sizes
        splitter.setSizes([400, 400, 400])

    @asyncSlot()
    async def on_generate_clicked(self):
        """Handle generate button click"""
        if not config.openai_api_key:
            reply = QMessageBox.question(
                self,
                "API Key Required",
                "OpenAI API key is not set. Would you like to set it now?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                self.on_settings_clicked()
            return
        description = self.description_panel.description_edit.toPlainText().strip()

        if not description:
            logger.warning("Generate clicked with empty description")
            self.status_bar.showMessage("Please enter a function description", 3000)
            return

        logger.info("Generating schema from description")
        logger.debug(f"Description: {description}")

        # Disable generate button
        self.description_panel.generate_button.setEnabled(False)
        self.description_panel.generate_button.setText("Generating...")

        # Show loading dialog
        progress = QProgressDialog("Generating schema...", "Cancel", 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None)
        progress.show()

        try:
            # Generate schema
            schema = await self.schema_generator.generate_schema(description)
            self.current_schema = schema  # Store the schema

            # Format and display schema
            formatted_schema = json.dumps(schema, indent=2)
            self.schema_panel.schema_edit.setPlainText(formatted_schema)

            # Update status and enable testing
            self.status_bar.showMessage("Schema generated successfully", 3000)
            self.test_panel.test_input_edit.setEnabled(True)
            self.test_panel.test_button.setEnabled(True)

            # Add example input template
            example_input = self._generate_example_input(schema)
            self.test_panel.test_input_edit.setPlainText(json.dumps(example_input, indent=2))

        except Exception as e:
            error_msg = f"Failed to generate schema: {str(e)}"
            logger.error(error_msg)
            logger.debug(f"Schema generation error details: {traceback.format_exc()}")

            self.status_bar.showMessage(f"Error: {str(e)}", 5000)
            QMessageBox.critical(self, "Error", error_msg)

        finally:
            # Re-enable generate button
            self.description_panel.generate_button.setEnabled(True)
            self.description_panel.generate_button.setText("Generate Schema")
            progress.close()

    @asyncSlot()
    async def on_test_clicked(self):
        """Handle test button click"""
        if not self.current_schema:
            self.status_bar.showMessage("Please generate a schema first", 3000)
            return

        try:
            # Parse test input
            test_input_text = self.test_panel.test_input_edit.toPlainText()
            try:
                test_input = json.loads(test_input_text)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON in test input. Please check the format.")

            # Disable test button and show progress
            self.test_panel.test_button.setEnabled(False)
            self.test_panel.test_button.setText("Testing...")
            self.test_panel.test_results_edit.setPlainText("Verifying tool call format...")

            # Show loading dialog
            progress = QProgressDialog("Testing function format...", "Cancel", 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setCancelButton(None)
            progress.show()

            # Test the function format
            result = await self.schema_generator.test_function(self.current_schema, test_input)

            # Use the formatter from formatters.py
            formatted_result = format_test_result(result)
            self.test_panel.test_results_edit.setPlainText(formatted_result)

            # Update status based on result
            if result["status"] == "success":
                self.status_bar.showMessage("Tool call format verified successfully", 3000)
            else:
                self.status_bar.showMessage("Tool call format verification failed", 3000)

        except ValueError as ve:
            self.status_bar.showMessage(str(ve), 5000)
            self.test_panel.test_results_edit.setPlainText(f"Error: {str(ve)}")

        except Exception as e:
            error_msg = f"Test failed: {str(e)}"
            logger.error(error_msg)
            logger.debug(f"Error details: {traceback.format_exc()}")

            self.status_bar.showMessage(error_msg, 5000)
            self.test_panel.test_results_edit.setPlainText(f"Error: {str(e)}")

        finally:
            self.test_panel.test_button.setEnabled(True)
            self.test_panel.test_button.setText("Test Format")
            if 'progress' in locals():
                progress.close()

    def _generate_example_input(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate example input based on the schema."""
        example = {}
        properties = schema.get('parameters', {}).get('properties', {})

        for param_name, param_schema in properties.items():
            param_type = param_schema.get('type', 'string')
            if param_type == 'string':
                example[param_name] = "example_string"
            elif param_type == 'number':
                example[param_name] = 0.0
            elif param_type == 'integer':
                example[param_name] = 0
            elif param_type == 'boolean':
                example[param_name] = False
            elif param_type == 'array':
                example[param_name] = []
            elif param_type == 'object':
                example[param_name] = {}

        return example

    def on_new_tool(self):
        """Handle new tool action"""
        if self.current_schema:
            reply = QMessageBox.question(
                self,
                "New Tool",
                "Do you want to create a new tool? Any unsaved changes will be lost.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        try:
            # Create new tool using tool manager
            new_tool = self.tool_manager.create_new_tool()

            # Clear all panels
            self.description_panel.description_edit.clear()
            self.schema_panel.schema_edit.clear()
            self.test_panel.test_input_edit.clear()
            self.test_panel.test_results_edit.clear()

            # Reset state
            self.current_schema = None
            self.test_panel.test_button.setEnabled(False)
            self.status_bar.showMessage("Created new tool", 3000)

            logger.info("New tool created")

        except Exception as e:
            error_msg = f"Failed to create new tool: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def on_save_tool(self):
        """Handle save tool action"""
        if not self.current_schema:
            QMessageBox.warning(
                self,
                "Save Tool",
                "No tool to save. Please generate a schema first."
            )
            return

        try:
            from PySide6.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Tool",
                str(self.tool_manager.save_dir),
                "Tool Files (*.json);;All Files (*)"
            )

            if file_path:
                # Prepare tool data
                tool_data = {
                    "description": self.description_panel.description_edit.toPlainText(),
                    "schema": self.current_schema,
                    "test_input": json.loads(self.test_panel.test_input_edit.toPlainText())
                    if self.test_panel.test_input_edit.toPlainText().strip()
                    else None
                }

                # Save using tool manager
                self.tool_manager.save_tool(file_path, tool_data)
                self.status_bar.showMessage(f"Tool saved to {file_path}", 3000)

        except Exception as e:
            error_msg = f"Failed to save tool: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def on_load_tool(self):
        """Handle load tool action"""
        try:
            from PySide6.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Load Tool",
                str(self.tool_manager.save_dir),
                "Tool Files (*.json);;All Files (*)"
            )

            if file_path:
                # Load using tool manager
                tool_data = self.tool_manager.load_tool(file_path)

                # Update UI
                self.description_panel.description_edit.setPlainText(tool_data["description"])
                self.current_schema = tool_data["schema"]
                self.schema_panel.schema_edit.setPlainText(
                    json.dumps(tool_data["schema"], indent=2)
                )

                # Handle test input if available
                if tool_data.get("test_input"):
                    self.test_panel.test_input_edit.setPlainText(
                        json.dumps(tool_data["test_input"], indent=2)
                    )
                    self.test_panel.test_button.setEnabled(True)

                self.status_bar.showMessage(f"Tool loaded from {file_path}", 3000)

        except Exception as e:
            error_msg = f"Failed to load tool: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def on_clear_all(self):
        """Clear all panels"""
        reply = QMessageBox.question(
            self,
            "Clear All",
            "Do you want to clear all panels? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.description_panel.description_edit.clear()
            self.schema_panel.schema_edit.clear()
            self.test_panel.test_input_edit.clear()
            self.test_panel.test_results_edit.clear()
            self.current_schema = None
            self.test_panel.test_button.setEnabled(False)
            self.status_bar.showMessage("All panels cleared", 3000)

    def on_copy_schema(self):
        """Copy schema to clipboard"""
        if not self.current_schema:
            self.status_bar.showMessage("No schema to copy", 3000)
            return

        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        schema_text = self.schema_panel.schema_edit.toPlainText()
        clipboard.setText(schema_text)
        self.status_bar.showMessage("Schema copied to clipboard", 3000)

    def on_show_docs(self):
        """Show documentation"""
        doc_text = """
LuvlToolGen Documentation

1. Creating a New Tool:
   - Click 'New Tool' or press Ctrl+N
   - Enter function description
   - Click 'Generate Schema'

2. Testing Your Tool:
   - After generation, modify test input if needed
   - Click 'Test Format' to verify

3. Saving/Loading:
   - Save your tool with Ctrl+S
   - Load existing tools with Ctrl+O

4. Keyboard Shortcuts:
   - New Tool: Ctrl+N
   - Save Tool: Ctrl+S
   - Load Tool: Ctrl+O
   - Test Function: F5
   - Clear All: Ctrl+L
   - Copy Schema: Ctrl+C
   - Documentation: F1
   - Exit: Ctrl+Q

For more information, visit:
https://github.com/yourusername/luvltoolgen
"""
        msg = QMessageBox(self)
        msg.setWindowTitle("LuvlToolGen Documentation")
        msg.setText(doc_text)
        msg.setStyleSheet("QLabel{min-width: 500px;}")
        msg.exec()

    def on_show_about(self):
        """Show about dialog"""
        about_text = """
LuvlToolGen ❤️

A delightful tool generator that turns simple schemas
into production-ready AI function calling tools
with love and care.

Version: 1.0.0
Author: Linh Nguyen
License: MIT

Built with:
- Python 3.11
- PySide6
- OpenAI API
"""
        msg = QMessageBox(self)
        msg.setWindowTitle("About LuvlToolGen")
        msg.setTextFormat(Qt.MarkdownText)
        msg.setText(about_text)
        msg.setIconPixmap(QIcon(str(ICON_DIR / 'luvltoolgen.svg')).pixmap(64, 64))
        msg.exec()


    def on_settings_clicked(self):
        """Show settings dialog"""
        try:
            dialog = SettingsDialog(self)
            if dialog.exec() == SettingsDialog.Accepted:
                # Reload settings
                self._apply_settings()
                self.status_bar.showMessage("Settings saved", 3000)
        except Exception as e:
            error_msg = f"Failed to open settings: {str(e)}"
            logger.error(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def _apply_settings(self):
        """Apply current settings to the UI"""
        try:
            # Apply dark mode if enabled
            if config.get_setting('DARK_MODE', 'false').lower() == 'true':
                self.setStyleSheet("""
                    QMainWindow, QWidget {
                        background-color: #2b2b2b;
                        color: #ffffff;
                    }
                    QTextEdit {
                        background-color: #363636;
                        color: #ffffff;
                        border: 1px solid #555555;
                    }
                    QPushButton {
                        background-color: #444444;
                        border: 1px solid #555555;
                        padding: 5px;
                        color: #ffffff;
                    }
                    QPushButton:hover {
                        background-color: #555555;
                    }
                    QLabel {
                        color: #ffffff;
                    }
                """)
            else:
                self.setStyleSheet("")

            # Apply help text visibility
            show_help = config.get_setting('SHOW_HELP', 'true').lower() == 'true'
            for panel in [self.description_panel, self.schema_panel, self.test_panel]:
                if hasattr(panel, 'description_help'):
                    panel.description_help.setVisible(show_help)

            # Update tool manager save directory
            self.tool_manager = ToolManager(config.get_setting('SAVE_DIR', 'saved_tools'))

            logger.info("Settings applied successfully")

        except Exception as e:
            logger.error(f"Failed to apply settings: {str(e)}")
            raise