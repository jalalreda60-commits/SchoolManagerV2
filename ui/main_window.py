import os, sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QSizePolicy,
    QLineEdit, QMessageBox, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPixmap, QFont, QIcon, QColor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NAV_ITEMS = [
    ("📊", "Tableau de Bord"),
    ("🎓", "Élèves"),
    ("💳", "Paiements"),
    ("👨‍🏫", "Enseignants"),
    ("👥", "Employés"),
    ("📉", "Dépenses"),
    ("🚌", "Transport"),
    ("📅", "Emploi du Temps"),
    ("📋", "Rapports"),
    ("⚙",  "Paramètres"),
]

class NavBtn(QPushButton):
    def __init__(self, icon, text):
        super().__init__()
        self.setObjectName("navBtn")
        self.setText(f"  {icon}   {text}")
        self.setCheckable(True)
        self.setFixedHeight(44)
        self.setCursor(Qt.PointingHandCursor)
        self.setFont(QFont("Segoe UI", 12))


class MainWindow(QMainWindow):
    def __init__(self, session, current_user):
        super().__init__()
        self.session = session
        self.current_user = current_user
        self.setWindowTitle("Le Schéma — ERP Scolaire")
        self.setMinimumSize(1280, 780)
        self.showMaximized()
        icon_path = os.path.join(BASE_DIR, 'assets', 'school_logo.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self._nav_btns = []
        self._setup_ui()
        self._init_pages()
        self.navigate_to(0)

    def _setup_ui(self):
        from themes.dark_theme import ERP_THEME
        self.setStyleSheet(ERP_THEME)

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar ───────────────────────────────────────────────────────────
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(240)
        sb = QVBoxLayout(self.sidebar)
        sb.setContentsMargins(12, 16, 12, 16)
        sb.setSpacing(2)

        # Logo block
        logo_frame = QFrame()
        logo_frame.setStyleSheet("background: transparent;")
        lf = QVBoxLayout(logo_frame)
        lf.setContentsMargins(8, 4, 8, 12)
        lf.setSpacing(6)
        logo_lbl = QLabel()
        lpath = os.path.join(BASE_DIR, 'assets', 'school_logo.png')
        if os.path.exists(lpath):
            px = QPixmap(lpath).scaled(56, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_lbl.setPixmap(px)
        else:
            logo_lbl.setText("🎓"); logo_lbl.setFont(QFont("Arial", 28))
        logo_lbl.setAlignment(Qt.AlignCenter)
        logo_lbl.setStyleSheet("background: transparent;")
        lf.addWidget(logo_lbl)
        name_lbl = QLabel("Le Schéma")
        name_lbl.setStyleSheet("background:transparent; color:#3b82f6; font-size:16px; font-weight:700;")
        name_lbl.setAlignment(Qt.AlignCenter)
        lf.addWidget(name_lbl)
        slogan_lbl = QLabel("ERP Scolaire")
        slogan_lbl.setStyleSheet("background:transparent; color:#475569; font-size:10px; letter-spacing:1px;")
        slogan_lbl.setAlignment(Qt.AlignCenter)
        lf.addWidget(slogan_lbl)
        sb.addWidget(logo_frame)

        # Divider
        d1 = QFrame(); d1.setFrameShape(QFrame.HLine)
        d1.setStyleSheet("background:#1e3a5f; max-height:1px; border:none; margin:4px 8px;")
        sb.addWidget(d1)
        sb.addSpacing(8)

        # Nav section label
        nav_label = QLabel("NAVIGATION")
        nav_label.setStyleSheet("background:transparent; color:#334155; font-size:10px; font-weight:600; letter-spacing:2px; padding-left:14px;")
        sb.addWidget(nav_label)
        sb.addSpacing(4)

        for i, (icon, text) in enumerate(NAV_ITEMS):
            btn = NavBtn(icon, text)
            btn.clicked.connect(lambda checked, idx=i: self.navigate_to(idx))
            sb.addWidget(btn)
            self._nav_btns.append(btn)

        sb.addStretch()

        # Divider
        d2 = QFrame(); d2.setFrameShape(QFrame.HLine)
        d2.setStyleSheet("background:#1e3a5f; max-height:1px; border:none; margin:4px 8px;")
        sb.addWidget(d2)
        sb.addSpacing(8)

        # User block
        role_colors = {"Admin":"#3b82f6","Comptable":"#22c55e","Secrétaire":"#8b5cf6"}
        rc = role_colors.get(self.current_user.role, "#94a3b8")
        user_frame = QFrame()
        user_frame.setStyleSheet(f"background:rgba(59,130,246,0.06); border:1px solid #1e3a5f; border-radius:10px;")
        uf = QVBoxLayout(user_frame)
        uf.setContentsMargins(12, 10, 12, 10)
        uf.setSpacing(3)
        uname = QLabel(f"👤  {self.current_user.full_name or self.current_user.username}")
        uname.setStyleSheet(f"background:transparent; color:{rc}; font-size:12px; font-weight:600;")
        uf.addWidget(uname)
        urole = QLabel(f"     {self.current_user.role}")
        urole.setStyleSheet("background:transparent; color:#475569; font-size:11px;")
        uf.addWidget(urole)
        logout_btn = QPushButton("🚪  Déconnexion")
        logout_btn.setStyleSheet("""
            QPushButton{background:transparent; color:#475569; border:none;
                        font-size:11px; text-align:left; padding:2px 0;}
            QPushButton:hover{color:#ef4444;}
        """)
        logout_btn.clicked.connect(self.logout)
        uf.addWidget(logout_btn)
        sb.addWidget(user_frame)
        root.addWidget(self.sidebar)

        # ── Right pane ─────────────────────────────────────────────────────────
        right = QWidget()
        right.setStyleSheet("background:#0f172a;")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)

        # Top bar
        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setFixedHeight(58)
        tl = QHBoxLayout(topbar)
        tl.setContentsMargins(24, 0, 20, 0)
        tl.setSpacing(14)

        self._page_title = QLabel("Tableau de Bord")
        self._page_title.setStyleSheet("color:#f8fafc; font-size:16px; font-weight:600;")
        tl.addWidget(self._page_title)
        tl.addStretch()

        # Search bar
        search = QLineEdit()
        search.setPlaceholderText("🔍  Recherche rapide...")
        search.setFixedSize(240, 34)
        search.setStyleSheet("""
            QLineEdit{background:#0f172a; color:#94a3b8; border:1px solid #1e3a5f;
                      border-radius:8px; padding:0 12px; font-size:12px;}
            QLineEdit:focus{border-color:#3b82f6; color:#f8fafc;}
        """)
        tl.addWidget(search)

        # Clock
        self._clock = QLabel()
        self._clock.setStyleSheet("""
            background:rgba(59,130,246,0.1); color:#60a5fa;
            border:1px solid rgba(59,130,246,0.25); border-radius:8px;
            padding:6px 12px; font-size:13px; font-weight:600;
        """)
        self._update_clock()
        tl.addWidget(self._clock)
        self._clock_timer = QTimer()
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(1000)

        rl.addWidget(topbar)

        # Stack
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background:#0f172a;")
        rl.addWidget(self.stack)
        root.addWidget(right)

        self.statusBar().showMessage(
            f"✅  Connecté: {self.current_user.username}  ({self.current_user.role})  ·  Base: school.db")

    def _init_pages(self):
        from ui.dashboard import DashboardWidget
        from ui.students import StudentsWidget
        from ui.payments import PaymentsWidget
        from ui.employees import EmployeesWidget
        from ui.employees import EmployeesWidget as TeachersWidget
        from ui.expenses import ExpensesWidget
        from ui.transport_timetable import TransportWidget, TimetableWidget
        from ui.reports import ReportsWidget
        from ui.settings import SettingsWidget

        builders = [
            lambda: DashboardWidget(self.session, self.current_user),
            lambda: StudentsWidget(self.session, self.current_user),
            lambda: PaymentsWidget(self.session, self.current_user),
            lambda: TeachersWidget(self.session, self.current_user),
            lambda: EmployeesWidget(self.session, self.current_user),
            lambda: ExpensesWidget(self.session, self.current_user),
            lambda: TransportWidget(self.session, self.current_user),
            lambda: TimetableWidget(self.session, self.current_user),
            lambda: ReportsWidget(self.session, self.current_user),
            lambda: SettingsWidget(self.session, self.current_user),
        ]
        for fn in builders:
            try:
                w = fn()
            except Exception as e:
                w = QLabel(f"Erreur: {e}")
                w.setAlignment(Qt.AlignCenter)
                w.setStyleSheet("color:#ef4444;")
            self.stack.addWidget(w)

    def navigate_to(self, idx):
        for i, btn in enumerate(self._nav_btns):
            btn.setChecked(i == idx)
        self.stack.setCurrentIndex(idx)
        titles = [n[1] for n in NAV_ITEMS]
        if idx < len(titles):
            self._page_title.setText(f"{NAV_ITEMS[idx][0]}  {titles[idx]}")
        w = self.stack.currentWidget()
        for attr in ('load_data', 'load_students', 'load_payments', 'load_employees', 'load_expenses'):
            if hasattr(w, attr):
                try: getattr(w, attr)()
                except: pass
                break

    def _update_clock(self):
        self._clock.setText(datetime.now().strftime("🕐  %H:%M:%S"))

    def logout(self):
        if QMessageBox.question(self, "Déconnexion", "Se déconnecter?",
                QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            self.close()
            from ui.login_window import LoginWindow
            self._login = LoginWindow(self.session)
            self._login.login_successful.connect(self._on_relogin)
            self._login.show()

    def _on_relogin(self, user):
        self.current_user = user
        self.show()
        self.navigate_to(0)

from datetime import datetime
