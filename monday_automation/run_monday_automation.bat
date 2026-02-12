@echo off
REM Monday Automation - Address Issues to Excel
REM Schedule this with Windows Task Scheduler for every Monday

echo ========================================
echo Monday Automation: Address Issues
echo ========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Activate the project venv and run
call ..\.venv\Scripts\activate.bat
python address_issues_to_excel.py

echo.
echo Done! Check the output folder for results.
pause
