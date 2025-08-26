@echo off
setlocal ENABLEDELAYEDEXPANSION
REM Victoria launcher (Windows) — double-click friendly

REM Move to the script directory
pushd "%~dp0"

REM Ensure UTF-8 for emoji/ANSI
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

REM Prefer the Python launcher (py), then fall back to python
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 "%~dp0victoria.py"
  set "ERR=%ERRORLEVEL%"
) else (
  where python >nul 2>nul
  if %errorlevel%==0 (
    python "%~dp0victoria.py"
    set "ERR=%ERRORLEVEL%"
  ) else (
    echo.
    echo [!] Python not found. Please install Python 3 from https://www.python.org/downloads/
    echo     Or install the Microsoft Store "Python 3.x" app.
    set "ERR=9009"
    goto :epilogue
  )
)

:epilogue
popd

if not "%ERR%"=="0" (
  echo.
  echo [!] Victoria exited with code %ERR%.
  echo     Press any key to close this window...
  pause >nul
)

exit /b %ERR%
