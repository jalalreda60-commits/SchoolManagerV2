import os
from datetime import datetime, date
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QComboBox,
    QMessageBox, QFrame, QHeaderView, QAbstractItemView, QDoubleSpinBox, QSpinBox,
    QTabWidget, QTextEdit)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

DAYS = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi']
HOURS_START = ['08:00','09:00','10:00','11:00','14:00','15:00','16:00','17:00']
HOURS_END   = ['09:00','10:00','11:00','12:00','15:00','16:00','17:00','18:00']

def lbl(t):
    l = QLabel(t); l.setStyleSheet("color:#94a3b8; font-size:12px; font-weight:500; background:transparent;")
    return l


class TransportWidget(QWidget):
    def __init__(self, session, current_user):
        super().__init__()
        self.session = session; self.current_user = current_user
        self.setStyleSheet("background:transparent;")
        self._build(); self.load_data()

    def _build(self):
        from ui.widgets import page_header, filter_card, search_bar, build_table, action_btn, SummaryPill
        from PySide6.QtWidgets import QLabel as QL

        root = QVBoxLayout(self); root.setContentsMargins(24,20,24,20); root.setSpacing(16)
        hdr, _ = page_header("Gestion du Transport","Élèves abonnés, bus et itinéraires.")
        root.addWidget(hdr)

        tabs = QTabWidget()
        root.addWidget(tabs)

        # ── Students tab ──────────────────────────────────────────────────────
        st_tab = QWidget(); st_tab.setStyleSheet("background:transparent;")
        st_lay = QVBoxLayout(st_tab); st_lay.setContentsMargins(0,16,0,0); st_lay.setSpacing(12)

        pills = QHBoxLayout(); pills.setSpacing(10)
        self._pill_transport = SummaryPill("0 abonnés", "#fb923c")
        self._pill_revenue   = SummaryPill("0 MAD/mois", "#22c55e")
        for p in [self._pill_transport, self._pill_revenue]: pills.addWidget(p)
        pills.addStretch()
        pf = QFrame(); pf.setLayout(pills); pf.setStyleSheet("background:transparent;")
        st_lay.addWidget(pf)

        self._search = search_bar("🔍  Rechercher un élève...")
        self._search.textChanged.connect(self.load_data)
        fc = filter_card(self._search)
        st_lay.addWidget(fc)

        self._st_table = build_table(["Code","Nom","Prénom","Classe","Transport","Frais","Parent"])
        st_lay.addWidget(self._st_table)
        tabs.addTab(st_tab, "🎓  Élèves Transport")

        # ── Buses tab ─────────────────────────────────────────────────────────
        bus_tab = QWidget(); bus_tab.setStyleSheet("background:transparent;")
        bus_lay = QVBoxLayout(bus_tab); bus_lay.setContentsMargins(0,16,0,0); bus_lay.setSpacing(12)
        add_bus_btn = QPushButton("➕  Nouveau Bus")
        add_bus_btn.setObjectName("primaryBtn"); add_bus_btn.setFixedHeight(40); add_bus_btn.setFixedWidth(160)
        add_bus_btn.clicked.connect(self._add_bus)
        bus_lay.addWidget(add_bus_btn)
        self._bus_table = build_table(["N° Bus","Plaque","Capacité","Route","Chauffeur","Statut"])
        bus_lay.addWidget(self._bus_table)
        tabs.addTab(bus_tab, "🚌  Gestion des Bus")

    def load_data(self):
        from models.database import Student, Bus, Employee
        search = self._search.text().lower()
        students = self.session.query(Student).filter_by(is_active=True).all()
        self._st_table.setRowCount(0)
        transport_count = 0; transport_rev = 0
        from models.database import Setting
        tf = self.session.query(Setting).filter_by(key='transport_fee').first()
        tfee = float(tf.value) if tf else 300
        for s in students:
            if search and search not in f"{s.first_name} {s.last_name}".lower(): continue
            r = self._st_table.rowCount(); self._st_table.insertRow(r)
            for c, v in enumerate([s.student_code or "", s.last_name, s.first_name,
                s.class_.name if s.class_ else "—",
                "✅ Abonné" if s.has_transport else "❌ Non",
                f"{tfee:,.0f} MAD" if s.has_transport else "—",
                s.parent_phone or "—"]):
                item = QTableWidgetItem(v); item.setTextAlignment(Qt.AlignCenter)
                if v == "✅ Abonné": item.setForeground(QColor("#22c55e"))
                elif v == "❌ Non": item.setForeground(QColor("#ef4444"))
                self._st_table.setItem(r, c, item)
            if s.has_transport: transport_count += 1; transport_rev += tfee
        self._pill_transport.update_text(f"{transport_count} abonnés")
        self._pill_revenue.update_text(f"{transport_rev:,.0f} MAD/mois")

        buses = self.session.query(Bus).all()
        self._bus_table.setRowCount(0)
        for b in buses:
            driver = self.session.query(Employee).get(b.driver_id) if b.driver_id else None
            r = self._bus_table.rowCount(); self._bus_table.insertRow(r)
            for c, v in enumerate([b.bus_number or "", b.plate or "", str(b.capacity or "—"),
                b.route or "—",
                f"{driver.first_name} {driver.last_name}" if driver else "—",
                "✅ Actif" if b.is_active else "❌ Inactif"]):
                item = QTableWidgetItem(v); item.setTextAlignment(Qt.AlignCenter)
                self._bus_table.setItem(r, c, item)

    def _add_bus(self):
        from models.database import Bus, Employee
        dlg = QDialog(self); dlg.setWindowTitle("Nouveau Bus"); dlg.setMinimumSize(420,360)
        root = QVBoxLayout(dlg); root.setContentsMargins(28,24,28,24); root.setSpacing(14)
        root.addWidget(QLabel("🚌  Nouveau Bus",
            styleSheet="color:#f8fafc; font-size:18px; font-weight:700; background:transparent;"))
        form = QFormLayout(); form.setSpacing(10); form.setLabelAlignment(Qt.AlignRight)
        def f(ph=""): fi = QLineEdit(); fi.setPlaceholderText(ph); fi.setFixedHeight(40); return fi
        num = f("Ex: BUS-01"); plate = f("Ex: 12345-A-1")
        cap = QSpinBox(); cap.setRange(1,100); cap.setValue(30); cap.setFixedHeight(40)
        route = f("Itinéraire")
        fee = QDoubleSpinBox(); fee.setRange(0,9999); fee.setDecimals(2)
        fee.setSuffix(" MAD"); fee.setValue(300); fee.setFixedHeight(40)
        dc = QComboBox(); dc.setFixedHeight(40); dc.addItem("-- Aucun --", None)
        for d in self.session.query(Employee).filter_by(employee_type='driver', is_active=True).all():
            dc.addItem(f"{d.first_name} {d.last_name}", d.id)
        for rl, w in [("N° Bus:",num),("Plaque:",plate),("Capacité:",cap),
                      ("Route:",route),("Frais:",fee),("Chauffeur:",dc)]:
            form.addRow(lbl(rl), w)
        root.addLayout(form)
        br = QHBoxLayout(); br.addStretch()
        cc = QPushButton("Annuler"); cc.setObjectName("secondaryBtn"); cc.clicked.connect(dlg.reject)
        sc = QPushButton("💾  Enregistrer"); sc.setObjectName("primaryBtn")
        br.addWidget(cc); br.addWidget(sc); root.addLayout(br)
        def save():
            bus = Bus(bus_number=num.text().strip(), plate=plate.text().strip(),
                capacity=cap.value(), route=route.text().strip(),
                monthly_fee=fee.value(), driver_id=dc.currentData())
            self.session.add(bus); self.session.commit(); dlg.accept(); self.load_data()
        sc.clicked.connect(save); dlg.exec()


