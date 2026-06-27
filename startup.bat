@echo off
cd /d C:\Agent\first-cc
start "X402-Server" /MIN C:\Progra~1\Python312\python.exe server.py
timeout /t 5 /nobreak >nul
start "X402-Tunnel" /MIN ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -R 80:localhost:8000 serveo.net
timeout /t 10 /nobreak >nul
C:\Progra~1\Python312\python.exe tunnel_daemon.py
