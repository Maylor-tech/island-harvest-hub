@echo off
echo Setting up Island Harvest Hub Database Management Tasks...

REM Create daily backup task (runs at 2 AM daily)
schtasks /create /tn "IslandHarvest_DailyBackup" /tr "C:\Users\18023\island-harvest-enterprise\manage_database.bat" /sc daily /st 02:00 /f

REM Create weekly optimization task (runs at 3 AM every Sunday)
schtasks /create /tn "IslandHarvest_WeeklyOptimize" /tr "C:\Users\18023\island-harvest-enterprise\manage_database.bat" /sc weekly /d SUN /st 03:00 /f

REM Create monthly report task (runs at 4 AM on the 1st of each month)
schtasks /create /tn "IslandHarvest_MonthlyReport" /tr "C:\Users\18023\island-harvest-enterprise\manage_database.bat" /sc monthly /d 1 /st 04:00 /f

echo Database management tasks have been scheduled:
echo - Daily backup at 2:00 AM
echo - Weekly optimization at 3:00 AM every Sunday
echo - Monthly report at 4:00 AM on the 1st of each month
echo.
echo To view scheduled tasks, open Task Scheduler and look for tasks starting with "IslandHarvest_"
pause 