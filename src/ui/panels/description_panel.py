from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton

class DescriptionPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.description_label = QLabel("Function Description:")
        self.description_help = QLabel(
            "Enter a natural language description of your function.\n"
            "Example: 'Create a function that gets the weather for a city\n"
            "and returns the temperature and conditions.'"
        )
        self.description_help.setStyleSheet("color: #666; font-weight: normal; font-size: 11px;")

        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText(
            "Enter your function description here...\n\n"
            "Be specific about:\n"
            "- What the function should do\n"
            "- What parameters it needs\n"
            "- What constraints should be applied"
        )

        self.generate_button = QPushButton("Generate Schema")

        self.layout.addWidget(self.description_label)
        self.layout.addWidget(self.description_help)
        self.layout.addWidget(self.description_edit)
        self.layout.addWidget(self.generate_button)
