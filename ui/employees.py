import os
from datetime import datetime, date
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QComboBox,
    QDateEdit, QTextEdit, QDoubleSpinBox, QMessageBox, QFrame, QHeaderView,
    QAbstractItemView, QSpinBox)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor

MONTHS = ['Janvier','Février','Mars','Avril','Mai','Juin',
          'Juillet','Août','Septembre','Octobre','Novembre','Décembre']

def lbl(t):
    l = QLabel(t); l.setStyleSheet("color:#94a3b8; font-size:12px; font-weight:500; background:transparent;")
    return l


class EmployeeDialog(QDialog):
    def __init__(self, session, employee=None, parent=None):
        super().__init__(parent)
        self.session = session; self.employee = employee
        self.setWindowTitle("Modifier" if employee else "Nouvel Employé")
        self.setMinimumSize(500, 520)
        self._build()
        if employee: self._populate(employee)

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(28,24,28,24); root.setSpacing(16)
        title = QLabel("👤  " + ("Modifier" if self.employee else "Nouvel Employé"))
        title.setStyleSheet("color:#f8fafc; font-size:20px; font-weight:700; background:transparent;")
        root.addWidget(title)
        form = QFormLayout(); form.setSpacing(12); form.setLabelAlignment(Qt.AlignRight)
        def f(ph=""): fi = QLineEdit(); fi.setPlaceholderText(ph); fi.setFixedHeight(40); return fi
        self.first_name    = f("Prénom")
        self.last_name     = f("Nom")
        self.emp_type      = QComboBox(); self.emp_type.setFixedHeight(40)
        self.emp_type.addItems(["teacher","staff","driver"])
        self.subject       = f("Matière")
        self.phone         = f("+212 6XX XXX XXX")
        self.email         = f("email@example.com")
        self.address       = QTextEdit(); self.address.setMaximumHeight(60)
        self.hire_date     = QDateEdit(); self.hire_date.setCalendarPopup(True)
        self.hire_date.setDate(QDate.currentDate()); self.hire_date.setFixedHeight(40)
        self.base_salary   = QDoubleSpinBox(); self.base_salary.setRange(0,99999)
        self.base_salary.setDecimals(2); self.base_salary.setSuffix(" MAD"); self.base_salary.setFixedHeight(40)
        for rl, w in [("Prénom *:",self.first_name),("Nom *:",self.last_name),
                      ("Type:",self.emp_type),("Matière:",self.subject),
                      ("Téléphone:",self.phone),("Email:",self.email),
                      ("Adresse:",self.address),("Embauche:",self.hire_date),
                      ("Salaire base:",self.base_salary)]:
            form.addRow(lbl(rl), w)
        root.addLayout(form)
        br = QHBoxLayout(); br.addStretch()
        c = QPushButton("Annuler"); c.setObjectName("secondaryBtn"); c.clicked.connect(self.reject)
        s = QPushButton("💾  Enregistrer"); s.setObjectName("primaryBtn"); s.clicked.connect(self._save)
        br.addWidget(c); br.addWidget(s); root.addLayout(br)

    def _populate(self, e):
        self.first_name.setText(e.first_name); self.last_name.setText(e.last_name)
        idx = self.emp_type.findText(e.employee_type or "")
        if idx >= 0: self.emp_type.setCurrentIndex(idx)
        self.subject.setText(e.subject or ""); self.phone.setText(e.phone or "")
        self.email.setText(e.email or ""); self.address.setText(e.address or "")
        if e.hire_date:
            self.hire_date.setDate(QDate(e.hire_date.year, e.hire_date.month, e.hire_date.day))
        self.base_salary.setValue(e.base_salary or 0)

    def _save(self):
        if not self.first_name.text().strip():
            QMessageBox.warning(self,"Erreur","Prénom requis."); return
        from models.database import Employee
        e = self.employee if self.employee else Employee()
        if not self.employee: self.session.add(e)
        e.first_name = self.first_name.text().strip()
        e.last_name  = self.last_name.text().strip()
        e.employee_type = self.emp_type.currentText()
        e.subject    = self.subject.text().strip()
        e.phone      = self.phone.text().strip()
        e.email      = self.email.text().strip()
        e.address    = self.address.toPlainText()
        hd = self.hire_date.date()
        e.hire_date  = date(hd.year(), hd.month(), hd.day())
        e.base_salary = self.base_salary.value()
        self.session.commit(); self.accept()


