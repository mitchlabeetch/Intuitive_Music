# -*- mode: python ; coding: utf-8 -*-
# INTUITIVES DAW - macOS Standalone Build
# "Does this sound cool?" - The only rule.

import os
import platform
ARCH = platform.machine()

block_cipher = None

# Native engine binaries (if available)
BINARIES = []
if os.path.exists('engine/intuitives-engine'):
    BINARIES.extend([
        ('engine/intuitives-engine', 'engine'),
        ('engine/*.dylib', '.'),
        ('engine/rubberband', 'engine'),
        ('engine/intuitives-soundstretch', 'engine'),
        ('engine/sbsms', 'engine'),
    ])

a = Analysis(['intuitives.py'],
             pathex=[
                 os.path.dirname(SPECPATH),
             ],
             binaries=BINARIES,
             datas=[
                 ('meta.json', '.'),
                 ('files/', 'files'),
             ],
             hiddenimports=[
                 # Core Intuitives modules (new names)
                 'intlib',
                 'intlib.brand',
                 'intlib.constants',
                 'intlib.log',
                 'intlib.models',
                 'intlib.models.core',
                 'intlib.models.daw',
                 'intlib.lib',
                 'intui',
                 'intui.widgets',
                 'intui.daw',
                 'int_vendor',
                 'int_vendor.pymarshal',
                 'int_vendor.wavefile',
                 # Third party
                 'logging',
                 'numpy',
                 'PyQt6',
                 'PyQt6.QtCore',
                 'PyQt6.QtGui',
                 'PyQt6.QtWidgets',
                 'jinja2',
                 'mido',
                 'mutagen',
                 'psutil',
                 'yaml',
             ],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Intuitives',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Intuitives')

app = BUNDLE(coll,
             name='Intuitives.app',
             icon='macos/intuitives.icns',
             bundle_identifier='dev.intuitives.daw',
             info_plist={
                 'CFBundleDisplayName': 'Intuitives',
                 'CFBundleShortVersionString': '0.6.0',
                 'CFBundleVersion': '0.6.0-beta',
                 'NSHighResolutionCapable': True,
                 'NSMicrophoneUsageDescription': 'Intuitives DAW needs microphone access for audio recording.',
                 'LSApplicationCategoryType': 'public.app-category.music',
             })
