@echo off
echo Configuring ngrok...

ngrok config add-authtoken 2h6aKzep9W47cLy28Z2hLH4ebGy_4CjqBdr5hqotYUoxgDea5

echo Starting ngrok tunnel...
ngrok http --domain=mouse-funky-tahr.ngrok-free.app 8081

pause
