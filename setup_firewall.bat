@echo off
echo ===================================================
echo   DEV CONSOLE - Windows Defender Firewall Setup
echo ===================================================
echo.
echo Opening inbound TCP Port 5000 for Mobile LAN access...
echo.

netsh advfirewall firewall delete rule name="DevConsole-Port5000" >nul 2>&1
netsh advfirewall firewall add rule name="DevConsole-Port5000" dir=in action=allow protocol=TCP localport=5000 profile=any

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Port 5000 is now open!
    echo Phones on your local Wi-Fi can now connect to http://%COMPUTERNAME%:5000
) else (
    echo.
    echo [ERROR] Failed to add firewall rule.
    echo Please make sure you RIGHT-CLICK this file and select "RUN AS ADMINISTRATOR".
)

echo.
pause
