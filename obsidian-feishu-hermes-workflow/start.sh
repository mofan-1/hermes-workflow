#!/bin/bash
# ============================================
# Hermes Workflow Server 启动脚本
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "  Hermes Workflow Server"
echo "  飞书 → AI → Obsidian 知识工作流"
echo "========================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未检测到 Python 3，请先安装"
    exit 1
fi
echo "✅ Python: $(python3 --version)"

# 安装依赖
echo "📦 安装依赖..."
pip3 install -r requirements.txt -q 2>/dev/null || pip install -r requirements.txt -q

# 检查配置
if [ -z "$FEISHU_APP_ID" ] && [ ! -f .env ]; then
    echo ""
    echo "⚠️  未检测到配置"
    echo ""
    echo "请创建 .env 文件，或设置以下环境变量："
    echo ""
    echo "  FEISHU_APP_ID=你的飞书应用ID"
    echo "  FEISHU_APP_SECRET=你的飞书应用Secret"
    echo "  DEEPSEEK_API_KEY=你的DeepSeek API Key"
    echo ""
    echo "参考 .env.example 文件"
    echo ""
    echo "是否仍要启动？（仅启动健康检查）[y/N] "
    read -r response
    if [[ ! "$response" =~ ^[yY]$ ]]; then
        exit 0
    fi
fi

# 启动服务器
echo ""
echo "🚀 启动服务..."
cd server
python3 main.py
