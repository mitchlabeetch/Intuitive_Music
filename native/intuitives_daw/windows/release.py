# Run this script from Windows, not MSYS2

from glob import iglob
import json
import os
import shutil
import subprocess
import sys

CWD = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        '..',
    ),
)
os.chdir(CWD)

with open("meta.json") as f:
    meta = json.load(f)
MAJOR_VERSION = meta['version']['major']
MINOR_VERSION = meta['version']['minor']

if os.path.isdir('dist/intuitives'):
    shutil.rmtree('dist/intuitives')

#print("Running Pyinstaller")
#subprocess.check_call(["pyinstaller", "pyinstaller-windows-onedir.spec"])

print("Running Nuitka")
subprocess.check_call([
    sys.executable,
    '-m', 'nuitka',
	'--standalone',
	'--windows-disable-console',
	'--include-module=sgui',
	'--include-module=sglib',
	'--include-qt-plugins=platform,sensible',
	'--enable-plugin=pyqt6',
	'scripts\\intuitives',
])

shutil.copy('meta.json', 'intuitives.dist')
shutil.copy('COMMIT', 'intuitives.dist')
shutil.copytree('files', 'intuitives.dist/files')
os.makedirs('intuitives.dist/engine')
for path in iglob('engine/*.dll'):
    shutil.copy2(path, 'intuitives.dist/engine')
for path in iglob('engine/*.exe'):
    shutil.copy2(path, 'intuitives.dist/engine')
os.makedirs('dist', exist_ok=True)
if os.path.exists('dist/intuitives'):
    shutil.rmtree('dist/intuitives')
shutil.move('intuitives.dist', 'dist/intuitives')

TEMPLATE = r"""
!define PRODUCT_NAME "intuitives"
!define PRODUCT_VERSION "{MAJOR_VERSION_NUM}.0"
!define PRODUCT_PUBLISHER "intuitivesdaw"

;Require admin rights on NT6+ (When UAC is turned on)
RequestExecutionLevel admin

SetCompressor /SOLID lzma

Name "Intuitives DAW {MINOR_VERSION}"
OutFile "dist\IntuitivesDAW-{MINOR_VERSION}-win64-installer.exe"
InstallDir "$PROGRAMFILES64\intuitivesdaw@github\Intuitives"

;--------------------------------
;Interface Settings
  !define MUI_ABORTWARNING
  !define MUI_LICENSEPAGE_CHECKBOX
  !define MUI_FINISHPAGE_RUN "$INSTDIR\program\{MAJOR_VERSION}.exe"
  !define MUI_STARTMENUPAGE_DEFAULTFOLDER "Intuitives DAW"

!include MUI2.nsh
!include WinVer.nsh
!include x64.nsh

;--------------------------------
;Modern UI Configuration
;Installer pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "windows\gpl-3.0.txt"

!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY

!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

;Uninstaller pages
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
;!insertmacro MUI_UNPAGE_LICENSE textfile
;!insertmacro MUI_UNPAGE_COMPONENTS
!insertmacro MUI_UNPAGE_DIRECTORY
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

;--------------------------------
;Languages
  !insertmacro MUI_LANGUAGE "English"

Function .onInit
  ${{IfNot}} ${{AtLeastWin10}}
    MessageBox MB_OK "Windows 10 or later required, 64 bit only"
    Quit
  ${{EndIf}}
  ${{IfNot}} ${{RunningX64}}
    MessageBox MB_OK "64 bit Windows 10 or later required, 32 bit is not supported"
    Quit
  ${{EndIf}}
FunctionEnd

;Section
;    UserInfo::getAccountType
;    Pop $0
;
;    # compare the result with the string "Admin" to see if the user is admin.
;    # If match, jump 3 lines down.
;    StrCmp $0 "Admin" +3
;
;    # if there is not a match, print message and return
;    MessageBox MB_OK "not admin: $0"
;    Return
;SectionEnd

Section "Base Install" SEC01
    SectionIn RO
    SetOutPath $INSTDIR
    writeUninstaller "$INSTDIR\uninstall.exe"

    ; Clean up the old legacy file structure
    ; TODO: Remove this in mid 2023
    RMDir /r "$PROGRAMFILES64\intuitivesaudio@github\Intuitives\program"
    Delete "$PROGRAMFILES64\intuitivesaudio@github\Intuitives\uninstall.exe"
    ; Only if empty
    RMDir "$PROGRAMFILES64\intuitivesaudio@github\Intuitives"
    RMDir "$PROGRAMFILES64\intuitivesaudio@github"

    ; Delete the old program
    RMDir /r $INSTDIR\program
    ; Install the program
    CreateDirectory $INSTDIR\program
    SetOutPath $INSTDIR\program
    File /r "dist\intuitives\"
    File "files\share\pixmaps\{MAJOR_VERSION}.ico"
    ; Add to the "Add or remove programs" dialog
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\IntuitivesDAW" \
                "DisplayName" "Intuitives DAW"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\IntuitivesDAW" \
                "DisplayIcon" "$\"$INSTDIR\program\files\share\pixmaps\intuitives.ico$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\IntuitivesDAW" \
                "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
SectionEnd

Section "Start Menu Shortcut" SEC02
    createShortCut \
      "$SMPROGRAMS\Intuitives DAW.lnk" \
      "$INSTDIR\program\{MAJOR_VERSION}.exe" \
      "" \
      "$INSTDIR\program\{MAJOR_VERSION}.ico"
SectionEnd

Section /o "Portable Flash Drive Install" SEC03
    SetOutPath $INSTDIR
    ; Create the shortcut to the executable
    File windows\LaunchIntuitives.cmd
    SetOutPath $INSTDIR\program
    ; The exe looks for this empty file to choose the Intuitives home folder
    FileOpen $9 ..\_intuitives_home w
    FileWrite $9 "This file tells Intuitives it is a portable install."
    FileClose $9
SectionEnd

LangString DESC_SEC03 ${{LANG_ENGLISH}} "Store settings and projects in the same folder as the executable.  Only use this if you are installing to a flash drive, and you must change the install folder to the flash drive in the next step."

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
!insertmacro MUI_DESCRIPTION_TEXT ${{SEC03}} $(DESC_SEC03)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

Section "uninstall"
    ; We do not delete settings, projects or any other files the user may have
    ; stored next to the application, only the application itself
    RMDir /r $INSTDIR\program
    Delete "$SMPROGRAMS\Intuitives DAW.lnk"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\IntuitivesDAW"
SectionEnd
"""

NSIS = r"C:\Program Files (x86)\NSIS\Bin\makensis.exe"

template = TEMPLATE.format(
	MINOR_VERSION=MINOR_VERSION,
	MAJOR_VERSION=MAJOR_VERSION,
	MAJOR_VERSION_NUM=MAJOR_VERSION[-1],
)
template_name = "{0}.nsi".format(MAJOR_VERSION)
with open(template_name, "w") as f:
	f.write(template)
print("Running NSIS")
subprocess.check_call([NSIS, template_name])

