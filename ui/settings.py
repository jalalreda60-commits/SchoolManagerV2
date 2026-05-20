import os, shutil
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QComboBox,
    QMessageBox, QFrame, QHeaderView, QAbstractItemView, QDoubleSpinBox,
    QTabWidget, QGroupBox, QTextEdit, QScrollArea, QFileDialog)
from PySide6.QtCore import Qt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def lbl(t):
    l = QLabel(t); l.setStyleSheet("color:#94a3b8; font-size:12px; font-weight:500; background:transparent;")
    return l


class SettingsWidget(QWidget):
    def __init__(self, session, current_user):
        super().__init__()
        self.session = session; self.current_user = current_user
        self.setStyleSheet("background:transparent;")
        self._build(); self._load()

    def _build(self):
        from ui.widgets import page_header
        root = QVBoxLayout(self); root.setContentsMargins(24,20,24,20); root.setSpacing(16)

        hdr, _ = page_header("Paramètres","Configuration générale du système de gestion scolaire.")
        root.addWidget(hdr)

        tabs = QTabWidget(); root.addWidget(tabs)

        # ── School tab ────────────────────────────────────────────────────────
        school_tab = QWidget(); school_tab.setStyleSheet("background:transparent;")
        st_lay = QVBoxLayout(school_tab); st_lay.setContentsMargins(20,20,20,20); st_lay.setSpacing(16)

        sg = QGroupBox("Informations de l'établissement")
        sf = QFormLayout(sg); sf.setSpacing(12); sf.setLabelAlignment(Qt.AlignRight)
        def f(ph=""): fi = QLineEdit(); fi.setPlaceholderText(ph); fi.setFixedHeight(40); return fi
        self.s_name    = f("Nom de l'école"); self.s_address = f("Adresse")
        self.s_phone   = f("Téléphone");      self.s_email   = f("Email")
        self.s_currency = QComboBox(); self.s_currency.setFixedHeight(40)
        self.s_currency.addItems(["MAD","EUR","USD","XOF"])
        for rl, w in [("Nom école:",self.s_name),("Adresse:",self.s_address),
                      ("Téléphone:",self.s_phone),("Email:",self.s_email),
                      ("Devise:",self.s_currency)]:
            sf.addRow(lbl(rl), w)
        st_lay.addWidget(sg)

        fg = QGroupBox("Frais par défaut")
        ff = QFormLayout(fg); ff.setSpacing(12); ff.setLabelAlignment(Qt.AlignRight)
        def ds(): d = QDoubleSpinBox(); d.setRange(0,99999); d.setDecimals(2); d.setSuffix(" MAD"); d.setFixedHeight(40); return d
        self.s_transport = ds(); self.s_insurance = ds()
        ff.addRow(lbl("Frais transport:"), self.s_transport)
        ff.addRow(lbl("Frais assurance:"), self.s_insurance)
        st_lay.addWidget(fg)

        save_btn = QPushButton("💾  Enregistrer les paramètres")
        save_btn.setObjectName("primaryBtn"); save_btn.setFixedWidth(260)
        save_btn.clicked.connect(self._save_school)
        st_lay.addWidget(save_btn)
        st_lay.addStretch()
        tabs.addTab(school_tab, "🏫  École")

        # ── Backup tab ────────────────────────────────────────────────────────
        bk_tab = QWidget(); bk_tab.setStyleSheet("background:transparent;")
        bk_lay = QVBoxLayout(bk_tab); bk_lay.setContentsMargins(20,20,20,20); bk_lay.setSpacing(16)

        bkg = QGroupBox("Sauvegarde & Restauration")
        bkg_lay = QVBoxLayout(bkg); bkg_lay.setSpacing(12)

        db_info = QLabel(f"📁  Base de données: {os.path.join(BASE_DIR,'school.db')}")
        db_info.setStyleSheet("color:#94a3b8; font-size:12px; background:transparent;")
        bkg_lay.addWidget(db_info)

        btn_row = QHBoxLayout(); btn_row.setSpacing(12)
        backup_btn = QPushButton("💾  Créer une sauvegarde maintenant")
        backup_btn.setObjectName("primaryBtn"); backup_btn.setFixedHeight(40)
        backup_btn.clicked.connect(self._backup)
        restore_btn = QPushButton("📂  Restaurer une sauvegarde")
        restore_btn.setObjectName("secondaryBtn"); restore_btn.setFixedHeight(40)
        restore_btn.clicked.connect(self._restore)
        btn_row.addWidget(backup_btn); btn_row.addWidget(restore_btn); btn_row.addStretch()
        bkg_lay.addLayout(btn_row)

        log_lbl = QLabel("Historique des sauvegardes:")
        log_lbl.setStyleSheet("color:#94a3b8; font-size:12px; font-weight:600; background:transparent;")
        bkg_lay.addWidget(log_lbl)
        self._bk_log = QTextEdit(); self._bk_log.setReadOnly(True); self._bk_log.setMaximumHeight(200)
        bkg_lay.addWidget(self._bk_log)
        self._refresh_backup_log()

        bk_lay.addWidget(bkg); bk_lay.addStretch()
        tabs.addTab(bk_tab, "💾  Sauvegarde")

        # ── Users tab (admin only) ─────────────────────────────────────────────
        if self.current_user.role == 'Admin':
            usr_tab = QWidget(); usr_tab.setStyleSheet("background:transparent;")
            ul = QVBoxLayout(usr_tab); ul.setContentsMargins(20,20,20,20); ul.setSpacing(12)
            add_u = QPushButton("➕  Nouvel Utilisateur")
            add_u.setObjectName("primaryBtn"); add_u.setFixedWidth(200); add_u.setFixedHeight(40)
            add_u.clicked.connect(self._add_user)
            ul.addWidget(add_u)
            self._u_table = QTableWidget(); self._u_table.setColumnCount(5)
            self._u_table.setHorizontalHeaderLabels(["Utilisateur","Nom complet","Rôle","Statut","Dernière connexion"])
            self._u_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self._u_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self._u_table.verticalHeader().setVisible(False)
            self._u_table.setShowGrid(False)
            ul.addWidget(self._u_table)
            self._load_users()
            tabs.addTab(usr_tab, "👤  Utilisateurs")

    def _load(self):
        from models.database import Setting
        def g(k, d=""): s = self.session.query(Setting).filter_by(key=k).first(); return s.value if s else d
        self.s_name.setText(g('school_name','Le Schéma'))
        self.s_address.setText(g('school_address',''))
        self.s_phone.setText(g('school_phone',''))
        self.s_email.setText(g('school_email',''))
        idx = self.s_currency.findText(g('currency','MAD'))
        if idx >= 0: self.s_currency.setCurrentIndex(idx)
        self.s_transport.setValue(float(g('transport_fee','300')))
        self.s_insurance.setValue(float(g('insurance_fee','200')))

    def _save_school(self):
        from models.database import Setting
        def sv(k, v):
            s = self.session.query(Setting).filter_by(key=k).first()
            if s: s.value = v; s.updated_at = datetime.now()
            else: self.session.add(Setting(key=k, value=v))
        sv('school_name',self.s_name.text()); sv('school_address',self.s_address.text())
        sv('school_phone',self.s_phone.text()); sv('school_email',self.s_email.text())
        sv('currency',self.s_currency.currentText())
        sv('transport_fee',str(self.s_transport.value()))
        sv('insurance_fee',str(self.s_insurance.value()))
        self.session.commit()
        QMessageBox.information(self,"✅","Paramètres enregistrés!")

    def _backup(self):
        bdir = os.path.join(BASE_DIR,'backups'); os.makedirs(bdir,exist_ok=True)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest = os.path.join(bdir,f"school_backup_{ts}.db")
        try:
            shutil.copy2(os.path.join(BASE_DIR,'school.db'), dest)
            self._bk_log.append(f"✅ {datetime.now().strftime('%d/%m/%Y %H:%M')} — {os.path.basename(dest)}")
            QMessageBox.information(self,"✅",f"Sauvegarde créée:\n{dest}")
        except Exception as e:
            QMessageBox.warning(self,"Erreur",str(e))

    def _restore(self):
        bdir = os.path.join(BASE_DIR,'backups')
        fp, _ = QFileDialog.getOpenFileName(self,"Choisir sauvegarde",bdir,"Database (*.db)")
        if fp and QMessageBox.question(self,"Confirmer",
            "Remplacer la base de données actuelle?",
            QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            try:
                shutil.copy2(fp, os.path.join(BASE_DIR,'school.db'))
                self._bk_log.append(f"🔄 Restauration depuis: {os.path.basename(fp)}")
                QMessageBox.information(self,"✅","Restaurée. Redémarrez l'application.")
            except Exception as e:
                QMessageBox.warning(self,"Erreur",str(e))

    def _refresh_backup_log(self):
        bdir = os.path.join(BASE_DIR,'backups')
        if os.path.exists(bdir):
            for f in sorted(os.listdir(bdir), reverse=True)[:15]:
                if f.endswith('.db'):
                    sz = os.path.getsize(os.path.join(bdir,f))/1024
                    self._bk_log.append(f"📁 {f} ({sz:.0f} KB)")

    def _load_users(self):
        if not hasattr(self,'_u_table'): return
        from models.database import User
        self._u_table.setRowCount(0)
        for u in self.session.query(User).all():
            r = self._u_table.rowCount(); self._u_table.insertRow(r)
            for c, v in enumerate([u.username, u.full_name or "—", u.role,
                "✅ Actif" if u.is_active else "❌ Inactif",
                u.last_login.strftime("%d/%m/%Y %H:%M") if u.last_login else "—"]):
                item = QTableWidgetItem(v); item.setTextAlignment(Qt.AlignCenter)
                self._u_table.setItem(r, c, item)
            self._u_table.setRowHeight(r, 42)

    def _add_user(self):
        from hashlib import sha256
        from models.database import User
        dlg = QDialog(self); dlg.setWindowTitle("Nouvel Utilisateur"); dlg.setMinimumSize(400,320)
        root = QVBoxLayout(dlg); root.setContentsMargins(28,24,28,24); root.setSpacing(14)
        root.addWidget(QLabel("👤  Nouvel Utilisateur",
            styleSheet="color:#f8fafc; font-size:18px; font-weight:700; background:transparent;"))
        form = QFormLayout(); form.setSpacing(10); form.setLabelAlignment(Qt.AlignRight)
        def f(ph=""): fi = QLineEdit(); fi.setPlaceholderText(ph); fi.setFixedHeight(40); return fi
        uf = f("Identifiant"); nf = f("Nom complet")
        pf = f("Mot de passe"); pf.setEchoMode(QLineEdit.Password)
        rc = QComboBox(); rc.setFixedHeight(40); rc.addItems(["Admin","Comptable","Secrétaire"])
        for rl, w in [("Identifiant:",uf),("Nom complet:",nf),("Mot de passe:",pf),("Rôle:",rc)]:
            form.addRow(lbl(rl), w)
        root.addLayout(form)
        br = QHBoxLayout(); br.addStretch()
        cc = QPushButton("Annuler"); cc.setObjectName("secondaryBtn"); cc.clicked.connect(dlg.reject)
        sc = QPushButton("💾  Créer"); sc.setObjectName("primaryBtn")
        br.addWidget(cc); br.addWidget(sc); root.addLayout(br)
        def save():
            if not uf.text().strip() or not pf.text():
                QMessageBox.warning(dlg,"Erreur","Identifiant et mot de passe requis."); return
            if self.session.query(User).filter_by(username=uf.text().strip()).first():
                QMessageBox.warning(dlg,"Erreur","Identifiant déjà utilisé."); return
            self.session.add(User(username=uf.text().strip(),
                password=sha256(pf.text().encode()).hexdigest(),
                full_name=nf.text().strip(), role=rc.currentText()))
            self.session.commit(); dlg.accept(); self._load_users()
            QMessageBox.information(self,"✅","Utilisateur créé!")
        sc.clicked.connect(save); dlg.exec()
