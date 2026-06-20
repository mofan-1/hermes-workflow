"""
配置管理模块
"""

import os
from pathlib import Path


def load_config():
    """加载配置，优先从环境变量读取，其次从 .env 文件"""
    config = {
        "feishu": {
            "app_id": os.getenv("FEISHU_APP_ID", ""),
            "app_secret": os.getenv("FEISHU_APP_SECRET", ""),
        },
        "deepseek": {
            "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
            "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
            "model": os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        },
        "obsidian": {
            "inbox_vault": os.getenv("INBOX_VAULT_PATH", os.path.expanduser("~/hermes-workflow/inbox-vault")),
            "deep_vault": os.getenv("DEEP_VAULT_PATH", os.path.expanduser("~/hermes-workflow/deep-vault")),
        },
        "server": {
            "port": int(os.getenv("PORT", "9000")),
            "host": os.getenv("HOST", "0.0.0.0"),
        },
    }
    return config


def check_config(config):
    """检查配置是否完整"""
    missing = []

    if not config["feishu"]["app_id"]:
        missing.append("FEISHU_APP_ID（飞书应用 ID）")
    if not config["feishu"]["app_secret"]:
        missing.append("FEISHU_APP_SECRET（飞书应用 Secret）")
    if not config["deepseek"]["api_key"]:
        missing.append("DEEPSEEK_API_KEY（DeepSeek API 密钥）")

    return missing
