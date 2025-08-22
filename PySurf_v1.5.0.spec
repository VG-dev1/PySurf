# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['PySurf_v1.5.0.py'],
    pathex=[],
    binaries=[],
    datas=[('Icons', 'Icons')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PySurf_v1.5.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\vitoh\\PySurf_Dev\\PySurf_v1.4.1\\Icons\\PySurf_Icon.ico'],
)
