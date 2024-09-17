# run_docker.spec
# -*- mode: python ; coding: utf-8 -*-

template_dirs = [
    (r'D:\Users\User\Desktop\krystartust web\src\bank\templates', 'templates/bank'),
    (r'D:\Users\User\Desktop\krystartust web\src\client\templates', 'templates/client'),
    (r'D:\Users\User\Desktop\krystartust web\src\income\templates', 'templates/income'),
    (r'D:\Users\User\Desktop\krystartust web\src\loan\templates', 'templates/loan'),
    (r'D:\Users\User\Desktop\krystartust web\src\main\templates', 'templates/main'),
    (r'D:\Users\User\Desktop\krystartust web\src\reports\templates', 'templates/reports'),
    (r'D:\Users\User\Desktop\krystartust web\src\savings\templates', 'templates/savings'),
]

# Include the Docker management scripts
docker_scripts = [
    (r'D:\Users\User\Desktop\krystartust web\src\docker_manager.bat', '.'),
]

# Combine all data directories
datas = template_dirs + docker_scripts

a = Analysis(
    ['run_docker.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'platform', 
        'subprocess', 
        'os', 
        'django', 
        'django.core.management', 
        'django.db.backends.postgresql',
        'django.contrib.contenttypes.context_processors',
        'django.contrib.staticfiles.context_processors',
        'django.contrib.sessions.context_processors',
        'django.contrib.messages.context_processors',
        'django.contrib.auth.context_processors',
        'django.contrib.admin.context_processors',
        'django.contrib.contenttypes.templatetags',
        'django.contrib.sessions.templatetags',
        'django.contrib.messages.templatetags',
        'django.contrib.staticfiles.templatetags',
        'django.contrib.auth.templatetags',
        'django.contrib.admin.templatetags',
        'savings.context_processors',
        'income.templatetags',
        'reports.templatetags',
        'user.templatetags',
        'loan.context_processors',
        'client.templatetags',
        'expenses.templatetags',
        'main.templatetags',
        'income.context_processors',
        'bank.context_processors',
        'main.context_processors',
        'bank.templatetags',
        'reports.context_processors',
        'savings.templatetags',
        'mx.DateTime'
    ],
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
    name='run_docker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)