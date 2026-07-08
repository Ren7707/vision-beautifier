# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

drop = (
    'opencv_videoio_ffmpeg',
    'pyside6\\opengl32sw.dll',
    'pyside6\\qt6network.dll',
    'pyside6\\qt6opengl.dll',
    'pyside6\\qt6pdf.dll',
    'pyside6\\qt6qml',
    'pyside6\\qt6quick',
    'pyside6\\qt6virtualkeyboard.dll',
    'pyside6\\qtnetwork.pyd',
    'pyside6\\plugins\\generic\\',
    'pyside6\\plugins\\imageformats\\',
    'pyside6\\plugins\\networkinformation\\',
    'pyside6\\plugins\\platforminputcontexts\\',
    'pyside6\\plugins\\platforms\\qdirect2d.dll',
    'pyside6\\plugins\\platforms\\qminimal.dll',
    'pyside6\\plugins\\platforms\\qoffscreen.dll',
    'pyside6\\plugins\\styles\\',
    'pyside6\\plugins\\tls\\',
    'pyside6\\translations\\',
)


def keep(item):
    name = item[0].lower()
    return not any(part in name for part in drop)


a.binaries = TOC([item for item in a.binaries if keep(item)])
a.datas = TOC([item for item in a.datas if keep(item)])
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='VisionBeautifier',
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
)
