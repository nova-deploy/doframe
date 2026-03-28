@echo off
setlocal enabledelayedexpansion

set APP_NAME=Doframe
set MAIN_FILE=main.py
set ICON_FILE=logo.ico
set OUT_DIR=dist

@REM Fais avec de l'ia...

echo.
echo  ============================
echo   Compilation PyInstaller - DOFRAME
echo  ============================
echo.

if exist "%OUT_DIR%" (
    echo [*] Nettoyage du dossier dist...
    rmdir /s /q "%OUT_DIR%"
)
if exist "build" (
    rmdir /s /q "build"
)
if exist "%APP_NAME%.spec" (
    del "%APP_NAME%.spec"
)

echo [*] Lancement de PyInstaller...
python -m PyInstaller ^
    --onefile ^
    --noconsole ^
    --uac-admin ^
    --icon="%ICON_FILE%" ^
    --name="%APP_NAME%" ^
    --distpath="%OUT_DIR%" ^
    --add-data="skin;skin" ^
    --add-data="sounds;sounds" ^
    --add-data="logo.ico;." ^
    --hidden-import=customtkinter ^
    --hidden-import=PIL ^
    --hidden-import=pygame ^
    --hidden-import=win32api ^
    --hidden-import=win32con ^
    --hidden-import=win32gui ^
    --hidden-import=win32process ^
    --hidden-import=keyboard ^
    --collect-all=customtkinter ^
    "%MAIN_FILE%"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERREUR]
    pause
    exit /b 1
)

echo.
echo [OK] Executable : %OUT_DIR%\%APP_NAME%.exe
echo.
pause
