import os
from datetime import datetime, date
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QComboBox,
    QDateEdit, QTextEdit, QCheckBox, QFileDialog, QMessageBox, QFrame, QHeaderView,
    QAbstractItemView, QDoubleSpinBox, QScrollArea, QSizePolicy)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap, QColor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLASSES = ['PS','MS','GS','CP','CE1','CE2','CM1','CM2','6EME','1AC','2AC','3AC','TC','1BAC','2BAC']


def lbl(text):
    l = QLabel(text)
    l.setStyleSheet("color:#94a3b8; font-size:12px; font-weight:500; background:transparent;")
    return l

def field(ph=""):
    f = QLineEdit(); f.setPlaceholderText(ph); f.setFixedHeight(40)
    return f


class StudentDialog(QDialog):
    def __init__(self, session, student=None, parent=None):
        super().__init__(parent)
        self.session = session; self.student = student; self.photo_path = None
        self.setWindowTitle("Modifier Élève" if student else "Nouvel Élève")
        self.setMinimumSize(680, 680)
        self._build()
        if student: self._populate(student)

    def _build(self):
        from themes.dark_theme import CARD, BORDER, ACCENT, TEXT, TEXT2
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(20)

        title = QLabel("👤  " + ("Modifier" if self.student else "Nouvel Élève"))
        title.setStyleSheet(f"color:#f8fafc; font-size:20px; font-weight:700; background:transparent;")
        root.addWidget(title)

        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none; background:transparent;}")
        inner = QWidget(); inner.setStyleSheet("background:transparent;")
        form = QFormLayout(inner); form.setSpacing(14); form.setLabelAlignment(Qt.AlignRight)
        form.setContentsMargins(0,0,0,0)

        # Photo
        photo_row = QHBoxLayout()
        self.photo_lbl = QLabel()
        self.photo_lbl.setFixedSize(80, 80)
        self.photo_lbl.setStyleSheet(f"border:2px dashed {BORDER}; border-radius:10px; background:#0f172a;")
        self.photo_lbl.setAlignment(Qt.AlignCenter); self.photo_lbl.setText("📷")
        photo_row.addWidget(self.photo_lbl)
        pb = QPushButton("  Choisir Photo"); pb.setObjectName("secondaryBtn"); pb.setFixedHeight(36)
        pb.clicked.connect(self._pick_photo)
        photo_row.addWidget(pb); photo_row.addStretch()
        pf = QFrame(); pf.setLayout(photo_row); pf.setStyleSheet("background:transparent;")
        form.addRow(lbl("Photo:"), pf)

        self.first_name = field("Prénom")
        self.last_name  = field("Nom")
        self.gender = QComboBox(); self.gender.addItems(["Masculin","Féminin"]); self.gender.setFixedHeight(40)
        self.birth_date = QDateEdit(); self.birth_date.setCalendarPopup(True)
        self.birth_date.setDate(QDate(2015,1,1)); self.birth_date.setFixedHeight(40)
        self.address = QTextEdit(); self.address.setMaximumHeight(70)
        self.parent_name = field("Nom du parent")
        self.parent_phone = field("+212 6XX XXX XXX")
        self.emergency_phone = field("+212 6XX XXX XXX")

        self.class_combo = QComboBox(); self.class_combo.setFixedHeight(40)
        self.class_combo.addItem("-- Sélectionner --", None)
        from models.database import Class
        for cls in self.session.query(Class).all():
            self.class_combo.addItem(cls.name, cls.id)
        self.class_combo.currentIndexChanged.connect(self._update_fee)

        self.monthly_fee = QDoubleSpinBox(); self.monthly_fee.setRange(0,99999)
        self.monthly_fee.setDecimals(2); self.monthly_fee.setSuffix(" MAD")
        self.monthly_fee.setFixedHeight(40)

        checks = QHBoxLayout()
        self.has_transport  = QCheckBox("Transport inclus")
        self.insurance_paid = QCheckBox("Assurance payée")
        checks.addWidget(self.has_transport); checks.addWidget(self.insurance_paid); checks.addStretch()
        cf = QFrame(); cf.setLayout(checks); cf.setStyleSheet("background:transparent;")

        self.notes = QTextEdit(); self.notes.setMaximumHeight(70); self.notes.setPlaceholderText("Remarques...")

        for row_lbl, widget in [
            ("Prénom *:", self.first_name), ("Nom *:", self.last_name),
            ("Genre:", self.gender), ("Naissance:", self.birth_date),
            ("Adresse:", self.address), ("Parent:", self.parent_name),
            ("Tél. Parent:", self.parent_phone), ("Tél. Urgence:", self.emergency_phone),
            ("Classe *:", self.class_combo), ("Frais mensuel:", self.monthly_fee),
            ("Options:", cf), ("Notes:", self.notes),
        ]:
            form.addRow(lbl(row_lbl), widget)

        scroll.setWidget(inner); root.addWidget(scroll)

        btn_row = QHBoxLayout(); btn_row.addStretch()
        cancel = QPushButton("Annuler"); cancel.setObjectName("secondaryBtn"); cancel.clicked.connect(self.reject)
        save   = QPushButton("💾  Enregistrer"); save.setObjectName("primaryBtn"); save.clicked.connect(self._save)
        btn_row.addWidget(cancel); btn_row.addWidget(save)
        root.addLayout(btn_row)

    def _update_fee(self):
        from models.database import Class
        cid = self.class_combo.currentData()
        if cid:
            cls = self.session.query(Class).get(cid)
            if cls: self.monthly_fee.setValue(cls.monthly_fee)

    def _pick_photo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Photo", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.photo_path = path
            px = QPixmap(path).scaled(80,80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.photo_lbl.setPixmap(px)

    def _populate(self, s):
        self.first_name.setText(s.first_name); self.last_name.setText(s.last_name)
        if s.gender:
            idx = self.gender.findText(s.gender)
            if idx >= 0: self.gender.setCurrentIndex(idx)
        if s.birth_date:
            self.birth_date.setDate(QDate(s.birth_date.year, s.birth_date.month, s.birth_date.day))
        self.address.setText(s.address or ""); self.parent_name.setText(s.parent_name or "")
        self.parent_phone.setText(s.parent_phone or ""); self.emergency_phone.setText(s.emergency_phone or "")
        for i in range(self.class_combo.count()):
            if self.class_combo.itemData(i) == s.class_id:
                self.class_combo.setCurrentIndex(i); break
        self.monthly_fee.setValue(s.monthly_fee or 0)
        self.has_transport.setChecked(s.has_transport)
        self.insurance_paid.setChecked(s.insurance_paid)
        self.notes.setText(s.notes or "")
        if s.photo:
            fp = os.path.join(BASE_DIR, s.photo) if not os.path.isabs(s.photo) else s.photo
            if os.path.exists(fp):
                px = QPixmap(fp).scaled(80,80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.photo_lbl.setPixmap(px)

    def _save(self):
        if not self.first_name.text().strip() or not self.last_name.text().strip():
            QMessageBox.warning(self, "Erreur", "Prénom et nom requis."); return
        if self.class_combo.currentData() is None:
            QMessageBox.warning(self, "Erreur", "Sélectionnez une classe."); return
        from models.database import Student
        import random, string
        s = self.student if self.student else Student()
        if not self.student:
            s.student_code = f"STU-{datetime.now().year}-{''.join(random.choices(string.digits,k=4))}"
            s.registration_date = date.today()
            self.session.add(s)
        s.first_name = self.first_name.text().strip()
        s.last_name  = self.last_name.text().strip()
        s.gender     = self.gender.currentText()
        bd = self.birth_date.date()
        s.birth_date = date(bd.year(), bd.month(), bd.day())
        s.address    = self.address.toPlainText()
        s.parent_name = self.parent_name.text().strip()
        s.parent_phone = self.parent_phone.text().strip()
        s.emergency_phone = self.emergency_phone.text().strip()
        s.class_id   = self.class_combo.currentData()
        s.monthly_fee = self.monthly_fee.value()
        s.has_transport = self.has_transport.isChecked()
        s.insurance_paid = self.insurance_paid.isChecked()
        s.notes      = self.notes.toPlainText()
        if self.photo_path:
            import shutil
            pd = os.path.join(BASE_DIR,'assets','photos'); os.makedirs(pd, exist_ok=True)
            ext = os.path.splitext(self.photo_path)[1]
            dest = os.path.join(pd, f"{s.student_code}{ext}")
            shutil.copy2(self.photo_path, dest)
            s.photo = os.path.join('assets','photos',f"{s.student_code}{ext}")
        self.session.commit(); self.accept()


class StudentsWidget(QWidget):
    def __init__(self, session, current_user):
        super().__init__()
        self.session = session; self.current_user = current_user
        self.setStyleSheet("background:transparent;")
        self._all = []
        self._build()
        self.load_students()

    def _build(self):
        from ui.widgets import page_header, filter_card, search_bar, build_table, action_btn, SummaryPill
        root = QVBoxLayout(self); root.setContentsMargins(24,20,24,20); root.setSpacing(16)

        hdr, add_btn = page_header("Gestion des Élèves",
            "Gérez les dossiers, inscriptions et informations des élèves.",
            "➕  Nouvel Élève", self._add)
        root.addWidget(hdr)

        # Filter row
        self._search = search_bar("🔍  Rechercher par nom, code, parent...")
        self._search.textChanged.connect(self._filter)
        from PySide6.QtWidgets import QComboBox, QLabel as QL
        self._class_f = QComboBox(); self._class_f.setFixedHeight(38); self._class_f.setFixedWidth(120)
        self._class_f.addItem("Toutes", None)
        for c in CLASSES: self._class_f.addItem(c, c)
        self._class_f.currentIndexChanged.connect(self._filter)
        self._status_f = QComboBox(); self._status_f.setFixedHeight(38); self._status_f.setFixedWidth(120)
        self._status_f.addItems(["Tous","Actifs","Inactifs"])
        self._status_f.currentIndexChanged.connect(self._filter)
        fc = filter_card(self._search, "stretch", QL("Classe:"), self._class_f, QL("Statut:"), self._status_f)
        root.addWidget(fc)

        # Summary pills
        pills_row = QHBoxLayout(); pills_row.setSpacing(10)
        self._pill_total    = SummaryPill("0 élèves", "#3b82f6")
        self._pill_transport= SummaryPill("0 transport", "#fb923c")
        self._pill_unpaid   = SummaryPill("0 impayés", "#ef4444")
        for p in [self._pill_total, self._pill_transport, self._pill_unpaid]:
            pills_row.addWidget(p)
        pills_row.addStretch()
        pr = QFrame(); pr.setLayout(pills_row); pr.setStyleSheet("background:transparent;")
        root.addWidget(pr)

        # Table
        self._table = build_table(
            ["Code","Prénom","Nom","Classe","Parent","Téléphone","Transport","Assurance","Actions"], 8)
        root.addWidget(self._table)

    def load_students(self):
        from models.database import Student, Class
        self._all = self.session.query(Student).join(Class, isouter=True).all()
        self._display(self._all)

    def _display(self, students):
        from ui.widgets import action_btn
        from PySide6.QtWidgets import QTableWidgetItem as QTI
        self._table.setRowCount(0)
        for s in students:
            r = self._table.rowCount(); self._table.insertRow(r)
            row_data = [
                s.student_code or "",
                s.first_name, s.last_name,
                s.class_.name if s.class_ else "—",
                s.parent_name or "—",
                s.parent_phone or "—",
                "✅" if s.has_transport else "—",
                "✅" if s.insurance_paid else "—",
            ]
            for c, val in enumerate(row_data):
                item = QTI(val); item.setTextAlignment(Qt.AlignCenter)
                if c == 0: item.setForeground(QColor("#60a5fa"))
                if val == "✅": item.setForeground(QColor("#22c55e"))
                self._table.setItem(r, c, item)

            # Actions
            aw = QWidget(); al = QHBoxLayout(aw)
            al.setContentsMargins(6,4,6,4); al.setSpacing(6)
            eb = action_btn("✏", "#3b82f6", "Modifier")
            pb = action_btn("💳", "#22c55e", "Paiement")
            db = action_btn("🗑", "#ef4444", "Supprimer")
            eb.clicked.connect(lambda _, sid=s.id: self._edit(sid))
            pb.clicked.connect(lambda _, sid=s.id: self._payment(sid))
            db.clicked.connect(lambda _, sid=s.id: self._delete(sid))
            al.addWidget(eb); al.addWidget(pb); al.addWidget(db)
            self._table.setCellWidget(r, 8, aw)

        # Update pills
        active = [s for s in students if s.is_active]
        transport = [s for s in students if s.has_transport]
        from datetime import datetime
        now = datetime.now()
        from models.database import Payment
        paid_ids = [p[0] for p in self.session.query(Payment.student_id).filter(
            Payment.month==now.month, Payment.year==now.year,
            Payment.payment_type=='monthly').all()]
        unpaid = [s for s in active if s.id not in paid_ids]
        self._pill_total.update_text(f"{len(students)} élèves")
        self._pill_transport.update_text(f"{len(transport)} transport")
        self._pill_unpaid.update_text(f"{len(unpaid)} impayés")

    def _filter(self):
        text   = self._search.text().lower()
        cls_f  = self._class_f.currentData()
        status = self._status_f.currentIndex()
        result = []
        for s in self._all:
            if status == 1 and not s.is_active: continue
            if status == 2 and s.is_active: continue
            if cls_f and (not s.class_ or s.class_.name != cls_f): continue
            if text and text not in f"{s.first_name} {s.last_name} {s.student_code or ''}".lower(): continue
            result.append(s)
        self._display(result)

    def _add(self):
        dlg = StudentDialog(self.session, parent=self)
        if dlg.exec(): self.load_students()

    def _edit(self, sid):
        from models.database import Student
        s = self.session.query(Student).get(sid)
        if s:
            dlg = StudentDialog(self.session, student=s, parent=self)
            if dlg.exec(): self.load_students()

    def _delete(self, sid):
        from models.database import Student
        if QMessageBox.question(self, "Confirmer","Désactiver cet élève?",
            QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            s = self.session.query(Student).get(sid)
            if s: s.is_active = False; self.session.commit(); self.load_students()

    def _payment(self, sid):
        from ui.payments import PaymentDialog
        from models.database import Student
        s = self.session.query(Student).get(sid)
        if s:
            dlg = PaymentDialog(self.session, s, self.current_user, parent=self)
            if dlg.exec(): self.load_students()
