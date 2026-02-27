@echo off
echo Configuring ngrok...

ngrok config add-authtoken 2cXvMAWlHhcpYnMXfpSEXQp052M_4rH5gnyiyq9kPr5F5Wcfx

echo Starting ngrok tunnel...
ngrok http --domain=evolving-ghastly-rabbit.ngrok-free.app 8080

pause
