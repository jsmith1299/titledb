@echo off
setlocal

cd /d D:\nsw_updates

echo ======================================== >> update.log
echo [%date% %time%] Starting daily update >> update.log

REM Run Python script
"C:\Users\Nick\AppData\Local\Microsoft\WindowsApps\python.exe" update.py >> update.log 2>&1

if errorlevel 1 (
    echo [%date% %time%] ERROR: update.py failed >> update.log
    exit /b 1
)

echo [%date% %time%] update.py completed successfully >> update.log

REM Stage all changes
git add . >> update.log 2>&1

REM Check whether anything changed
git diff --cached --quiet

if errorlevel 1 (
    echo [%date% %time%] Changes detected. Creating commit... >> update.log

    git commit -m "Daily update" >> update.log 2>&1

    if errorlevel 1 (
        echo [%date% %time%] ERROR: Git commit failed >> update.log
        exit /b 1
    )

    git push origin main >> update.log 2>&1

    if errorlevel 1 (
        echo [%date% %time%] ERROR: GitHub push failed >> update.log
        exit /b 1
    )

    echo [%date% %time%] Successfully pushed changes to GitHub >> update.log
) else (
    echo [%date% %time%] No changes detected. Nothing to push. >> update.log
)

echo [%date% %time%] Daily update finished >> update.log
echo. >> update.log

endlocal