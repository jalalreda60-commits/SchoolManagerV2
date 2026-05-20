import os
from datetime import datetime, date
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QComboBox,
    QDateEdit, QTextEdit, QDoubleSpinBox, QMessageBox, QFrame, QSpinBox,
    QHeaderView, QAbstractItemView)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor

CATEGORIES = ['Loyer','Électricité','Eau','Internet','Fournitures',
              'Maintenance','Transport','Alimentation','Événements','Autres']

def lbl(t):
    l = QLabel(t); l.setStyleSheet("color:#94a3b8; font-size:12px; font-weight:500; background:transparent;")
    return l


class ExpenseDialog(QDialog):
    def __init__(self, session, expense=None, current_user=None, parent=None):
        super().__init__(parent)
        self.session = session; self.expense = expense; self.current_user = current_user
        self.setWindowTitle("Modifier Dépense" if expense else "Nouvelle Dépense")
        self.setMinimumSize(480, 420)
        self._build()
        if expense: self._populate(expense)

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(28,24,28,24); root.setSpacing(16)
        title = QLabel("📉  " + ("Modifier" if self.expense else "Nouvelle Dépense"))
        title.setStyleSheet("color:#f8fafc; font-size:20px; font-weight:700; background:transparent;")
        root.addWidget(title)
        form = QFormLayout(); form.setSpacing(12); form.setLabelAlignment(Qt.AlignRight)

        self.title_f = QLineEdit(); self.title_f.setPlaceholderText("Titre"); self.title_f.setFixedHeight(40)
        self.category = QComboBox(); self.category.setFixedHeight(40); self.category.addItems(CATEGORIES)
        self.exp_type = QComboBox(); self.exp_type.setFixedHeight(40); self.exp_type.addItems(["fixed","variable"])
        self.amount = QDoubleSpinBox(); self.amount.setRange(0,999999)
        self.amount.setDecimals(2); self.amount.setSuffix(" MAD"); self.amount.setFixedHeight(40)
        self.exp_date = QDateEdit(); self.exp_date.setCalendarPopup(True)
        self.exp_date.setDate(QDate.currentDate()); self.exp_date.setFixedHeight(40)
        self.desc = QTextEdit(); self.desc.setMaximumHeight(80); self.desc.setPlaceholderText("Description...")

        for rl, w in [("Titre *:",self.title_f),("Catégorie:",self.category),
                      ("Type:",self.exp_type),("Montant *:",self.amount),
                      ("Date:",self.exp_date),("Description:",self.desc)]:
            form.addRow(lbl(rl), w)
        root.addLayout(form)

        br = QHBoxLayout(); br.addStretch()
        c = QPushButton("Annuler"); c.setObjectName("secondaryBtn"); c.clicked.connect(self.reject)
        s = QPushButton("💾  Enregistrer"); s.setObjectName("primaryBtn"); s.clicked.connect(self._save)
        br.addWidget(c); br.addWidget(s); root.addLayout(br)

    def _populate(self, e):
        self.title_f.setText(e.title)
        idx = self.category.findText(e.category or "")
        if idx >= 0: self.category.setCurrentIndex(idx)
        idx2 = self.exp_type.findText(e.expense_type or "")
        if idx2 >= 0: self.exp_type.setCurrentIndex(idx2)
        self.amount.setValue(e.amount or 0)
        if e.expense_date:
            self.exp_date.setDate(QDate(e.expense_date.year, e.expense_date.month, e.expense_date.day))
        self.desc.setText(e.description or "")

    def _save(self):
        if not self.title_f.text().strip():
            QMessageBox.warning(self,"Erreur","Titre requis."); return
        from models.database import Expense
        e = self.expense if self.expense else Expense()
        if not self.expense: self.session.add(e)
        e.title = self.title_f.text().strip()
        e.category = self.category.currentText()
        e.expense_type = self.exp_type.currentText()
        e.amount = self.amount.value()
        d = self.exp_date.date()
        e.expense_date = date(d.year(), d.month(), d.day())
        e.description = self.desc.toPlainText()
        if self.current_user: e.created_by = self.current_user.id
        self.session.commit(); self.accept()


