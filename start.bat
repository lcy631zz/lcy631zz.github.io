@echo off
chcp 65001 >nul
title 博客管理面板

echo.
echo   ================================
echo     博客启动中...
echo   ================================
echo.

set "BLOG_DIR=%~dp0"
cd /d "%BLOG_DIR%"

:: Check Hugo
hugo version >nul 2>&1
if errorlevel 1 (
    echo   [错误] 未检测到 Hugo，请先安装 Hugo
    echo   下载地址: https://gohugo.io/installation/
    echo   Windows 推荐使用: scoop install hugo-extended
    echo   或下载安装包: https://github.com/gohugoio/hugo/releases
    pause
    exit /b 1
)

echo   [1/2] 启动博客网站 (端口 1313)...
start "博客网站" hugo server -p 1313 --bind 0.0.0.0 --navigateToChanged=false --disableFastRender

timeout /t 3 /nobreak >nul

echo   [2/2] 启动管理面板 (端口 8082)...
start "管理面板" python3 admin-server.py

timeout /t 2 /nobreak >nul

echo.
echo   ================================
echo     启动完成！
echo   ================================
echo.
echo   本机访问:
echo     博客首页:  http://localhost:1313
echo     管理面板:  http://localhost:8082/admin
echo.
echo   同 WiFi 下其他设备访问:
echo     博客首页:  http://你的IP:1313
echo     管理面板:  http://你的IP:8082/admin
echo.
echo   关闭此窗口即可停止所有服务
echo.

:: Get local IP
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set IP=%%a
    goto :gotip
)
:gotip
set IP=%IP: =%
echo   你的 IP 地址: %IP%
echo.

pause
