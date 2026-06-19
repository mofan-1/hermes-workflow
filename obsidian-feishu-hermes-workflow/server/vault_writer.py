"""
Obsidian 知识库写入模块
"""

import os
import json
from datetime import datetime
from pathlib import Path


class VaultWriter:
    def __init__(self, config):
        self.inbox_path = os.path.expanduser(config["obsidian"]["inbox_vault"])
        self.deep_path = os.path.expanduser(config["obsidian"]["deep_vault"])

    def save_to_inbox(self, content, analysis):
        """保存内容到收件箱知识库"""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M")
        file_date = now.strftime("%Y%m%d_%H%M%S")
        title = analysis.get("title", "未命名灵感")
        tags = analysis.get("tags", [])
        tags_str = ", ".join(["灵感"] + tags)

        # 确定子目录
        if "想法" in tags or "灵感" in tags:
            sub_dir = "灵感"
        elif "文章" in tags or "阅读" in tags:
            sub_dir = "文章收藏"
        else:
            sub_dir = "待整理"

        target_dir = os.path.join(self.inbox_path, sub_dir)
        Path(target_dir).mkdir(parents=True, exist_ok=True)

        filename = f"{file_date}_{title[:30]}.md"
        filepath = os.path.join(target_dir, filename)

        content_text = f"""---
title: {title}
created: {date_str}
tags: [{tags_str}]
status: inbox
source: 飞书
---

# {title}

> {analysis.get("summary", "")}

---

## 原始内容

{content}

---

## 关联
-

## 待办
- [ ] 整理到深加工知识库
"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content_text)

        return filepath

    def save_to_deep(self, content, analysis, content_type="article"):
        """保存内容到深加工知识库"""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M")
        file_date = now.strftime("%Y%m%d_%H%M%S")
        title = analysis.get("title", "未命名作品")

        # 根据内容类型选择子目录
        sub_dir_map = {
            "article": "文章",
            "copywriting": "文案",
            "insight": "洞察",
            "collision": "碰撞",
            "project": "项目",
        }
        sub_dir = sub_dir_map.get(content_type, "洞察")

        target_dir = os.path.join(self.deep_path, sub_dir)
        Path(target_dir).mkdir(parents=True, exist_ok=True)

        filename = f"{file_date}_{title[:30]}.md"
        filepath = os.path.join(target_dir, filename)

        content_text = f"""---
title: {title}
created: {date_str}
tags: [{sub_dir}, 深加工]
status: active
---

# {title}

---

{content}

---

> 由 Hermes Workflow 自动生成
"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content_text)

        return filepath

    def init_vaults(self):
        """初始化两个知识库的目录结构"""
        inbox_structure = ["灵感", "文章收藏", "待整理", "日常记录"]
        deep_structure = ["洞察", "文章", "文案", "碰撞", "项目"]

        for folder in inbox_structure:
            Path(os.path.join(self.inbox_path, folder)).mkdir(parents=True, exist_ok=True)

        for folder in deep_structure:
            Path(os.path.join(self.deep_path, folder)).mkdir(parents=True, exist_ok=True)

        return {
            "inbox": self.inbox_path,
            "deep": self.deep_path,
        }
