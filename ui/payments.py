import os
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QComboBox, QDoubleSpinBox, QTextEdit, QMessageBox, QFrame, QSpinBox,
    QCheckBox, QHeaderView, QAbstractItemView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONTHS = ['Janvier','Février','Mars','Avril','Mai','Juin',
          'Juillet','Août','Septembre','Octobre','Novembre','Décembre']

def lbl(text):
    l = QLabel(text)
    l.setStyleSheet("color:#94a3b8; font-size:12px; font-weight:500; background:transparent;")
    return l


class PaymentDialog(QDialog):
    def __init__(self, session, student, current_user, parent=None):
        super().__init__(parent)
        self.session = session; self.student = student; self.current_user = current_user
        self.setWindowTitle(f"Paiement — {student.first_name} {student.last_name}")
        self.setMinimumSize(520, 560)
        self._build()

    def _build(self):
        from themes.dark_theme import CARD, BORDER, ACCENT, TEXT, TEXT2, SUCCESS
        root = QVBoxLayout(self); root.setContentsMargins(28,24,28,24); root.setSpacing(18)

        title = QLabel(f"💳  Paiement")
        title.setStyleSheet("color:#f8fafc; font-size:20px; font-weight:700; background:transparent;")
        root.addWidget(title)

        # Student info pill
        info = QFrame()
        info.setStyleSheet(f"""QFrame{{background:rgba(59,130,246,0.08);
            border:1px solid rgba(59,130,246,0.2); border-radius:10px;}}""")
        il = QHBoxLayout(info); il.setContentsMargins(16,12,16,12); il.setSpacing(20)
        name_l = QLabel(f"👤  {self.student.first_name} {self.student.last_name}")
        name_l.setStyleSheet(f"background:transparent; color:{ACCENT}; font-size:15px; font-weight:700;")
        il.addWidget(name_l)
        cls_l = QLabel(f"🎓  {self.student.class_.name if self.student.class_ else '—'}")
        cls_l.setStyleSheet(f"background:transparent; color:#94a3b8; font-size:12px;")
        il.addWidget(cls_l)
        il.addStretch()
        fee_l = QLabel(f"Frais: {self.student.monthly_fee:,.0f} MAD/mois")
        fee_l.setStyleSheet(f"background:transparent; color:{SUCCESS}; font-size:12px; font-weight:600;")
        il.addWidget(fee_l)
        root.addWidget(info)

        # Form
        form = QFormLayout(); form.setSpacing(12); form.setLabelAlignment(Qt.AlignRight)
        self.pay_type = QComboBox(); self.pay_type.setFixedHeight(40)
        self.pay_type.addItems(["Mensualité","Assurance","Transport"])
        self.pay_type.currentIndexChanged.connect(self._update_amount)

        self.month_combo = QComboBox(); self.month_combo.setFixedHeight(40)
        for m in MONTHS: self.month_combo.addItem(m)
        self.month_combo.setCurrentIndex(datetime.now().month-1)

        self.year_spin = QSpinBox(); self.year_spin.setRange(2020,2050)
        self.year_spin.setValue(datetime.now().year); self.year_spin.setFixedHeight(40)

        period_row = QHBoxLayout()
        period_row.addWidget(self.month_combo)
        period_row.addWidget(self.year_spin)
        pf = QFrame(); pf.setLayout(period_row); pf.setStyleSheet("background:transparent;")

        self.amount = QDoubleSpinBox(); self.amount.setRange(0,99999)
        self.amount.setDecimals(2); self.amount.setSuffix(" MAD"); self.amount.setFixedHeight(40)

        self.notes = QTextEdit(); self.notes.setMaximumHeight(70); self.notes.setPlaceholderText("Notes...")
        self.print_cb = QCheckBox("Générer le reçu PDF automatiquement")
        self.print_cb.setChecked(True)

        for row, w in [("Type:",self.pay_type),("Période:",pf),
                       ("Montant:",self.amount),("Notes:",self.notes),("",self.print_cb)]:
            form.addRow(lbl(row), w)
        root.addLayout(form)

        # Recent payments mini table
        prev_lbl = QLabel("Paiements récents")
        prev_lbl.setStyleSheet("color:#94a3b8; font-size:12px; font-weight:600; background:transparent;")
        root.addWidget(prev_lbl)
        self._prev = QTableWidget()
        self._prev.setColumnCount(5)
        self._prev.setHorizontalHeaderLabels(["Type","Mois","Année","Montant","Date"])
        self._prev.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._prev.setMaximumHeight(120); self._prev.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._prev.verticalHeader().setVisible(False); self._prev.setShowGrid(False)
        self._load_prev()
        root.addWidget(self._prev)

        btn_row = QHBoxLayout(); btn_row.addStretch()
        cancel = QPushButton("Annuler"); cancel.setObjectName("secondaryBtn"); cancel.clicked.connect(self.reject)
        pay    = QPushButton("💳  Confirmer le Paiement"); pay.setObjectName("primaryBtn"); pay.clicked.connect(self._save)
        btn_row.addWidget(cancel); btn_row.addWidget(pay)
        root.addLayout(btn_row)
        self._update_amount()

    def _update_amount(self):
        from models.database import Setting
        idx = self.pay_type.currentIndex()
        if idx == 0: self.amount.setValue(self.student.monthly_fee or 0)
        elif idx == 1:
            s = self.session.query(Setting).filter_by(key='insurance_fee').first()
            self.amount.setValue(float(s.value) if s else 200)
        elif idx == 2:
            s = self.session.query(Setting).filter_by(key='transport_fee').first()
            self.amount.setValue(float(s.value) if s else 300)

    def _load_prev(self):
        from models.database import Payment
        pays = self.session.query(Payment).filter_by(
            student_id=self.student.id).order_by(Payment.payment_date.desc()).limit(5).all()
        self._prev.setRowCount(0)
        tmap = {'monthly':'Mensualité','insurance':'Assurance','transport':'Transport'}
        for p in pays:
            r = self._prev.rowCount(); self._prev.insertRow(r)
            for c, v in enumerate([
                tmap.get(p.payment_type, p.payment_type),
                MONTHS[p.month-1] if p.month and 1<=p.month<=12 else "—",
                str(p.year or ""),
                f"{p.amount:,.2f} MAD",
                p.payment_date.strftime("%d/%m/%Y") if p.payment_date else "—"
            ]):
                item = QTableWidgetItem(v); item.setTextAlignment(Qt.AlignCenter)
                self._prev.setItem(r, c, item)
            self._prev.setRowHeight(r, 32)

    def _save(self):
        from models.database import Payment, Receipt, Setting
        tmap = {0:'monthly',1:'insurance',2:'transport'}
        ptype = tmap[self.pay_type.currentIndex()]
        amount = self.amount.value(); month = self.month_combo.currentIndex()+1
        year = self.year_spin.value()
        if amount <= 0:
            QMessageBox.warning(self,"Erreur","Montant invalide."); return
        if ptype=='monthly':
            ex = self.session.query(Payment).filter_by(student_id=self.student.id,
                payment_type='monthly',month=month,year=year).first()
            if ex and QMessageBox.question(self,"Doublon",
                    f"Paiement existant pour {MONTHS[month-1]} {year}. Continuer?",
                    QMessageBox.Yes|QMessageBox.No) == QMessageBox.No:
                return
        s = self.session.query(Setting).filter_by(key='receipt_counter').first()
        counter = int(s.value)+1 if s else 1
        rec_num = f"REC-{year}-{counter:06d}"
        if s: s.value = str(counter)
        else: self.session.add(Setting(key='receipt_counter',value=str(counter)))

        pay = Payment(student_id=self.student.id, payment_type=ptype, amount=amount,
            month=month, year=year, receipt_number=rec_num,
            notes=self.notes.toPlainText(), created_by=self.current_user.id)
        self.session.add(pay); self.session.flush()

        if self.print_cb.isChecked():
            school = {}
            for k in ['school_name','school_address','school_phone','currency']:
                sv = self.session.query(Setting).filter_by(key=k).first()
                school[k] = sv.value if sv else ''
            from services.receipt_service import generate_receipt_pdf
            try:
                pdf = generate_receipt_pdf({
                    'receipt_number':rec_num,
                    'student_name':f"{self.student.first_name} {self.student.last_name}",
                    'student_code':self.student.student_code or '',
                    'class_name':self.student.class_.name if self.student.class_ else '',
                    'parent_name':self.student.parent_name or '',
                    'payment_type':ptype, 'amount':amount,
                    'month':month, 'year':year,
                    'payment_date':datetime.now().strftime('%d/%m/%Y %H:%M'),
                    'cashier':self.current_user.full_name or self.current_user.username,
                    **school,
                })
                self.session.add(Receipt(receipt_number=rec_num, student_id=self.student.id,
                    payment_id=pay.id, amount=amount, payment_type=ptype,
                    pdf_path=pdf, created_by=self.current_user.id))
                import subprocess, platform
                if platform.system()=='Windows': os.startfile(pdf)
                elif platform.system()=='Darwin': subprocess.run(['open',pdf])
                else: subprocess.run(['xdg-open',pdf])
                QMessageBox.information(self,"✅ Paiement enregistré",
                    f"Reçu: {rec_num}\nMontant: {amount:,.2f} MAD")
            except Exception as e:
                QMessageBox.warning(self,"Avertissement",f"Paiement OK mais erreur PDF:\n{e}")

        if ptype=='insurance': self.student.insurance_paid = True
        self.session.commit(); self.accept()


