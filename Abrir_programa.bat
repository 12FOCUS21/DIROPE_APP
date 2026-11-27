@echo off
setlocal
cd /d "%~dp0"
if not exist "iniciar.py" goto :carpeta_incompleta
if not exist "preparar.py" goto :carpeta_incompleta
if not exist "src\dirope\interfaz\ventana.py" goto :carpeta_incompleta
where py >nul 2>nul
if not errorlevel 1 (
    py -3 -c "import sys, tkinter; sys.exit(sys.version_info < (3, 10))" >nul 2>nul
    if not errorlevel 1 goto :usar_py
)
where python >nul 2>nul
if not errorlevel 1 (
    python -c "import sys, tkinter; sys.exit(sys.version_info < (3, 10))" >nul 2>nul
    if not errorlevel 1 goto :usar_python
)
echo No se encontro Python 3.10 o superior con Tcl/Tk. Instala Python desde python.org con Tcl/Tk habilitado.
pause
exit /b 1

:carpeta_incompleta
echo Faltan archivos. Extrae todo el ZIP antes de abrir Abrir_programa.bat.
pause
exit /b 1

:usar_py
py -3 preparar.py %*
goto :fin

:usar_python
python preparar.py %*

:fin
set "ESTADO=%ERRORLEVEL%"
if not "%ESTADO%"=="0" pause
exit /b %ESTADO%
