# 🎓 Le Schéma — School Management System

![Build Status](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/build.yml/badge.svg)

> **Innover · Créer · Exceller**

A professional, futuristic school management desktop application built with Python + PySide6.

---

## ⬇️ Download the EXE (no Python needed)

1. Click the **Actions** tab above
2. Click the latest successful **Build Windows EXE** run
3. Scroll down to **Artifacts** → download **LeSchema-SchoolManager-Windows**
4. Extract the ZIP → double-click `SchoolManager.exe`

**Or** go to the [Releases](../../releases) page to download a stable build.

---

## 🔑 Default Login

| Field    | Value      |
|----------|------------|
| Username | `admin`    |
| Password | `admin123` |

---

## ✨ Features

| Module | Description |
|--------|-------------|
| 📊 Dashboard | Live stats: students, revenue, expenses, profit |
| 🎓 Students | Full CRUD, photo, 15 classes (PS → 2BAC) |
| 💳 Payments | Monthly, insurance, transport — auto PDF receipt |
| 👥 Employees | Teachers, staff, drivers + salary tracking |
| 📉 Expenses | Fixed & variable expenses, analytics |
| 🚌 Transport | Bus & route management |
| 📅 Timetable | Weekly schedule per class |
| 📊 Reports | PDF reports + Excel export |
| ⚙ Settings | School info, fees, backup/restore, user management |

### Key capabilities
- 🧾 Automatic **PDF receipts** with QR code, school logo, numbered `REC-YYYY-000001`
- 📄 **PDF reports**: student list, financial, unpaid students, employees
- 📊 **Excel export** with formatted sheets
- 💾 **SQLite database** — works fully offline
- 🔒 **3 roles**: Admin, Comptable, Secrétaire
- 🌙 **Dark futuristic UI** with orange/gold Le Schéma branding

---

## 🛠️ Build It Yourself (GitHub Actions)

The EXE is built automatically by GitHub on every push. You never need to install anything locally.

1. Fork this repository
2. Go to **Actions** tab → enable workflows if prompted
3. Push any change (or click **Run workflow** manually)
4. Wait ~5 minutes → download the artifact

### Tech Stack
- **Python 3.11**
- **PySide6** — UI framework
- **SQLAlchemy + SQLite** — database
- **ReportLab** — PDF generation
- **qrcode + Pillow** — QR codes & image processing
- **openpyxl** — Excel export
- **PyInstaller** — packages everything into one `.exe`

---

## 📁 Project Structure

```
LeSchema_SchoolManager/
├── .github/workflows/build.yml   ← GitHub Actions (builds EXE automatically)
├── main.py                        ← Entry point
├── SchoolManager.spec             ← PyInstaller config
├── models/
│   └── database.py               ← SQLAlchemy models + DB init
├── services/
│   └── receipt_service.py        ← PDF receipt generator
├── themes/
│   └── dark_theme.py             ← Global stylesheet
├── ui/
│   ├── login_window.py
│   ├── main_window.py
│   ├── dashboard.py
│   ├── students.py
│   ├── payments.py
│   ├── employees.py
│   ├── expenses.py
│   ├── transport_timetable.py
│   ├── reports.py
│   └── settings.py
└── assets/
    ├── school_logo.png
    └── school_logo.ico
```

---

## 📜 License

© 2026 Le Schéma. All rights reserved.
