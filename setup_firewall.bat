@echo off
setlocal EnableDelayedExpansion

:: 1. Check for Administrator privileges and auto-elevate via UAC if needed
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [DEV CONSOLE] Requesting Administrator privileges to configure Windows Firewall...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd -ArgumentList '/c \"\"%~dpnx0\"\"' -Verb RunAs"
    exit /b
)

title Dev Console - Windows LAN and Firewall Setup
color 0A

echo ======================================================================
echo          DEV CONSOLE - Windows LAN and Firewall Setup
echo ======================================================================
echo.
echo [1/3] Setting Network Connection Profile to 'Private'...
echo       (Windows blocks mobile LAN connections if profile is 'Public')
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-NetConnectionProfile | Set-NetConnectionProfile -NetworkCategory Private"
if %errorlevel% equ 0 (
    echo       --> Network Category set to Private [OK]
) else (
    echo       --> Warning: Could not auto-switch network profile.
)

echo.
echo [2/3] Adding Inbound Firewall Rule for TCP Port 5000...
netsh advfirewall firewall delete rule name="DevConsole-Port5000" >nul 2>&1
netsh advfirewall firewall add rule name="DevConsole-Port5000" dir=in action=allow protocol=TCP localport=5000 profile=any
if %errorlevel% equ 0 (
    echo       --> TCP Port 5000 is ALLOWED for all network profiles [OK]
) else (
    echo       --> Error adding Port 5000 firewall rule.
)

echo.
echo [3/3] Adding Inbound Firewall Rule for Python.exe...
netsh advfirewall firewall delete rule name="DevConsole-Python" >nul 2>&1
netsh advfirewall firewall add rule name="DevConsole-Python" dir=in action=allow program="%LOCALAPPDATA%\Programs\Python\Python313\python.exe" profile=any >nul 2>&1
netsh advfirewall firewall add rule name="DevConsole-Python" dir=in action=allow program="python.exe" profile=any >nul 2>&1
echo       --> Python executable inbound access is ALLOWED [OK]

echo.
echo ======================================================================
echo                     LAN CONFIGURATION READY!
echo ======================================================================
echo.
echo  Your PC's IP address on the local network is:
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ip = (Get-NetIPAddress -InterfaceAlias 'Ethernet','Wi-Fi*','Wireless*' -AddressFamily IPv4 -ErrorAction SilentlyContinue | Where-Object { $_.IPAddress -notmatch '^(127\.|169\.254\.)' } | Select-Object -ExpandProperty IPAddress -First 1); Write-Host '   --> http://' $ip ':5000' -ForegroundColor Yellow; Write-Host '   (IMPORTANT: Type :5000 with THREE ZEROS, not :500!)' -ForegroundColor Cyan"
echo.
echo  Steps to connect your phone:
echo    1. Connect phone to the EXACT SAME Wi-Fi network as this PC.
echo    2. Open your mobile browser (Chrome/Safari) and go to:
echo       http://192.168.1.106:5000
echo    3. Or simply scan the QR code on the TV Screen!
echo.
echo ======================================================================
echo.
pause
