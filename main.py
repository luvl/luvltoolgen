import sys
from PySide6.QtWidgets import QApplication
import asyncio
from src.ui.main_window import MainWindow
from src.utils.async_utils import HAS_QASYNC
from PySide6.QtGui import QIcon
from src.utils.resources import ICON_DIR

def main():
    app = QApplication(sys.argv)

    if HAS_QASYNC:
        # Setup async event loop with qasync
        from qasync import QEventLoop
        loop = QEventLoop(app)
        asyncio.set_event_loop(loop)
    else:
        # Fallback to regular event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Set application icon
    icon_path = ICON_DIR / 'luvltoolgen.svg'
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Create and show main window
    window = MainWindow()
    window.show()

    if HAS_QASYNC:
        # Run with qasync
        with loop:
            loop.run_forever()
    else:
        # Run without qasync
        sys.exit(app.exec())

if __name__ == "__main__":
    main()
