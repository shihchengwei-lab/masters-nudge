@echo off
REM Launch the Masters' Nudge floating window without a console.
REM Requires Python 3 with tkinter (default in standard CPython on Windows).
start "" pythonw "%~dp0buddy_window.py"
