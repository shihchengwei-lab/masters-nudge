@echo off
set "PYTHONIOENCODING=utf-8"
where py >nul 2>nul
if %errorlevel% equ 0 py -3 -c "import sys; raise SystemExit(not (sys.version_info.major == 3 and sys.version_info.minor in range(10, 100)))" >nul 2>nul
if %errorlevel% equ 0 goto use_py
where python >nul 2>nul
if %errorlevel% equ 0 python -c "import sys; raise SystemExit(not (sys.version_info.major == 3 and sys.version_info.minor in range(10, 100)))" >nul 2>nul
if %errorlevel% equ 0 goto use_python
where python3 >nul 2>nul
if %errorlevel% equ 0 python3 -c "import sys; raise SystemExit(not (sys.version_info.major == 3 and sys.version_info.minor in range(10, 100)))" >nul 2>nul
if %errorlevel% equ 0 goto use_python3
echo masters-nudge: Python 3.10+ not found 1>&2
exit /b 0

:use_py
py -3 %*
exit /b 0

:use_python
python %*
exit /b 0

:use_python3
python3 %*
exit /b 0