class ExpensesWidget(QWidget):
    def __init__(self, session, current_user):
        super().__init__()
        self.session = session; self.current_user = current_user
        self.setStyleSheet("background:transparent;")
        self._build(); self.load_expenses()

    def _build(self):
        from ui.widgets import page_header, filter_card, search_bar, build_table, action_btn, SummaryPill
        from PySide6.QtWidgets import QComboBox, QLabel as QL

        root = QVBoxLayout(self); root.setContentsMargins(24,20,24,20); root.setSpacing(16)

        hdr, _ = page_header("Gestion des Dépenses",
            "Dépenses fixes et variables — suivi et analytiques.",
            "➕  Nouvelle Dépense", self._add)
        root.addWidget(hdr)

        self._search = search_bar("🔍  Rechercher une dépense...")
        self._search.textChanged.connect(self.load_expenses)
        self._year_f = QSpinBox(); self._year_f.setRange(2020,2050)
        self._year_f.setValue(datetime.now().year); self._year_f.setFixedHeight(38); self._year_f.setFixedWidth(80)
        self._year_f.valueChanged.connect(self.load_expenses)
        self._cat_f = QComboBox(); self._cat_f.setFixedHeight(38); self._cat_f.setFixedWidth(140)
        self._cat_f.addItem("Toutes catégories")
        self._cat_f.addItems(CATEGORIES)
        self._cat_f.currentIndexChanged.connect(self.load_expenses)

        fc = filter_card(self._search, "stretch", QL("Année:"), self._year_f, QL("Catégorie:"), self._cat_f)
        root.addWidget(fc)

        pills = QHBoxLayout(); pills.setSpacing(10)
        self._pill_total = SummaryPill("0 dépenses", "#ef4444")
        self._pill_sum   = SummaryPill("0 MAD", "#f59e0b")
        self._pill_fixed = SummaryPill("0 fixes", "#8b5cf6")
        for p in [self._pill_total, self._pill_sum, self._pill_fixed]: pills.addWidget(p)
        pills.addStretch()
        pf = QFrame(); pf.setLayout(pills); pf.setStyleSheet("background:transparent;")
        root.addWidget(pf)

        self._table = build_table(["Titre","Catégorie","Type","Montant","Date","Description","Actions"], 6)
        root.addWidget(self._table)

    def load_expenses(self):
        from models.database import Expense
        from sqlalchemy import func
        from ui.widgets import action_btn
        search = self._search.text().lower()
        year = self._year_f.value()
        cat = self._cat_f.currentText()

        q = self.session.query(Expense).filter(
            func.strftime('%Y', Expense.expense_date)==str(year))
        if cat != "Toutes catégories": q = q.filter_by(category=cat)
        exps = q.order_by(Expense.expense_date.desc()).all()
        if search: exps = [e for e in exps if search in e.title.lower()]

        self._table.setRowCount(0)
        total = fixed_count = 0
        for exp in exps:
            r = self._table.rowCount(); self._table.insertRow(r)
            type_label = "🔒 Fixe" if exp.expense_type == "fixed" else "🔄 Variable"
            for c, v in enumerate([exp.title,
                exp.category or "—", type_label,
                f"{exp.amount:,.2f} MAD",
                exp.expense_date.strftime("%d/%m/%Y") if exp.expense_date else "—",
                (exp.description or "")[:45] + ("…" if len(exp.description or "")>45 else "")]):
                item = QTableWidgetItem(v); item.setTextAlignment(Qt.AlignCenter)
                if c == 3: item.setForeground(QColor("#ef4444"))
                self._table.setItem(r, c, item)
            aw = QWidget(); al = QHBoxLayout(aw)
            al.setContentsMargins(6,4,6,4); al.setSpacing(6)
            eb = action_btn("✏","#3b82f6","Modifier")
            db = action_btn("🗑","#ef4444","Supprimer")
            eb.clicked.connect(lambda _, eid=exp.id: self._edit(eid))
            db.clicked.connect(lambda _, eid=exp.id: self._delete(eid))
            al.addWidget(eb); al.addWidget(db)
            self._table.setCellWidget(r, 6, aw)
            total += exp.amount
            if exp.expense_type == "fixed": fixed_count += 1

        self._pill_total.update_text(f"{len(exps)} dépenses")
        self._pill_sum.update_text(f"{total:,.2f} MAD")
        self._pill_fixed.update_text(f"{fixed_count} fixes")

    def _add(self):
        dlg = ExpenseDialog(self.session, current_user=self.current_user, parent=self)
        if dlg.exec(): self.load_expenses()

    def _edit(self, eid):
        from models.database import Expense
        e = self.session.query(Expense).get(eid)
        if e:
            dlg = ExpenseDialog(self.session, expense=e, current_user=self.current_user, parent=self)
            if dlg.exec(): self.load_expenses()

    def _delete(self, eid):
        from models.database import Expense
        if QMessageBox.question(self,"Confirmer","Supprimer cette dépense?",
            QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            e = self.session.query(Expense).get(eid)
            if e: self.session.delete(e); self.session.commit(); self.load_expenses()

from PySide6.QtWidgets import QLineEdit
