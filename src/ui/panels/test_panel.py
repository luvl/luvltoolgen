from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton

class TestPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.test_label = QLabel("Test Input:")
        self.test_help = QLabel(
            "Enter JSON input to test if OpenAI can correctly\n"
            "use this function schema in its tool calling format.\n"
            "Example input will be automatically generated."
        )
        self.test_help.setStyleSheet("color: #666; font-weight: normal; font-size: 11px;")

        self.test_input_edit = QTextEdit()
        self.test_input_edit.setPlaceholderText("Enter test input here in JSON format...")
        self.test_input_edit.setMaximumHeight(150)

        self.test_button = QPushButton("Test Format")
        self.test_button.setEnabled(False)

        self.results_label = QLabel("Test Results:")
        self.results_help = QLabel(
            "This shows if OpenAI can successfully create a tool call\n"
            "using your schema. A successful result means OpenAI understood\n"
            "how to use your function and provided valid arguments."
        )
        self.results_help.setStyleSheet("color: #666; font-weight: normal; font-size: 11px;")

        self.test_results_edit = QTextEdit()
        self.test_results_edit.setReadOnly(True)
        self.test_results_edit.setPlaceholderText(
            "Test results will show:\n"
            "- If OpenAI can use your function schema\n"
            "- The exact tool call OpenAI would make\n"
            "- The arguments OpenAI would pass to your function"
        )

        self.layout.addWidget(self.test_label)
        self.layout.addWidget(self.test_help)
        self.layout.addWidget(self.test_input_edit)
        self.layout.addWidget(self.test_button)
        self.layout.addWidget(self.results_label)
        self.layout.addWidget(self.results_help)
        self.layout.addWidget(self.test_results_edit)
