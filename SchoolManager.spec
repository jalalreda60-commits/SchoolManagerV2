# -*- mode: python ; coding: utf-8 -*-
import os
block_cipher = None
BASE = os.path.abspath('.')

a = Analysis(
    ['main.py'],
    pathex=[BASE],
    binaries=[],
    datas=[
        (os.path.join(BASE,'assets'),       'assets'),
        (os.path.join(BASE,'themes'),       'themes'),
        (os.path.join(BASE,'models'),       'models'),
        (os.path.join(BASE,'services'),     'services'),
        (os.path.join(BASE,'ui'),           'ui'),
        (os.path.join(BASE,'controllers'),  'controllers'),
    ],
    hiddenimports=[
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.dialects.sqlite.pysqlite',
        'sqlalchemy.orm','sqlalchemy.ext.declarative','sqlalchemy.pool',
        'reportlab','reportlab.platypus','reportlab.lib',
        'reportlab.lib.pagesizes','reportlab.lib.colors',
        'reportlab.lib.styles','reportlab.lib.units','reportlab.lib.enums',
        'qrcode','qrcode.image.pil',
        'PIL','PIL.Image','PIL.ImageDraw','PIL.ImageFont',
        'openpyxl','openpyxl.styles',
        'matplotlib','matplotlib.backends.backend_qtagg',
        'matplotlib.backends.backend_agg',
        'matplotlib.figure','matplotlib.pyplot',
        'PySide6','PySide6.QtCore','PySide6.QtWidgets','PySide6.QtGui',
        'models','models.database',
        'services','services.receipt_service',
        'themes','themes.dark_theme',
        'ui','ui.login_window','ui.dashboard','ui.students',
        'ui.payments','ui.employees','ui.expenses',
        'ui.transport_timetable','ui.reports','ui.settings',
        'ui.main_window','ui.widgets',
        'controllers',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter','scipy','pandas','numpy.distutils'],
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
    name='SchoolManager',
    debug=False, bootloader_ignore_signals=False,
    strip=False, upx=True, upx_exclude=[],
    runtime_tmpdir=None, console=False,
    disable_windowed_traceback=False,
    argv_emulation=False, target_arch=None,
    codesign_identity=None, entitlements_file=None,
    icon=os.path.join(BASE,'assets','school_logo.ico'),
)
