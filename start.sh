#!/bin/bash
# 博客一键启动脚本

BLOG_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BLOG_DIR"

echo ""
echo "  ================================"
echo "   博客启动中..."
echo " ================================"
echo ""

# Check Hugo
if ! command -v hugo &> /dev/null; then
    echo "  未检测到 Hugo，正在安装..."
    if command -v brew &> /dev/null; then
        brew install hugo
    else
        echo "  请先安装 Hugo: https://gohugo.io/installation/"
        echo "  Mac 用户运行: brew install hugo"
        echo "  Linux 用户运行: sudo apt install hugo (或 snap install hugo)"
        exit 1
    fi
fi

echo "  Hugo 版本: $(hugo version | head -1)"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "  错误: 需要 Python3，请先安装"
    exit 1
fi

# Kill any existing servers on ports 1313 and 8082
lsof -ti:1313 | xargs kill -9 2>/dev/null
lsof -ti:8082 | xargs kill -9 2>/dev/null

echo ""
echo "  [1/2] 启动博客网站 (端口 1313)..."
nohup hugo server -p 1313 --bind 0.0.0.0 --navigateToChanged=false --disableFastRender > /tmp/hugo-server.log 2>&1 &
HUGO_PID=$!
echo "        PID: $HUGO_PID"

sleep 2

echo ""
echo "  [2/2] 启动管理面板 (端口 8082)..."
nohup python3 "$BLOG_DIR/admin-server.py" > /tmp/admin-server.log 2>&1 &
ADMIN_PID=$!
echo "        PID: $ADMIN_PID"

sleep 1

# Get local IP
LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || ipconfig getifaddr en0 2>/dev/null || echo "localhost")

echo ""
echo "  ================================"
echo "   启动完成！"
echo " ================================"
echo ""
echo "  本机访问:"
echo "    博客首页:  http://localhost:1313"
echo "    管理面板:  http://localhost:8082/admin"
echo ""
echo "  同 WiFi 下其他设备访问:"
echo "    博客首页:  http://$LOCAL_IP:1313"
echo "    管理面板:  http://$LOCAL_IP:8082/admin"
echo ""
echo "  按 Ctrl+C 停止所有服务"
echo ""

# Wait and handle Ctrl+C
trap "echo ''; echo '  正在停止服务...'; kill $HUGO_PID $ADMIN_PID 2>/dev/null; echo '  已停止'; exit 0" INT

# Keep script running
while true; do
    sleep 1
done