class PaymentsWidget(QWidget):
    def __init__(self, session, current_user):
        super().__init__()
        self.session = session; self.current_user = current_user
        self.setStyleSheet("background:transparent;")
        self._build(); self.load_payments()

    def _build(self):
        from ui.widgets import page_header, filter_card, search_bar, build_table, SummaryPill
        from PySide6.QtWidgets import QComboBox, QLabel as QL
        root = QVBoxLayout(self); root.setContentsMargins(24,20,24,20); root.setSpacing(16)

        hdr, _ = page_header("Gestion des Paiements",
            "Historique et suivi de tous les paiements enregistrés.")
        root.addWidget(hdr)

        self._search = search_bar("🔍  Nom, code reçu...")
        self._type_f = QComboBox(); self._type_f.setFixedHeight(38); self._type_f.setFixedWidth(140)
        self._type_f.addItems(["Tous types","Mensualité","Assurance","Transport"])
        self._type_f.currentIndexChanged.connect(self.load_payments)
        self._month_f = QComboBox(); self._month_f.setFixedHeight(38); self._month_f.setFixedWidth(120)
        self._month_f.addItem("Tous mois",0)
        for i,m in enumerate(MONTHS,1): self._month_f.addItem(m,i)
        self._month_f.setCurrentIndex(datetime.now().month)
        self._month_f.currentIndexChanged.connect(self.load_payments)
        self._year_f = QSpinBox(); self._year_f.setRange(2020,2050)
        self._year_f.setValue(datetime.now().year); self._year_f.setFixedHeight(38); self._year_f.setFixedWidth(80)
        self._year_f.valueChanged.connect(self.load_payments)
        self._search.textChanged.connect(self.load_payments)

        fc = filter_card(self._search, "stretch", QL("Type:"), self._type_f,
                         QL("Mois:"), self._month_f, QL("Année:"), self._year_f)
        root.addWidget(fc)

        pills = QHBoxLayout(); pills.setSpacing(10)
        self._pill_total = SummaryPill("0 paiements", "#3b82f6")
        self._pill_sum   = SummaryPill("0 MAD", "#22c55e")
        for p in [self._pill_total, self._pill_sum]: pills.addWidget(p)
        pills.addStretch()
        pf = QFrame(); pf.setLayout(pills); pf.setStyleSheet("background:transparent;")
        root.addWidget(pf)

        self._table = build_table(["Reçu","Élève","Classe","Type","Mois","Année","Montant","Date"])
        self._table.doubleClicked.connect(self._open_pdf)
        root.addWidget(self._table)

    def load_payments(self):
        from models.database import Payment, Student
        from sqlalchemy import func
        tmap = {1:'monthly',2:'insurance',3:'transport'}
        q = self.session.query(Payment).join(Student, isouter=True)
        ti = self._type_f.currentIndex()
        if ti > 0: q = q.filter(Payment.payment_type==tmap[ti])
        month = self._month_f.currentData()
        if month: q = q.filter(Payment.month==month)
        q = q.filter(Payment.year==self._year_f.value())
        pays = q.order_by(Payment.payment_date.desc()).all()
        search = self._search.text().lower()
        if search:
            pays = [p for p in pays if search in
                f"{p.student.first_name if p.student else ''} {p.student.last_name if p.student else ''} {p.receipt_number or ''}".lower()]
        tlabels = {'monthly':'Mensualité','insurance':'Assurance','transport':'Transport'}
        self._table.setRowCount(0)
        total = 0
        for p in pays:
            r = self._table.rowCount(); self._table.insertRow(r)
            st = p.student
            vals = [p.receipt_number or "—",
                f"{st.first_name} {st.last_name}" if st else "—",
                st.class_.name if st and st.class_ else "—",
                tlabels.get(p.payment_type, p.payment_type),
                MONTHS[p.month-1] if p.month and 1<=p.month<=12 else "—",
                str(p.year or ""), f"{p.amount:,.2f} MAD",
                p.payment_date.strftime("%d/%m/%Y %H:%M") if p.payment_date else "—"]
            for c, v in enumerate(vals):
                item = QTableWidgetItem(v); item.setTextAlignment(Qt.AlignCenter)
                if c == 0: item.setForeground(QColor("#60a5fa"))
                if c == 6: item.setForeground(QColor("#22c55e"))
                self._table.setItem(r, c, item)
            total += p.amount
        self._pill_total.update_text(f"{len(pays)} paiements")
        self._pill_sum.update_text(f"{total:,.2f} MAD")

    def _open_pdf(self):
        from models.database import Receipt
        row = self._table.currentRow()
        if row < 0: return
        rn = self._table.item(row, 0).text()
        rec = self.session.query(Receipt).filter_by(receipt_number=rn).first()
        if rec and rec.pdf_path and os.path.exists(rec.pdf_path):
            import subprocess, platform
            if platform.system()=='Windows': os.startfile(rec.pdf_path)
            elif platform.system()=='Darwin': subprocess.run(['open',rec.pdf_path])
            else: subprocess.run(['xdg-open',rec.pdf_path])
        else:
            QMessageBox.information(self,"Info","Aucun PDF pour ce paiement.")
