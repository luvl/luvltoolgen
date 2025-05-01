from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit

class SchemaPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.schema_label = QLabel("Generated Schema:")
        self.schema_help = QLabel(
            "This is the OpenAI-compatible function schema.\n"
            "It defines the function's parameters and their types\n"
            "in a format that OpenAI can understand and use."
        )
        self.schema_help.setStyleSheet("color: #666; font-weight: normal; font-size: 11px;")

        self.schema_edit = QTextEdit()
        self.schema_edit.setReadOnly(True)
        self.schema_edit.setPlaceholderText(
            "The generated schema will appear here...\n\n"
            "It will include:\n"
            "- Function name and description\n"
            "- Parameter definitions\n"
            "- Type constraints and validations"
        )

        self.layout.addWidget(self.schema_label)
        self.layout.addWidget(self.schema_help)
        self.layout.addWidget(self.schema_edit)
