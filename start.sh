#!/bin/bash

# 竞品监测平台启动脚本

echo "================================"
echo "  竞品监测平台启动脚本"
echo "================================"
echo ""

# 设置工作目录
WORK_DIR="/Users/xiaoxiao.liu/竞品监测平台"
cd "$WORK_DIR" || exit 1

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行 python3 -m venv venv"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查数据库
if [ ! -f "data/competitors.db" ]; then
    echo "⚠️  数据库不存在，正在初始化..."
    python init_db.py
    echo ""
fi

# 检查API Key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  警告: 未设置 ANTHROPIC_API_KEY 环境变量"
    echo "   数据采集功能将无法使用"
    echo "   请运行: export ANTHROPIC_API_KEY='your-key-here'"
    echo ""
fi

# 询问启动模式
echo "请选择启动模式:"
echo "1) 前台运行（开发模式，按Ctrl+C停止）"
echo "2) 后台运行（生产模式）"
echo ""
read -p "请选择 [1/2]: " mode

if [ "$mode" = "2" ]; then
    # 后台运行
    echo ""
    echo "正在后台启动服务..."
    nohup python app.py > logs/app.log 2>&1 &
    PID=$!
    echo "✓ 服务已启动 (PID: $PID)"
    echo "✓ 访问地址: http://localhost:5000"
    echo "✓ 日志文件: logs/app.log"
    echo ""
    echo "停止服务: pkill -f app.py"
    echo "查看日志: tail -f logs/app.log"
else
    # 前台运行
    echo ""
    echo "正在启动服务..."
    echo "按 Ctrl+C 停止服务"
    echo ""
    python app.py
fi
