#!/bin/bash

echo "================================"
echo "  配置Claude API Key"
echo "================================"
echo ""

read -p "请输入你的Claude API Key (sk-ant-...): " api_key

if [ -z "$api_key" ]; then
    echo "❌ 未输入API Key"
    exit 1
fi

# 设置环境变量
export ANTHROPIC_API_KEY="$api_key"

# 添加到shell配置文件
if [ -f ~/.zshrc ]; then
    if grep -q "ANTHROPIC_API_KEY" ~/.zshrc; then
        echo "✓ ~/.zshrc 中已有配置"
    else
        echo "" >> ~/.zshrc
        echo "# Claude API Key (竞品监测平台)" >> ~/.zshrc
        echo "export ANTHROPIC_API_KEY=\"$api_key\"" >> ~/.zshrc
        echo "✓ 已添加到 ~/.zshrc"
    fi
fi

echo ""
echo "✓ API Key 配置成功！"
echo ""
echo "下一步："
echo "1. 重启终端或运行: source ~/.zshrc"
echo "2. 重启平台服务: cd /Users/xiaoxiao.liu/竞品监测平台 && ./start.sh"
echo ""