class EmployeesWidget(QWidget):
    def __init__(self, session, current_user):
        super().__init__()
        self.session = session; self.current_user = current_user
        self.setStyleSheet("background:transparent;")
        self._build(); self.load_employees()

    def _build(self):
        from ui.widgets import page_header, filter_card, search_bar, build_table, action_btn, SummaryPill
        from PySide6.QtWidgets import QComboBox, QLabel as QL
        root = QVBoxLayout(self); root.setContentsMargins(24,20,24,20); root.setSpacing(16)

        hdr, add_btn = page_header("Gestion des Employés",
            "Enseignants, personnel administratif et chauffeurs.",
            "➕  Nouvel Employé", self._add)
        root.addWidget(hdr)

        self._search = search_bar("🔍  Rechercher un employé...")
        self._search.textChanged.connect(self.load_employees)
        self._type_f = QComboBox(); self._type_f.setFixedHeight(38); self._type_f.setFixedWidth(140)
        self._type_f.addItems(["Tous","Enseignants","Personnel","Chauffeurs"])
        self._type_f.currentIndexChanged.connect(self.load_employees)
        fc = filter_card(self._search, "stretch", QL("Type:"), self._type_f)
        root.addWidget(fc)

        pills = QHBoxLayout(); pills.setSpacing(10)
        self._pill_total    = SummaryPill("0 employés", "#3b82f6")
        self._pill_teachers = SummaryPill("0 enseignants", "#8b5cf6")
        self._pill_cost     = SummaryPill("0 MAD/mois", "#f59e0b")
        for p in [self._pill_total, self._pill_teachers, self._pill_cost]: pills.addWidget(p)
        pills.addStretch()
        pf = QFrame(); pf.setLayout(pills); pf.setStyleSheet("background:transparent;")
        root.addWidget(pf)

        self._table = build_table(
            ["Nom","Prénom","Type","Matière","Téléphone","Salaire","Embauche","Actions"], 7)
        root.addWidget(self._table)

    def load_employees(self):
        from models.database import Employee
        from ui.widgets import action_btn
        search = self._search.text().lower()
        tmap = {1:'teacher',2:'staff',3:'driver'}
        ti = self._type_f.currentIndex()
        q = self.session.query(Employee).filter_by(is_active=True)
        if ti > 0: q = q.filter_by(employee_type=tmap[ti])
        emps = q.all()
        if search: emps = [e for e in emps if search in f"{e.first_name} {e.last_name}".lower()]

        tlabels = {'teacher':'👨‍🏫 Enseignant','staff':'👤 Personnel','driver':'🚌 Chauffeur'}
        self._table.setRowCount(0)
        total_cost = 0
        for emp in emps:
            r = self._table.rowCount(); self._table.insertRow(r)
            for c, v in enumerate([emp.last_name, emp.first_name,
                tlabels.get(emp.employee_type, emp.employee_type),
                emp.subject or "—", emp.phone or "—",
                f"{emp.base_salary:,.0f} MAD",
                emp.hire_date.strftime("%d/%m/%Y") if emp.hire_date else "—"]):
                item = QTableWidgetItem(v); item.setTextAlignment(Qt.AlignCenter)
                self._table.setItem(r, c, item)
            aw = QWidget(); al = QHBoxLayout(aw)
            al.setContentsMargins(6,4,6,4); al.setSpacing(6)
            eb = action_btn("✏","#3b82f6","Modifier")
            sb = action_btn("💰","#22c55e","Payer salaire")
            db = action_btn("🗑","#ef4444","Désactiver")
            eb.clicked.connect(lambda _, eid=emp.id: self._edit(eid))
            sb.clicked.connect(lambda _, eid=emp.id: self._pay_salary(eid))
            db.clicked.connect(lambda _, eid=emp.id: self._delete(eid))
            al.addWidget(eb); al.addWidget(sb); al.addWidget(db)
            self._table.setCellWidget(r, 7, aw)
            total_cost += emp.base_salary or 0

        teachers = sum(1 for e in emps if e.employee_type=='teacher')
        self._pill_total.update_text(f"{len(emps)} employés")
        self._pill_teachers.update_text(f"{teachers} enseignants")
        self._pill_cost.update_text(f"{total_cost:,.0f} MAD/mois")

    def _add(self):
        dlg = EmployeeDialog(self.session, parent=self)
        if dlg.exec(): self.load_employees()

    def _edit(self, eid):
        from models.database import Employee
        e = self.session.query(Employee).get(eid)
        if e:
            dlg = EmployeeDialog(self.session, employee=e, parent=self)
            if dlg.exec(): self.load_employees()

    def _pay_salary(self, eid):
        from models.database import Employee, Salary
        e = self.session.query(Employee).get(eid)
        if not e: return
        dlg = QDialog(self); dlg.setWindowTitle(f"Payer — {e.first_name} {e.last_name}")
        dlg.setMinimumSize(400, 340)
        root = QVBoxLayout(dlg); root.setContentsMargins(28,24,28,24); root.setSpacing(14)
        root.addWidget(QLabel(f"💰  Paiement Salaire\n{e.first_name} {e.last_name}",
            styleSheet="color:#f8fafc; font-size:16px; font-weight:700; background:transparent;"))
        form = QFormLayout(); form.setSpacing(10); form.setLabelAlignment(Qt.AlignRight)
        mc = QComboBox(); mc.setFixedHeight(40)
        for m in MONTHS: mc.addItem(m)
        mc.setCurrentIndex(datetime.now().month-1)
        ys = QSpinBox(); ys.setRange(2020,2050); ys.setValue(datetime.now().year); ys.setFixedHeight(40)
        pr = QHBoxLayout(); pr.addWidget(mc); pr.addWidget(ys)
        pf = QFrame(); pf.setLayout(pr); pf.setStyleSheet("background:transparent;")
        amount_s = QDoubleSpinBox(); amount_s.setRange(0,99999); amount_s.setDecimals(2)
        amount_s.setSuffix(" MAD"); amount_s.setValue(e.base_salary or 0); amount_s.setFixedHeight(40)
        bonus_s = QDoubleSpinBox(); bonus_s.setRange(0,99999); bonus_s.setDecimals(2)
        bonus_s.setSuffix(" MAD"); bonus_s.setFixedHeight(40)
        for rl, w in [("Période:",pf),("Salaire:",amount_s),("Bonus:",bonus_s)]:
            form.addRow(lbl(rl), w)
        root.addLayout(form)
        br = QHBoxLayout(); br.addStretch()
        c = QPushButton("Annuler"); c.setObjectName("secondaryBtn"); c.clicked.connect(dlg.reject)
        s = QPushButton("💰  Payer"); s.setObjectName("primaryBtn")
        br.addWidget(c); br.addWidget(s)
        root.addLayout(br)
        def do_pay():
            sal = Salary(employee_id=e.id, amount=amount_s.value(), bonus=bonus_s.value(),
                month=mc.currentIndex()+1, year=ys.value(),
                paid_date=datetime.now(), is_paid=True)
            self.session.add(sal); self.session.commit()
            QMessageBox.information(dlg,"✅","Salaire enregistré!"); dlg.accept()
        s.clicked.connect(do_pay); dlg.exec()

    def _delete(self, eid):
        from models.database import Employee
        if QMessageBox.question(self,"Confirmer","Désactiver cet employé?",
            QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            e = self.session.query(Employee).get(eid)
            if e: e.is_active = False; self.session.commit(); self.load_employees()
