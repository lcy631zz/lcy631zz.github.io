@echo off
REM 一条脚本同时启动博客预览(1313)和管理面板(8082)
REM 双击本文件即可，会各开一个最小化窗口；关掉那两个窗口服务才停。
REM 注意：本脚本由你本机直接运行，服务器才会在你真机上，
REM       这样你自己的浏览器才能打开 http://localhost:8082/admin

cd /d D:\blog\lcy631zz.github.io-master\lcy631zz.github.io-master

REM 预检：确认依赖文件存在，找不到就报错并暂停，方便排查
if not exist "C:\hugo\hugo.exe" (
    echo [错误] 找不到 C:\hugo\hugo.exe
    echo 请确认 Hugo 已安装在该路径，或修改本脚本中的路径。
    pause
    exit /b 1
)
if not exist "C:\Users\Eintv631\.workbuddy\binaries\python\versions\3.13.12\python.exe" (
    echo [错误] 找不到 Python: C:\Users\Eintv631\.workbuddy\binaries\python\versions\3.13.12\python.exe
    pause
    exit /b 1
)
if not exist "D:\blog\lcy631zz.github.io-master\lcy631zz.github.io-master\admin-server.py" (
    echo [错误] 找不到 admin-server.py，请确认在正确目录下双击本脚本。
    pause
    exit /b 1
)

start "Hugo-Preview" /min "C:\hugo\hugo.exe" server -p 1313 --bind 0.0.0.0 --navigateToChanged=false --disableFastRender
start "Blog-Admin" /min "C:\Users\Eintv631\.workbuddy\binaries\python\versions\3.13.12\python.exe" admin-server.py

echo 已尝试启动，请在浏览器打开（约 5 秒后）：
echo   管理面板  http://localhost:8082/admin
echo   预览首页  http://localhost:1313/
echo.
echo 若浏览器仍打不开，请检查：
echo   1) 任务栏是否出现两个最小化命令行窗口（标题 Hugo-Preview / Blog-Admin）
echo   2) 防火墙是否拦截了 8082 / 1313 端口
echo   3) 两个端口是否已被其他程序占用
timeout /t 5 >nul