class TimetableWidget(QWidget):
    def __init__(self, session, current_user):
        super().__init__()
        self.session = session; self.current_user = current_user
        self.setStyleSheet("background:transparent;")
        self._build(); self.load_timetable()

    def _build(self):
        from ui.widgets import page_header
        from models.database import Class
        root = QVBoxLayout(self); root.setContentsMargins(24,20,24,20); root.setSpacing(16)

        hdr, add_btn = page_header("Emploi du Temps",
            "Planning hebdomadaire par classe et enseignant.",
            "➕  Ajouter Cours", self._add_course)
        root.addWidget(hdr)

        filter_row = QHBoxLayout(); filter_row.setSpacing(12)
        cl = QLabel("Filtrer par classe:")
        cl.setStyleSheet("color:#94a3b8; font-size:12px; background:transparent;")
        filter_row.addWidget(cl)
        self._class_f = QComboBox(); self._class_f.setFixedHeight(38); self._class_f.setFixedWidth(140)
        self._class_f.addItem("Toutes les classes", None)
        for cls in self.session.query(Class).all():
            self._class_f.addItem(cls.name, cls.id)
        self._class_f.currentIndexChanged.connect(self.load_timetable)
        filter_row.addWidget(self._class_f)
        filter_row.addStretch()
        ff = QFrame(); ff.setLayout(filter_row); ff.setStyleSheet("background:transparent;")
        root.addWidget(ff)

        self._table = QTableWidget()
        self._table.setColumnCount(len(DAYS))
        self._table.setHorizontalHeaderLabels(DAYS)
        self._table.setRowCount(len(HOURS_START))
        self._table.setVerticalHeaderLabels(
            [f"{s} — {e}" for s, e in zip(HOURS_START, HOURS_END)])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.verticalHeader().setDefaultSectionSize(56)
        self._table.verticalHeader().setStyleSheet(
            "QHeaderView::section{background:#111827; color:#94a3b8; font-size:11px; padding:4px;}")
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setShowGrid(True)
        root.addWidget(self._table)

    def load_timetable(self):
        from models.database import Schedule, Employee, Class
        self._table.clearContents()
        cid = self._class_f.currentData()
        q = self.session.query(Schedule)
        if cid: q = q.filter_by(class_id=cid)
        for sched in q.all():
            if sched.day_of_week < 6 and sched.start_time in HOURS_START:
                row = HOURS_START.index(sched.start_time)
                col = sched.day_of_week
                emp = self.session.query(Employee).get(sched.employee_id) if sched.employee_id else None
                cls = self.session.query(Class).get(sched.class_id) if sched.class_id else None
                item = QTableWidgetItem(
                    f"{sched.subject or ''}\n{emp.last_name if emp else ''}\n{cls.name if cls else ''}")
                item.setTextAlignment(Qt.AlignCenter)
                item.setBackground(QColor("#1e3a5f"))
                item.setForeground(QColor("#60a5fa"))
                self._table.setItem(row, col, item)

    def _add_course(self):
        from models.database import Schedule, Employee, Class
        dlg = QDialog(self); dlg.setWindowTitle("Ajouter un cours"); dlg.setMinimumSize(400,400)
        root = QVBoxLayout(dlg); root.setContentsMargins(28,24,28,24); root.setSpacing(14)
        root.addWidget(QLabel("📅  Nouveau Cours",
            styleSheet="color:#f8fafc; font-size:18px; font-weight:700; background:transparent;"))
        form = QFormLayout(); form.setSpacing(10); form.setLabelAlignment(Qt.AlignRight)
        def c(h=40): cb = QComboBox(); cb.setFixedHeight(h); return cb
        cc = c(); [cc.addItem(cls.name, cls.id) for cls in self.session.query(Class).all()]
        ec = c(); ec.addItem("-- Aucun --", None)
        for t in self.session.query(Employee).filter_by(employee_type='teacher',is_active=True).all():
            ec.addItem(f"{t.first_name} {t.last_name}", t.id)
        subj = QLineEdit(); subj.setFixedHeight(40); subj.setPlaceholderText("Mathématiques...")
        dc = c(); [dc.addItem(d) for d in DAYS]
        sc = c(); [sc.addItem(h) for h in HOURS_START]
        ec2 = c(); [ec2.addItem(h) for h in HOURS_END]
        room = QLineEdit(); room.setFixedHeight(40); room.setPlaceholderText("Salle 101")
        for rl, w in [("Classe:",cc),("Enseignant:",ec),("Matière:",subj),
                      ("Jour:",dc),("Début:",sc),("Fin:",ec2),("Salle:",room)]:
            form.addRow(lbl(rl), w)
        root.addLayout(form)
        br = QHBoxLayout(); br.addStretch()
        can = QPushButton("Annuler"); can.setObjectName("secondaryBtn"); can.clicked.connect(dlg.reject)
        sav = QPushButton("💾  Enregistrer"); sav.setObjectName("primaryBtn")
        br.addWidget(can); br.addWidget(sav); root.addLayout(br)
        def save():
            self.session.add(Schedule(class_id=cc.currentData(), employee_id=ec.currentData(),
                subject=subj.text().strip(), day_of_week=dc.currentIndex(),
                start_time=sc.currentText(), end_time=ec2.currentText(), room=room.text().strip()))
            self.session.commit(); dlg.accept(); self.load_timetable()
        sav.clicked.connect(save); dlg.exec()
