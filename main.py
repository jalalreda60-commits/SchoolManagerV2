import sys
import os

# Add project root to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from PySide6.QtWidgets import QApplication, QSplashScreen, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QFont, QPainter, QColor, QLinearGradient

def create_splash(app):
    """Create and show a splash screen."""
    logo_path = os.path.join(BASE_DIR, 'assets', 'school_logo.png')

    # Create splash pixmap
    pixmap = QPixmap(500, 320)
    pixmap.fill(QColor("#0f0f23"))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Gradient background
    gradient = QLinearGradient(0, 0, 500, 320)
    gradient.setColorAt(0, QColor("#0f0f23"))
    gradient.setColorAt(1, QColor("#1a1a2e"))
    painter.fillRect(0, 0, 500, 320, gradient)

    # Border
    from PySide6.QtGui import QPen
    painter.setPen(QPen(QColor("#FF6B00"), 2))
    painter.drawRoundedRect(2, 2, 496, 316, 12, 12)

    # Logo
    if os.path.exists(logo_path):
        logo = QPixmap(logo_path).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        painter.drawPixmap(190, 40, logo)

    # Text
    painter.setPen(QColor("#FF6B00"))
    painter.setFont(QFont("Segoe UI", 22, QFont.Bold))
    painter.drawText(0, 185, 500, 35, Qt.AlignCenter, "Le Schéma")

    painter.setPen(QColor("#a0a0c0"))
    painter.setFont(QFont("Segoe UI", 11))
    painter.drawText(0, 215, 500, 25, Qt.AlignCenter, "Innover • Créer • Exceller")

    painter.setPen(QColor("#606080"))
    painter.setFont(QFont("Segoe UI", 9))
    painter.drawText(0, 250, 500, 20, Qt.AlignCenter, "Système de Gestion Scolaire v1.0")

    painter.setPen(QColor("#FF6B00"))
    painter.setFont(QFont("Segoe UI", 9))
    painter.drawText(0, 285, 500, 20, Qt.AlignCenter, "Chargement en cours...")

    painter.end()

    splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
    splash.show()
    app.processEvents()
    return splash


def main():
    # High DPI support
    os.environ.setdefault('QT_ENABLE_HIGHDPI_SCALING', '1')

    app = QApplication(sys.argv)
    app.setApplicationName("Le Schéma - Gestion Scolaire")
    app.setOrganizationName("Le Schéma")
    app.setApplicationVersion("1.0")

    # Show splash
    splash = create_splash(app)

    # Initialize database
    from models.database import init_db, Session
    init_db()
    session = Session()

    # Create directories
    for d in ['assets', 'documents', 'receipts', 'backups', 'reports', 'assets/photos']:
        os.makedirs(os.path.join(BASE_DIR, d), exist_ok=True)

    # Short delay for splash
    import time
    time.sleep(1.5)

    # Show login
    from ui.login_window import LoginWindow
    login_win = LoginWindow(session)

    def on_login_success(user):
        splash.finish(login_win)
        from ui.main_window import MainWindow
        main_win = MainWindow(session, user)
        main_win.show()
        # Keep reference to prevent GC
        app._main_win = main_win

    login_win.login_successful.connect(on_login_success)
    splash.finish(login_win)
    login_win.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
