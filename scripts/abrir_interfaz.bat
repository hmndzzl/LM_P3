@echo off
setlocal
cd /d "%~dp0.."
where py >nul 2>nul
if %errorlevel% equ 0 (
    py -3 -B -m lm_p3 %*
) else (
    python -B -m lm_p3 %*
)
if errorlevel 1 pause
