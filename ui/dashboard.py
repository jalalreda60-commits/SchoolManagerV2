import os
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QPushButton, QSizePolicy, QGridLayout)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QColor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class StatCard(QFrame):
    def __init__(self, title, value, icon, color, subtitle=""):
        super().__init__()
        self.setObjectName("card")
        self.setMinimumHeight(120)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._color = color
        self.setStyleSheet(f"""
            QFrame#card {{
                background: #1e293b;
                border: 1px solid #1e3a5f;
                border-radius: 14px;
            }}
            QFrame#card:hover {{
                border: 1px solid {color};
                background: #162032;
            }}
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(6)

        top = QHBoxLayout()
        top.setSpacing(0)
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"background:transparent; font-size:22px; color:{color};")
        top.addWidget(icon_lbl)
        top.addStretch()

        badge = QLabel("●")
        badge.setStyleSheet(f"background:transparent; color:{color}; font-size:8px;")
        top.addWidget(badge)
        lay.addLayout(top)
        lay.addSpacing(4)

        self._val_lbl = QLabel(str(value))
        self._val_lbl.setStyleSheet(f"background:transparent; color:{color}; font-size:26px; font-weight:700;")
        lay.addWidget(self._val_lbl)

        t_lbl = QLabel(title)
        t_lbl.setStyleSheet("background:transparent; color:#94a3b8; font-size:12px; font-weight:500;")
        lay.addWidget(t_lbl)

        if subtitle:
            s_lbl = QLabel(subtitle)
            s_lbl.setStyleSheet("background:transparent; color:#475569; font-size:10px;")
            lay.addWidget(s_lbl)

    def update_value(self, v):
        self._val_lbl.setText(str(v))


class ChartCard(QFrame):
    def __init__(self, title):
        super().__init__()
        self.setObjectName("card")
        self.setMinimumHeight(260)
        self.setStyleSheet("""
            QFrame#card {
                background: #1e293b;
                border: 1px solid #1e3a5f;
                border-radius: 14px;
            }
        """)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 18, 20, 18)
        self._layout.setSpacing(12)

        hdr = QHBoxLayout()
        t = QLabel(title)
        t.setStyleSheet("background:transparent; color:#f8fafc; font-size:14px; font-weight:600;")
        hdr.addWidget(t)
        hdr.addStretch()
        self._layout.addLayout(hdr)
        self._canvas_holder = QVBoxLayout()
        self._layout.addLayout(self._canvas_holder)

    def set_canvas(self, canvas):
        while self._canvas_holder.count():
            item = self._canvas_holder.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self._canvas_holder.addWidget(canvas)


class NotifRow(QFrame):
    def __init__(self, msg, level="warning"):
        super().__init__()
        cols = {"warning":"#f59e0b","danger":"#ef4444","success":"#22c55e","info":"#3b82f6"}
        icons = {"warning":"⚠","danger":"🔴","success":"✅","info":"ℹ"}
        c = cols.get(level,"#3b82f6")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(12)
        ic = QLabel(icons.get(level,"ℹ"))
        ic.setStyleSheet(f"background:transparent; font-size:14px; color:{c};")
        lay.addWidget(ic)
        ml = QLabel(msg)
        ml.setStyleSheet("background:transparent; color:#f8fafc; font-size:12px;")
        ml.setWordWrap(True)
        lay.addWidget(ml, 1)
        self.setStyleSheet(f"""
            QFrame {{
                background: rgba({self._hex_rgb(c)}, 0.07);
                border-left: 3px solid {c};
                border-radius: 8px;
                margin: 2px 0;
            }}
        """)

    def _hex_rgb(self, h):
        h = h.lstrip('#')
        return f"{int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)}"


class DashboardWidget(QWidget):
    def __init__(self, session, current_user):
        super().__init__()
        self.session = session
        self.current_user = current_user
        self.setStyleSheet("background: transparent;")
        self._charts = {}
        self.setup_ui()
        self.load_data()
        self._timer = QTimer()
        self._timer.timeout.connect(self.load_data)
        self._timer.start(30000)

    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(20)

        # ── Header ────────────────────────────────────────────────────────────
        hdr = QHBoxLayout()
        hdr.setSpacing(12)
        left = QVBoxLayout()
        left.setSpacing(4)
        title = QLabel("Tableau de Bord")
        title.setObjectName("pageTitle")
        title.setStyleSheet("color:#f8fafc; font-size:26px; font-weight:700; background:transparent;")
        sub = QLabel(f"Bienvenue, {self.current_user.full_name or self.current_user.username}")
        sub.setStyleSheet("color:#94a3b8; font-size:13px; background:transparent;")
        left.addWidget(title)
        left.addWidget(sub)
        hdr.addLayout(left)
        hdr.addStretch()

        now = datetime.now()
        date_lbl = QLabel(now.strftime("📅  %A %d %B %Y"))
        date_lbl.setStyleSheet("""
            background: rgba(59,130,246,0.1);
            color: #60a5fa; font-size: 12px; font-weight:500;
            border: 1px solid rgba(59,130,246,0.25);
            border-radius: 8px; padding: 8px 14px;
        """)
        hdr.addWidget(date_lbl)

        refresh_btn = QPushButton("⟳  Actualiser")
        refresh_btn.setObjectName("secondaryBtn")
        refresh_btn.setFixedHeight(36)
        refresh_btn.clicked.connect(self.load_data)
        hdr.addWidget(refresh_btn)
        root.addLayout(hdr)

        # ── Scroll area ────────────────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none; background:transparent;}")
        inner = QWidget()
        inner.setStyleSheet("background:transparent;")
        self._inner_layout = QVBoxLayout(inner)
        self._inner_layout.setSpacing(20)
        self._inner_layout.setContentsMargins(0, 0, 4, 0)
        scroll.setWidget(inner)
        root.addWidget(scroll)

        # ── Stat cards (3×3 grid) ─────────────────────────────────────────────
        grid = QGridLayout()
        grid.setSpacing(14)

        from themes.dark_theme import ACCENT, PURPLE, SUCCESS, WARNING, DANGER, TEXT2
        card_defs = [
            ("Total Élèves",       "0", "🎓", ACCENT,   "Élèves actifs"),
            ("Recettes du Mois",   "0 MAD","💰", SUCCESS, "Ce mois"),
            ("Recettes Annuelles", "0 MAD","📈", "#06b6d4","Cette année"),
            ("Dépenses",           "0 MAD","📉", DANGER,  "Cette année"),
            ("Bénéfice Net",       "0 MAD","💎", PURPLE,  "Cette année"),
            ("Impayés",            "0",    "⚠",  WARNING, "Ce mois"),
            ("Enseignants",        "0",    "👨‍🏫", "#a78bfa","Actifs"),
            ("Employés",           "0",    "👥",  "#22d3ee","Total"),
            ("Transport",          "0",    "🚌",  "#fb923c","Abonnés"),
        ]
        self._cards = {}
        for i, (title, val, icon, color, sub) in enumerate(card_defs):
            c = StatCard(title, val, icon, color, sub)
            self._cards[title] = c
            grid.addWidget(c, i//3, i%3)

        grid_w = QWidget()
        grid_w.setStyleSheet("background:transparent;")
        grid_w.setLayout(grid)
        self._inner_layout.addWidget(grid_w)

        # ── Charts row ────────────────────────────────────────────────────────
        charts_row = QHBoxLayout()
        charts_row.setSpacing(14)
        self._revenue_card = ChartCard("📊  Recettes Mensuelles — 12 mois")
        self._class_card   = ChartCard("🎓  Répartition des Élèves par Classe")
        charts_row.addWidget(self._revenue_card, 3)
        charts_row.addWidget(self._class_card, 2)
        self._inner_layout.addLayout(charts_row)

        # ── Bottom row (expense chart + notifications) ─────────────────────────
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(14)
        self._expense_card = ChartCard("📉  Dépenses vs Recettes — Comparatif")
        bottom_row.addWidget(self._expense_card, 3)

        notif_frame = QFrame()
        notif_frame.setObjectName("card")
        notif_frame.setMinimumWidth(280)
        notif_lay = QVBoxLayout(notif_frame)
        notif_lay.setContentsMargins(16, 16, 16, 16)
        notif_lay.setSpacing(8)
        notif_title = QLabel("🔔  Alertes & Notifications")
        notif_title.setStyleSheet("background:transparent; color:#f8fafc; font-size:14px; font-weight:600;")
        notif_lay.addWidget(notif_title)
        self._notif_layout = QVBoxLayout()
        self._notif_layout.setSpacing(6)
        notif_lay.addLayout(self._notif_layout)
        notif_lay.addStretch()
        bottom_row.addWidget(notif_frame, 2)
        self._inner_layout.addLayout(bottom_row)
        self._inner_layout.addStretch()

    # ── Data loading ───────────────────────────────────────────────────────────
    def load_data(self):
        try:
            self._load_stats()
            self._load_charts()
            self._load_notifications()
        except Exception as e:
            print(f"Dashboard error: {e}")
            import traceback; traceback.print_exc()

    def _load_stats(self):
        from models.database import Student, Payment, Employee, Expense
        from sqlalchemy import func
        s = self.session
        now = datetime.now()

        total_st = s.query(Student).filter_by(is_active=True).count()
        self._cards["Total Élèves"].update_value(total_st)

        m_rev = s.query(func.sum(Payment.amount)).filter(
            Payment.month==now.month, Payment.year==now.year).scalar() or 0
        self._cards["Recettes du Mois"].update_value(f"{m_rev:,.0f} MAD")

        y_rev = s.query(func.sum(Payment.amount)).filter(Payment.year==now.year).scalar() or 0
        self._cards["Recettes Annuelles"].update_value(f"{y_rev:,.0f} MAD")

        y_exp = s.query(func.sum(Expense.amount)).filter(
            func.strftime('%Y', Expense.expense_date)==str(now.year)).scalar() or 0
        self._cards["Dépenses"].update_value(f"{y_exp:,.0f} MAD")

        profit = y_rev - y_exp
        self._cards["Bénéfice Net"].update_value(f"{profit:,.0f} MAD")

        paid_ids = [p[0] for p in s.query(Payment.student_id).filter(
            Payment.month==now.month, Payment.year==now.year,
            Payment.payment_type=='monthly').all()]
        unpaid = s.query(Student).filter(Student.is_active==True, ~Student.id.in_(paid_ids)).count()
        self._cards["Impayés"].update_value(unpaid)

        teachers = s.query(Employee).filter_by(employee_type='teacher', is_active=True).count()
        employees = s.query(Employee).filter_by(is_active=True).count()
        transport = s.query(Student).filter_by(has_transport=True, is_active=True).count()
        self._cards["Enseignants"].update_value(teachers)
        self._cards["Employés"].update_value(employees)
        self._cards["Transport"].update_value(transport)

    def _load_charts(self):
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
            from matplotlib.figure import Figure
            from models.database import Payment, Expense, Student, Class
            from sqlalchemy import func

            BG_C   = '#0f172a'
            CARD_C = '#1e293b'
            GRID_C = '#1e3a5f'
            ACCENT_C = '#3b82f6'
            PURPLE_C = '#8b5cf6'
            SUCCESS_C = '#22c55e'
            DANGER_C  = '#ef4444'
            TEXT_C   = '#94a3b8'

            now = datetime.now()
            month_labels = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']

            # ── Chart 1: Revenue line ──────────────────────────────────────────
            revenues = []
            expenses_m = []
            labels = []
            for i in range(12):
                m = ((now.month - 1 - (11-i)) % 12) + 1
                y = now.year if m <= now.month else now.year - 1
                rev = self.session.query(func.sum(Payment.amount)).filter(
                    Payment.month==m, Payment.year==y).scalar() or 0
                exp = self.session.query(func.sum(Expense.amount)).filter(
                    func.strftime('%m', Expense.expense_date)==f"{m:02d}",
                    func.strftime('%Y', Expense.expense_date)==str(y)).scalar() or 0
                revenues.append(float(rev))
                expenses_m.append(float(exp))
                labels.append(month_labels[m-1])

            fig1 = Figure(figsize=(7, 3), facecolor=CARD_C)
            ax1 = fig1.add_subplot(111)
            ax1.set_facecolor(CARD_C)
            xs = range(len(labels))
            ax1.fill_between(xs, revenues, alpha=0.15, color=ACCENT_C)
            ax1.plot(xs, revenues, color=ACCENT_C, linewidth=2.5, marker='o',
                     markersize=5, markerfacecolor=ACCENT_C, label='Recettes')
            ax1.fill_between(xs, expenses_m, alpha=0.1, color=DANGER_C)
            ax1.plot(xs, expenses_m, color=DANGER_C, linewidth=2, linestyle='--',
                     marker='s', markersize=4, label='Dépenses')
            ax1.set_xticks(list(xs))
            ax1.set_xticklabels(labels, color=TEXT_C, fontsize=9)
            ax1.tick_params(colors=TEXT_C, which='both')
            ax1.yaxis.set_tick_params(labelcolor=TEXT_C, labelsize=8)
            ax1.spines[:].set_color(GRID_C)
            ax1.grid(axis='y', color=GRID_C, linewidth=0.5, alpha=0.7)
            ax1.legend(loc='upper left', fontsize=9, framealpha=0,
                       labelcolor=TEXT_C)
            fig1.tight_layout(pad=1.5)
            canvas1 = FigureCanvasQTAgg(fig1)
            canvas1.setStyleSheet("background:transparent;")
            self._revenue_card.set_canvas(canvas1)

            # ── Chart 2: Students pie ─────────────────────────────────────────
            classes = self.session.query(Class).all()
            cls_names = []
            cls_counts = []
            for cls in classes:
                cnt = self.session.query(Student).filter_by(class_id=cls.id, is_active=True).count()
                if cnt > 0:
                    cls_names.append(cls.name)
                    cls_counts.append(cnt)

            fig2 = Figure(figsize=(4, 3), facecolor=CARD_C)
            ax2 = fig2.add_subplot(111)
            ax2.set_facecolor(CARD_C)
            if cls_counts:
                palette = [ACCENT_C, PURPLE_C, SUCCESS_C, '#f59e0b', '#06b6d4',
                           '#fb923c', '#a78bfa', '#34d399', '#f472b6', '#60a5fa',
                           '#fbbf24', '#4ade80', '#38bdf8', '#c084fc', '#fb7185']
                colors_pie = [palette[i % len(palette)] for i in range(len(cls_counts))]
                wedges, texts, autotexts = ax2.pie(
                    cls_counts, labels=cls_names, colors=colors_pie,
                    autopct='%1.0f%%', startangle=90,
                    pctdistance=0.8, wedgeprops=dict(width=0.6, edgecolor=CARD_C, linewidth=2))
                for t in texts: t.set_color(TEXT_C); t.set_fontsize(8)
                for at in autotexts: at.set_color('white'); at.set_fontsize(7); at.set_fontweight('bold')
            else:
                ax2.text(0.5, 0.5, 'Aucun élève', ha='center', va='center',
                         color=TEXT_C, transform=ax2.transAxes)
            fig2.tight_layout(pad=1.0)
            canvas2 = FigureCanvasQTAgg(fig2)
            canvas2.setStyleSheet("background:transparent;")
            self._class_card.set_canvas(canvas2)

            # ── Chart 3: Bar compare ──────────────────────────────────────────
            fig3 = Figure(figsize=(7, 3), facecolor=CARD_C)
            ax3 = fig3.add_subplot(111)
            ax3.set_facecolor(CARD_C)
            x = list(range(len(labels)))
            w = 0.38
            bars1 = ax3.bar([xi - w/2 for xi in x], revenues, w,
                            color=ACCENT_C, alpha=0.85, label='Recettes', linewidth=0)
            bars2 = ax3.bar([xi + w/2 for xi in x], expenses_m, w,
                            color=DANGER_C, alpha=0.75, label='Dépenses', linewidth=0)
            ax3.set_xticks(x)
            ax3.set_xticklabels(labels, color=TEXT_C, fontsize=9)
            ax3.tick_params(colors=TEXT_C, which='both')
            ax3.yaxis.set_tick_params(labelcolor=TEXT_C, labelsize=8)
            ax3.spines[:].set_color(GRID_C)
            ax3.grid(axis='y', color=GRID_C, linewidth=0.5, alpha=0.7)
            ax3.legend(loc='upper left', fontsize=9, framealpha=0, labelcolor=TEXT_C)
            fig3.tight_layout(pad=1.5)
            canvas3 = FigureCanvasQTAgg(fig3)
            canvas3.setStyleSheet("background:transparent;")
            self._expense_card.set_canvas(canvas3)

        except Exception as e:
            print(f"Chart error: {e}")

    def _load_notifications(self):
        while self._notif_layout.count():
            item = self._notif_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        from models.database import Student, Payment
        from sqlalchemy import func
        now = datetime.now()
        paid_ids = [p[0] for p in self.session.query(Payment.student_id).filter(
            Payment.month==now.month, Payment.year==now.year,
            Payment.payment_type=='monthly').all()]
        unpaid = self.session.query(Student).filter(
            Student.is_active==True, ~Student.id.in_(paid_ids)).count()
        total_st = self.session.query(Student).filter_by(is_active=True).count()

        if unpaid > 0:
            self._notif_layout.addWidget(NotifRow(
                f"{unpaid} élève(s) n'ont pas payé ce mois.", "warning"))
        if total_st == 0:
            self._notif_layout.addWidget(NotifRow(
                "Aucun élève enregistré.", "info"))
        if unpaid == 0 and total_st > 0:
            self._notif_layout.addWidget(NotifRow(
                "Tous les paiements du mois sont à jour ✓", "success"))

        y_rev = self.session.query(func.sum(Payment.amount)).filter(
            Payment.year==now.year).scalar() or 0
        from models.database import Expense
        y_exp = self.session.query(func.sum(Expense.amount)).filter(
            func.strftime('%Y', Expense.expense_date)==str(now.year)).scalar() or 0
        if y_rev - y_exp < 0:
            self._notif_layout.addWidget(NotifRow(
                f"Déficit de {abs(y_rev-y_exp):,.0f} MAD cette année.", "danger"))
