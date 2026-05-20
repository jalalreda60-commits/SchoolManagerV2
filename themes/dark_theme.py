# ── Color tokens ──────────────────────────────────────────────────────────────
BG        = "#0f172a"
SIDEBAR   = "#111827"
CARD      = "#1e293b"
CARD2     = "#162032"
BORDER    = "#1e3a5f"
ACCENT    = "#3b82f6"
PURPLE    = "#8b5cf6"
TEXT      = "#f8fafc"
TEXT2     = "#94a3b8"
TEXT3     = "#475569"
SUCCESS   = "#22c55e"
WARNING   = "#f59e0b"
DANGER    = "#ef4444"
INPUT_BG  = "#0f172a"

ERP_THEME = f"""
QMainWindow, QDialog, QWidget {{
    background-color: {BG};
    color: {TEXT};
    font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
    font-size: 13px;
}}
QScrollArea, QAbstractScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{
    background: {SIDEBAR}; width: 6px; border-radius: 3px; margin: 0;
}}
QScrollBar::handle:vertical {{
    background: #334155; border-radius: 3px; min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: {ACCENT}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ background: {SIDEBAR}; height: 6px; border-radius: 3px; }}
QScrollBar::handle:horizontal {{ background: #334155; border-radius: 3px; }}

QFrame#sidebar {{ background-color: {SIDEBAR}; border-right: 1px solid {BORDER}; }}
QFrame#topbar  {{ background-color: {SIDEBAR}; border-bottom: 1px solid {BORDER}; }}

QFrame#card {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: 14px;
}}
QFrame#card:hover {{
    border: 1px solid {ACCENT};
    background-color: {CARD2};
}}

QPushButton#navBtn {{
    background: transparent; color: {TEXT2}; border: none;
    border-radius: 10px; padding: 10px 14px;
    text-align: left; font-size: 13px; font-weight: 500;
}}
QPushButton#navBtn:hover {{ background: rgba(59,130,246,0.12); color: {TEXT}; }}
QPushButton#navBtn:checked {{
    background: rgba(59,130,246,0.18); color: {ACCENT}; font-weight: 600;
}}

QPushButton#primaryBtn {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {ACCENT}, stop:1 #2563eb);
    color: white; border: none; border-radius: 8px;
    padding: 10px 22px; font-weight: 600; font-size: 13px;
}}
QPushButton#primaryBtn:hover {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #60a5fa, stop:1 {ACCENT});
}}
QPushButton#primaryBtn:pressed {{ background: #1d4ed8; }}

QPushButton#secondaryBtn {{
    background: rgba(59,130,246,0.08); color: {ACCENT};
    border: 1px solid rgba(59,130,246,0.3); border-radius: 8px;
    padding: 9px 18px; font-weight: 500;
}}
QPushButton#secondaryBtn:hover {{
    background: rgba(59,130,246,0.18); border-color: {ACCENT};
}}

QPushButton#dangerBtn {{
    background: rgba(239,68,68,0.1); color: {DANGER};
    border: 1px solid rgba(239,68,68,0.3); border-radius: 8px;
    padding: 8px 16px; font-weight: 500;
}}
QPushButton#dangerBtn:hover {{ background: rgba(239,68,68,0.2); border-color: {DANGER}; }}

QPushButton#successBtn {{
    background: rgba(34,197,94,0.1); color: {SUCCESS};
    border: 1px solid rgba(34,197,94,0.3); border-radius: 8px;
    padding: 8px 16px; font-weight: 500;
}}
QPushButton#successBtn:hover {{ background: rgba(34,197,94,0.2); border-color: {SUCCESS}; }}

QPushButton#warningBtn {{
    background: rgba(245,158,11,0.1); color: {WARNING};
    border: 1px solid rgba(245,158,11,0.3); border-radius: 8px;
    padding: 8px 16px; font-weight: 500;
}}
QPushButton#warningBtn:hover {{ background: rgba(245,158,11,0.2); border-color: {WARNING}; }}

QLineEdit, QTextEdit, QPlainTextEdit {{
    background: {INPUT_BG}; color: {TEXT};
    border: 1px solid #1e3a5f; border-radius: 8px;
    padding: 9px 12px; font-size: 13px;
    selection-background-color: {ACCENT};
}}
QLineEdit:focus, QTextEdit:focus {{ border: 1px solid {ACCENT}; }}

QComboBox {{
    background: {INPUT_BG}; color: {TEXT};
    border: 1px solid #1e3a5f; border-radius: 8px;
    padding: 9px 12px; font-size: 13px; min-width: 100px;
}}
QComboBox:focus {{ border: 1px solid {ACCENT}; }}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent; border-right: 5px solid transparent;
    border-top: 6px solid {TEXT2}; width: 0; height: 0;
}}
QComboBox QAbstractItemView {{
    background: #1e293b; border: 1px solid {BORDER}; border-radius: 8px;
    color: {TEXT}; selection-background-color: rgba(59,130,246,0.2);
    outline: none; padding: 4px;
}}
QComboBox QAbstractItemView::item {{
    padding: 8px 12px; border-radius: 6px; min-height: 30px;
}}

QSpinBox, QDoubleSpinBox, QDateEdit {{
    background: {INPUT_BG}; color: {TEXT};
    border: 1px solid #1e3a5f; border-radius: 8px;
    padding: 9px 12px; font-size: 13px;
}}
QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{ border: 1px solid {ACCENT}; }}
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    background: #334155; border-radius: 3px; width: 18px;
}}

QTableWidget {{
    background: {CARD}; alternate-background-color: {CARD2};
    color: {TEXT}; gridline-color: transparent;
    border: 1px solid {BORDER}; border-radius: 12px;
    selection-background-color: rgba(59,130,246,0.15);
    selection-color: {TEXT}; font-size: 13px;
}}
QTableWidget::item {{ padding: 10px 8px; border: none; }}
QTableWidget::item:selected {{ background: rgba(59,130,246,0.2); color: {TEXT}; }}
QTableWidget::item:hover {{ background: rgba(59,130,246,0.08); }}
QHeaderView::section {{
    background: #0f172a; color: {TEXT2};
    padding: 12px 8px; border: none;
    border-bottom: 1px solid {BORDER};
    font-weight: 600; font-size: 11px;
    text-transform: uppercase; letter-spacing: 0.5px;
}}

QTabWidget::pane {{
    border: 1px solid {BORDER}; border-radius: 12px;
    background: {CARD}; top: -1px;
}}
QTabBar::tab {{
    background: transparent; color: {TEXT2};
    padding: 10px 22px; border: none;
    border-bottom: 2px solid transparent;
    font-size: 13px; font-weight: 500; margin-right: 4px;
}}
QTabBar::tab:selected {{
    color: {ACCENT}; border-bottom: 2px solid {ACCENT};
    background: rgba(59,130,246,0.08); border-radius: 8px 8px 0 0;
}}
QTabBar::tab:hover {{ color: {TEXT}; background: rgba(255,255,255,0.04); border-radius: 8px 8px 0 0; }}

QGroupBox {{
    border: 1px solid {BORDER}; border-radius: 12px;
    margin-top: 16px; padding: 16px;
    color: {TEXT2}; font-weight: 600; font-size: 12px;
}}
QGroupBox::title {{
    subcontrol-origin: margin; left: 14px; padding: 0 8px;
    color: {ACCENT}; text-transform: uppercase; letter-spacing: 1px;
}}

QCheckBox {{ color: {TEXT}; spacing: 10px; font-size: 13px; }}
QCheckBox::indicator {{
    width: 18px; height: 18px; border: 2px solid #334155;
    border-radius: 5px; background: {INPUT_BG};
}}
QCheckBox::indicator:checked {{ background: {ACCENT}; border-color: {ACCENT}; }}

QMessageBox {{ background: {CARD}; color: {TEXT}; }}
QMessageBox QPushButton {{
    background: {ACCENT}; color: white; border-radius: 8px;
    padding: 8px 20px; font-weight: 600; min-width: 80px; border: none;
}}
QMessageBox QPushButton:hover {{ background: #60a5fa; }}

QStatusBar {{
    background: {SIDEBAR}; color: {TEXT3};
    border-top: 1px solid {BORDER}; font-size: 11px; padding: 4px 12px;
}}

QLabel#pageTitle {{
    color: {TEXT}; font-size: 26px; font-weight: 700; letter-spacing: -0.5px;
}}
QLabel#sectionTitle {{ color: {TEXT}; font-size: 16px; font-weight: 600; }}
QLabel#metaLabel {{ color: {TEXT2}; font-size: 12px; }}

QProgressBar {{
    background: #1e293b; border: none; border-radius: 4px;
    height: 6px; text-align: center; color: transparent;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {ACCENT}, stop:1 {PURPLE});
    border-radius: 4px;
}}
QDialog {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 16px; }}
"""
