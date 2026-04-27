@echo off
echo Starting all Trading Bot APIs and Tunnels with delays...

:: MarketDataAPI
echo Launching MarketDataAPI...
start "MarketDataAPI" /d "MarketDataAPI" cmd /c MarketDataAPI.bat
timeout /t 2 /nobreak > nul
    
:: NewsAPI
echo Launching NewsAPI...
start "NewsAPI" /d "NewsAPI" cmd /c NewsAPI.bat
timeout /t 2 /nobreak > nul


:: TradingBotAPI
echo Launching TradingBotAPI...
start "TradingBotAPI" /d "TradingBotAPI" cmd /c TradingBot.bat
timeout /t 2 /nobreak > nul

echo All services are starting in separate windows.
exit /b
