@echo off
REM PDF Translator - Build Windows Executable
REM This script builds a standalone Windows executable using PyInstaller

echo ========================================
echo PDF Translator - Build Executable
echo ========================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller!
        pause
        exit /b 1
    )
)

echo.
echo Building executable...
echo.

REM Build with PyInstaller
REM Option 1: Use spec file (recommended for customization)
pyinstaller PDFTranslator.spec

REM Option 2: Use command line (uncomment to use)
REM pyinstaller --name="PDFTranslator" ^
REM     --windowed ^
REM     --onefile ^
REM     --hidden-import=PySide6.QtCore ^
REM     --hidden-import=PySide6.QtGui ^
REM     --hidden-import=PySide6.QtWidgets ^
REM     --hidden-import=pdf_translator ^
REM     --hidden-import=deep_translator ^
REM     --hidden-import=langdetect ^
REM     --hidden-import=fitz ^
REM     --collect-all=PySide6 ^
REM     --noconfirm ^
REM     main.py

if errorlevel 1 (
    echo.
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Executable location: dist\PDFTranslator.exe
echo.
echo You can now distribute PDFTranslator.exe
echo.
pause

