@echo off
echo Starting all Trading Bot APIs and Tunnels with delays...

:: MarketDataAPI
echo Launching MarketDataAPI...
start "MarketDataAPI" /d "MarketDataAPI" cmd /c MarketDataAPI.bat
timeout /t 2 /nobreak > nul

echo Launching MarketData Tunnel...
start "MarketData Tunnel" /d "MarketDataAPI\Tunnel-8080" cmd /c start_tunneling.bat
timeout /t 2 /nobreak > nul
    
:: NewsAPI
echo Launching NewsAPI...
start "NewsAPI" /d "NewsAPI" cmd /c NewsAPI.bat
timeout /t 2 /nobreak > nul

echo Launching News Tunnel...
start "News Tunnel" /d "NewsAPI\Tunnel-8081" cmd /c start_tunneling.bat
timeout /t 2 /nobreak > nul

:: TradingBotAPI
echo Launching TradingBotAPI...
start "TradingBotAPI" /d "TradingBotAPI" cmd /c TradingBot.bat
timeout /t 2 /nobreak > nul

echo Launching TradingBot Tunnel...
start "TradingBot Tunnel" /d "TradingBotAPI\Tunnel-8082" cmd /c start_tunneling.bat

echo All services are starting in separate windows.
exit /b
