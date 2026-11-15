@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    py -3 -m venv .venv
    if errorlevel 1 (
        python -m venv .venv
        if errorlevel 1 (
            echo No se pudo crear el entorno. Instala Python 3 y vuelve a intentar.
            pause
            exit /b 1
        )
    )
)
".venv\Scripts\python.exe" interfaz.py
if errorlevel 1 pause
