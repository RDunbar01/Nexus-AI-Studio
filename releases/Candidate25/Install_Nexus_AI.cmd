@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  python "%~dp0Install_Nexus_AI.py" %*
) else (
  py -3 "%~dp0Install_Nexus_AI.py" %*
)
if errorlevel 2 pause
