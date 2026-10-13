@echo off
REM 一条脚本同时启动博客预览(1313)和管理面板(8082)
REM 双击本文件即可，会各开一个最小化窗口；关掉那两个窗口服务才停。
cd /d D:\blog\lcy631zz.github.io-master\lcy631zz.github.io-master
start "Hugo-Preview" /min "C:\hugo\hugo.exe" server -p 1313 --bind 0.0.0.0 --navigateToChanged=false --disableFastRender
start "Blog-Admin" /min "C:\Users\Eintv631\.workbuddy\binaries\python\versions\3.13.12\python.exe" admin-server.py
echo 已启动，请在浏览器打开：
echo   管理面板  http://localhost:8082/admin
echo   预览首页  http://localhost:1313/
timeout /t 3 >nul
