"""Shared reusable premium widgets."""
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame, QTableWidget, QHeaderView, QAbstractItemView)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from themes.dark_theme import ACCENT, TEXT, TEXT2, TEXT3, CARD, BORDER, BG


def page_header(title, subtitle="", btn_text=None, btn_cb=None):
    """Returns (frame, btn_or_None)."""
    frame = QFrame()
    frame.setStyleSheet("background:transparent;")
    lay = QHBoxLayout(frame)
    lay.setContentsMargins(0,0,0,0)
    lay.setSpacing(12)
    left = QVBoxLayout()
    left.setSpacing(3)
    t = QLabel(title)
    t.setStyleSheet(f"background:transparent; color:{TEXT}; font-size:24px; font-weight:700;")
    left.addWidget(t)
    if subtitle:
        s = QLabel(subtitle)
        s.setStyleSheet(f"background:transparent; color:{TEXT2}; font-size:13px;")
        left.addWidget(s)
    lay.addLayout(left)
    lay.addStretch()
    btn = None
    if btn_text:
        btn = QPushButton(btn_text)
        btn.setObjectName("primaryBtn")
        btn.setFixedHeight(40)
        if btn_cb: btn.clicked.connect(btn_cb)
        lay.addWidget(btn)
    return frame, btn


def search_bar(placeholder="🔍  Rechercher...", width=None):
    f = QLineEdit()
    f.setPlaceholderText(placeholder)
    f.setFixedHeight(38)
    if width: f.setFixedWidth(width)
    return f


def filter_card(*widgets):
    """Wraps widgets in a horizontal filter bar card."""
    frame = QFrame()
    frame.setObjectName("card")
    frame.setStyleSheet(f"""
        QFrame#card{{background:{CARD}; border:1px solid {BORDER}; border-radius:12px;}}
    """)
    lay = QHBoxLayout(frame)
    lay.setContentsMargins(16, 10, 16, 10)
    lay.setSpacing(12)
    stretch_added = False
    for w in widgets:
        if w == "stretch":
            lay.addStretch()
            stretch_added = True
        elif isinstance(w, QLabel):
            w.setStyleSheet(f"background:transparent; color:{TEXT2}; font-size:12px;")
            lay.addWidget(w)
        else:
            lay.addWidget(w)
    if not stretch_added:
        lay.addStretch()
    return frame


def build_table(columns, stretch_col=None):
    t = QTableWidget()
    t.setColumnCount(len(columns))
    t.setHorizontalHeaderLabels(columns)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    if stretch_col is not None:
        t.horizontalHeader().setSectionResizeMode(stretch_col, QHeaderView.ResizeToContents)
    t.setSelectionBehavior(QAbstractItemView.SelectRows)
    t.setEditTriggers(QAbstractItemView.NoEditTriggers)
    t.setAlternatingRowColors(True)
    t.verticalHeader().setVisible(False)
    t.setShowGrid(False)
    t.verticalHeader().setDefaultSectionSize(46)
    return t


def action_btn(icon, color, tooltip=""):
    b = QPushButton(icon)
    b.setFixedSize(32, 32)
    b.setToolTip(tooltip)
    b.setStyleSheet(f"""
        QPushButton{{background:rgba({_hex_rgb(color)},0.12); color:{color};
                    border:1px solid rgba({_hex_rgb(color)},0.3); border-radius:8px;
                    font-size:14px;}}
        QPushButton:hover{{background:rgba({_hex_rgb(color)},0.25); border-color:{color};}}
    """)
    return b


def _hex_rgb(h):
    h = h.lstrip('#')
    return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"


class SummaryPill(QLabel):
    def __init__(self, text, color=ACCENT):
        super().__init__(text)
        self.setStyleSheet(f"""
            background:rgba({_hex_rgb(color)},0.12);
            color:{color};
            border:1px solid rgba({_hex_rgb(color)},0.3);
            border-radius:8px;
            padding:6px 14px;
            font-size:13px;
            font-weight:600;
        """)

    def update_text(self, text):
        self.setText(text)
