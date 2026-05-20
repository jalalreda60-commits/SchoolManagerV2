import sys, os
from hashlib import sha256
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QCheckBox, QFrame, QMessageBox, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Signal, QPoint
from PySide6.QtGui import QPixmap, QFont, QColor, QPainter, QLinearGradient, QPen

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class LoginWindow(QWidget):
    login_successful = Signal(object)

    def __init__(self, session):
        super().__init__()
        self.session = session
        self.setWindowTitle("Le Schéma — Connexion")
        self.setFixedSize(480, 620)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._drag_pos = None
        self._pw_visible = False
        self.setup_ui()
        self.animate_in()

    def setup_ui(self):
        from themes.dark_theme import CARD, BORDER, ACCENT, PURPLE, TEXT, TEXT2, TEXT3, BG
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self.card = QFrame()
        self.card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #1e293b, stop:1 #0f172a);
                border-radius: 20px;
                border: 1px solid {BORDER};
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(60)
        shadow.setColor(QColor(59, 130, 246, 80))
        shadow.setOffset(0, 20)
        self.card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(44, 36, 44, 36)
        card_layout.setSpacing(0)

        # Close button
        close_row = QHBoxLayout()
        close_row.addStretch()
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(239,68,68,0.15); color: #ef4444;
                border: 1px solid rgba(239,68,68,0.3); border-radius: 14px;
                font-weight: bold; font-size: 11px;
            }}
            QPushButton:hover {{ background: rgba(239,68,68,0.3); }}
        """)
        close_btn.clicked.connect(sys.exit)
        close_row.addWidget(close_btn)
        card_layout.addLayout(close_row)
        card_layout.addSpacing(8)

        # Logo
        logo_lbl = QLabel()
        logo_path = os.path.join(BASE_DIR, 'assets', 'school_logo.png')
        if os.path.exists(logo_path):
            px = QPixmap(logo_path).scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_lbl.setPixmap(px)
        else:
            logo_lbl.setText("🎓")
            logo_lbl.setFont(QFont("Arial", 42))
        logo_lbl.setAlignment(Qt.AlignCenter)
        logo_lbl.setStyleSheet("background: transparent;")
        card_layout.addWidget(logo_lbl)
        card_layout.addSpacing(16)

        name_lbl = QLabel("Le Schéma")
        name_lbl.setAlignment(Qt.AlignCenter)
        name_lbl.setStyleSheet(f"background:transparent; color:{ACCENT}; font-size:26px; font-weight:700; letter-spacing:-0.5px;")
        card_layout.addWidget(name_lbl)
        card_layout.addSpacing(4)

        slogan_lbl = QLabel("Innover  ·  Créer  ·  Exceller")
        slogan_lbl.setAlignment(Qt.AlignCenter)
        slogan_lbl.setStyleSheet(f"background:transparent; color:{TEXT3}; font-size:11px; letter-spacing:2px;")
        card_layout.addWidget(slogan_lbl)
        card_layout.addSpacing(32)

        # Divider
        div = QFrame(); div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"background:{BORDER}; max-height:1px; border:none;")
        card_layout.addWidget(div)
        card_layout.addSpacing(28)

        # Sign in label
        signin_lbl = QLabel("Connexion")
        signin_lbl.setStyleSheet(f"background:transparent; color:{TEXT}; font-size:20px; font-weight:700;")
        card_layout.addWidget(signin_lbl)
        card_layout.addSpacing(4)
        sub_lbl = QLabel("Entrez vos identifiants pour accéder au système")
        sub_lbl.setStyleSheet(f"background:transparent; color:{TEXT2}; font-size:12px;")
        card_layout.addWidget(sub_lbl)
        card_layout.addSpacing(24)

        # Username
        u_lbl = QLabel("Nom d'utilisateur")
        u_lbl.setStyleSheet(f"background:transparent; color:{TEXT2}; font-size:12px; font-weight:600;")
        card_layout.addWidget(u_lbl)
        card_layout.addSpacing(6)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Identifiant")
        self.username_input.setText("admin")
        self.username_input.setFixedHeight(46)
        card_layout.addWidget(self.username_input)
        card_layout.addSpacing(16)

        # Password
        p_lbl = QLabel("Mot de passe")
        p_lbl.setStyleSheet(f"background:transparent; color:{TEXT2}; font-size:12px; font-weight:600;")
        card_layout.addWidget(p_lbl)
        card_layout.addSpacing(6)

        pw_row = QHBoxLayout()
        pw_row.setSpacing(0)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setText("admin123")
        self.password_input.setFixedHeight(46)
        self.password_input.returnPressed.connect(self.do_login)
        pw_row.addWidget(self.password_input)

        self.eye_btn = QPushButton("👁")
        self.eye_btn.setFixedSize(46, 46)
        self.eye_btn.setStyleSheet(f"""
            QPushButton {{
                background: #0f172a; color: {TEXT2}; border: 1px solid #1e3a5f;
                border-left: none; border-radius: 0 8px 8px 0; font-size: 16px;
            }}
            QPushButton:hover {{ color: {ACCENT}; }}
        """)
        self.eye_btn.clicked.connect(self.toggle_password)
        pw_row.addWidget(self.eye_btn)
        card_layout.addLayout(pw_row)
        card_layout.addSpacing(14)

        # Remember me
        self.remember_cb = QCheckBox("Se souvenir de moi")
        self.remember_cb.setStyleSheet(f"background:transparent; color:{TEXT2}; font-size:12px;")
        card_layout.addWidget(self.remember_cb)
        card_layout.addSpacing(8)

        # Error
        self.error_lbl = QLabel("")
        self.error_lbl.setStyleSheet(f"background:rgba(239,68,68,0.08); color:#ef4444; font-size:12px; border-radius:6px; padding:8px 12px;")
        self.error_lbl.setAlignment(Qt.AlignCenter)
        self.error_lbl.hide()
        card_layout.addWidget(self.error_lbl)
        card_layout.addSpacing(20)

        # Login button
        self.login_btn = QPushButton("  Se Connecter  →")
        self.login_btn.setFixedHeight(48)
        self.login_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {ACCENT}, stop:1 #8b5cf6);
                color: white; border: none; border-radius: 10px;
                font-size: 15px; font-weight: 700; letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #60a5fa, stop:1 {ACCENT});
            }}
            QPushButton:pressed {{ background: #1d4ed8; }}
        """)
        self.login_btn.clicked.connect(self.do_login)
        card_layout.addWidget(self.login_btn)
        card_layout.addStretch()

        footer = QLabel("© 2026 Le Schéma  ·  Système de Gestion Scolaire")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(f"background:transparent; color:{TEXT3}; font-size:10px;")
        card_layout.addWidget(footer)

        layout.addWidget(self.card)

    def toggle_password(self):
        self._pw_visible = not self._pw_visible
        self.password_input.setEchoMode(QLineEdit.Normal if self._pw_visible else QLineEdit.Password)

    def animate_in(self):
        self.setWindowOpacity(0)
        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(400)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.start()

    def do_login(self):
        from models.database import User
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            self.show_error("Veuillez remplir tous les champs")
            return
        hashed = sha256(password.encode()).hexdigest()
        user = self.session.query(User).filter_by(username=username, password=hashed, is_active=True).first()
        if user:
            from datetime import datetime
            user.last_login = datetime.now()
            self.session.commit()
            self.login_successful.emit(user)
            self.close()
        else:
            self.show_error("Identifiant ou mot de passe incorrect")
            self.shake()

    def show_error(self, msg):
        self.error_lbl.setText(f"⚠  {msg}")
        self.error_lbl.show()
        QTimer.singleShot(4000, self.error_lbl.hide)

    def shake(self):
        x, y = self.x(), self.y()
        for i in range(6):
            QTimer.singleShot(i * 50, lambda dx=((i%2)*2-1)*8: self.move(x+dx, y))
        QTimer.singleShot(300, lambda: self.move(x, y))

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() == Qt.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag_pos)
    def mouseReleaseEvent(self, e):
        self._drag_pos = None
