#!/bin/bash
# 一键启动博客管理面板
# 使用方法：在 WSL 终端中执行 ./admin.sh

cd "$(dirname "$0")"

# 检查 Python3 是否可用
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "错误：需要安装 Python3"
    echo "请访问 https://www.python.org/downloads/ 下载安装"
    read -p "按回车键退出..."
    exit 1
fi

# 检查端口是否已被占用
PORT=8082
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "管理面板已在运行: http://localhost:$PORT/admin"
    echo "如需重启，请先执行: fuser -k $PORT/tcp"
    echo ""
    echo "  按 Ctrl+C 退出"
    wait
    exit 0
fi

echo "正在启动博客管理面板..."
echo ""

# 后台启动服务器
$PYTHON admin-server.py &
SERVER_PID=$!

sleep 2

# 尝试打开浏览器
URL="http://localhost:$PORT/admin"
if command -v xdg-open &> /dev/null; then
    xdg-open "$URL" 2>/dev/null
elif command -v python3 &> /dev/null; then
    python3 -c "import webbrowser; webbrowser.open('$URL')" 2>/dev/null
fi

echo "  管理面板: $URL"
echo ""
LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
if [ -n "$LOCAL_IP" ]; then
    echo "  手机访问: http://$LOCAL_IP:$PORT/admin （需同一 WiFi）"
    echo ""
fi
echo "  提示：如果手机无法访问，可能需要在 Windows 中转发端口"
echo "  Windows CMD 执行: netsh interface portproxy add v4tov4 listenport=$PORT listenaddress=0.0.0.0 connectport=$PORT connectaddress=127.0.0.1"
echo ""
echo "  按 Ctrl+C 停止服务"
echo ""

# 等待用户中断
wait $SERVER_PID 2>/dev/null

echo ""
echo "  已停止。"
