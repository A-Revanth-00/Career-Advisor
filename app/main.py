from __future__ import annotations
import sys
import logging
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from app.core.config import APP_NAME, APP_VERSION
from app.database.database import init_database
from app.ui.main_window import MainWindow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

def main() -> None:
    logger.info("Starting %s v%s...", APP_NAME, APP_VERSION)

    # Enable High DPI and attribute flags
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Initialize local SQLite database
    init_database()

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    window = MainWindow()
    window.show()

    logger.info("Application window initialized and displayed.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
