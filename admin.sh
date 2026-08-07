#!/bin/bash
# 一键启动博客管理面板
# 双击运行或在终端执行: ./admin.sh

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

echo "正在启动博客管理面板..."
echo ""

# 后台启动服务器
$PYTHON admin-server.py &
SERVER_PID=$!

sleep 2

# 尝试打开浏览器
URL="http://localhost:8082/admin"
if command -v xdg-open &> /dev/null; then
    xdg-open "$URL" 2>/dev/null
elif command -v python3 &> /dev/null; then
    python3 -c "import webbrowser; webbrowser.open('$URL')" 2>/dev/null
fi

echo "  管理面板: $URL"
echo ""
echo "  按 Ctrl+C 停止服务"
echo ""

# 等待用户中断
wait $SERVER_PID 2>/dev/null

echo ""
echo "  已停止。"
