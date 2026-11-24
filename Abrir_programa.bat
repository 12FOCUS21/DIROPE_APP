@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if not errorlevel 1 (
    python iniciar.py
    if errorlevel 1 pause
    exit /b
)
where py >nul 2>nul
if not errorlevel 1 (
    py -3 iniciar.py
    if errorlevel 1 pause
    exit /b
)
echo No se encontro Python. Instala Python 3.10 o superior con Tcl/Tk y agregalo al PATH.
pause
