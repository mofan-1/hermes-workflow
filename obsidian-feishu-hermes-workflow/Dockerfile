# ============================================
# Hermes Workflow - Docker 镜像
# 飞书 AI 机器人 + Obsidian 知识管理工作流
# ============================================

FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制源码
COPY server/ ./server/
COPY setup.py .
COPY .env.example .

# 创建默认知识库目录
RUN mkdir -p /data/inbox-vault /data/deep-vault

# 暴露端口
EXPOSE 9000

# 启动命令
CMD ["python", "server/main.py"]
