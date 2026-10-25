#!/bin/bash

# ============================================
# 服务器环境设置脚本
# 用于在远程服务器上设置 Python 环境
# ============================================

set -e

REMOTE_HOST="book"
REMOTE_PATH="~/workspace/bookshelf"

echo "============================================"
echo "  服务器环境设置"
echo "============================================"

# SSH 到服务器并执行设置
ssh "$REMOTE_HOST" << 'EOF'
cd ~/workspace/bookshelf

echo "检查 Python 版本..."
python3 --version

echo ""
echo "创建虚拟环境..."
python3 -m venv venv

echo "激活虚拟环境..."
source venv/bin/activate

echo "升级 pip..."
pip install --upgrade pip

echo "安装依赖..."
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo ""
echo "环境设置完成！"
echo "使用以下命令启动服务:"
echo "  cd ~/workspace/bookshelf"
echo "  source venv/bin/activate"
echo "  python main.py"
EOF

echo ""
echo "============================================"
echo "环境设置完成！"
echo "============================================"
