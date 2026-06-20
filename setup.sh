#!/bin/bash
# ============================================
# Hermes Workflow 一键安装脚本
# 飞书 + Hermes + Obsidian AI 知识管理工作流
# ============================================

set -e

echo "========================================"
echo "  Hermes Workflow 安装程序"
echo "  飞书 + Hermes + Obsidian 知识管理工作流"
echo "========================================"
echo ""

# 检查 Python
echo "🔍 检查 Python..."
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "❌ 未检测到 Python，请先安装 Python 3.11+"
    exit 1
fi
echo "✅ Python: $($PYTHON --version)"

# 检查 pip
echo "🔍 检查 pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ 未检测到 pip3"
    exit 1
fi
echo "✅ pip3 已就绪"

# 安装 Hermes Workflow
echo ""
echo "📦 安装 Hermes Workflow..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 创建可执行脚本
cat > /tmp/hermes-workflow << 'PYEOF'
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hermes_workflow.cli import main
main()
PYEOF

# 安装到系统
pip3 install -e . 2>/dev/null || {
    # 如果 pip install 失败，用脚本方式
    chmod +x /tmp/hermes-workflow
    mkdir -p ~/.local/bin
    cp /tmp/hermes-workflow ~/.local/bin/hermes-workflow
    chmod +x ~/.local/bin/hermes-workflow

    # 如果 PATH 中没有 ~/.local/bin，提示
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> ~/.zshrc
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> ~/.bashrc
    fi
}

echo ""
echo "========================================"
echo "  ✅ Hermes Workflow 安装成功！"
echo "========================================"
echo ""
echo "📖 使用命令："
echo ""
echo "  hermes-workflow install    一键创建知识库 + 生成配置"
echo "  hermes-workflow init       创建两个 Obsidian 知识库"
echo "  hermes-workflow config     生成 Hermes 配置文件"
echo "  hermes-workflow inbox ...  快速记录灵感"
echo ""
echo "📋 开始使用："
echo ""
echo "  1. 运行：hermes-workflow install"
echo "  2. 编辑 ~/.hermes/.env 填入 DeepSeek API Key"
echo "  3. 在 Obsidian 中打开 ~/hermes-workflow/inbox-vault"
echo "  4. 在 Obsidian 中打开 ~/hermes-workflow/deep-vault"
echo ""
echo "📌 然后在飞书或终端中跟 Hermes 对话："
echo '  "灵感：今天想到一个做AI内容的好方向"'
echo '  "帮我把这个灵感展开成一篇文章"'
echo ""
