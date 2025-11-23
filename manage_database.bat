@echo off
cd C:\Users\18023\island-harvest-enterprise
call venv\Scripts\activate

REM Check if task type is provided
if "%1"=="" (
    echo Running daily maintenance...
    python island_harvest_hub/db_manager.py daily
) else (
    echo Running %1 maintenance...
    python island_harvest_hub/db_manager.py %1
)

echo.
echo Database maintenance completed. Check db_manager.log for details.
pause 