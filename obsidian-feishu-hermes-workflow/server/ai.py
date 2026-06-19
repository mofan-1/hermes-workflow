"""
AI 处理器 - 调用 DeepSeek API 理解和分类内容
"""

import json
import requests


class AIProcessor:
    def __init__(self, config):
        self.api_key = config["deepseek"]["api_key"]
        self.base_url = config["deepseek"]["base_url"]
        self.model = config["deepseek"]["model"]

    def analyze_content(self, text):
        """
        分析用户输入，判断意图：
        - inspiration: 灵感/想法 → 存入收件箱
        - process: 加工请求 → 存入深加工库
        - unknown: 无法判断
        """
        prompt = f"""分析以下用户输入，判断意图并提取关键信息。

用户输入：{text}

请以 JSON 格式返回，不要包含其他内容：
{{
  "intent": "inspiration | process | chat",
  "title": "提炼的标题",
  "tags": ["标签1", "标签2"],
  "summary": "一句话摘要",
  "target": "inbox | deep",
  "reason": "判断理由"
}}

规则：
- inspiration = 记录灵感、想法、碎片信息 → target: inbox
- process = 要求写文章、生成文案、碰撞观点 → target: deep
- chat = 普通对话 → target: inbox（作为日常记录）
"""

        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "你是一个知识管理助手，负责分析用户输入并分类。"},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500,
                },
                timeout=30,
            )

            if resp.status_code != 200:
                return {"intent": "chat", "title": "未分类内容", "tags": [], "summary": text, "target": "inbox"}

            result = resp.json()
            content = result["choices"][0]["message"]["content"]

            # 提取 JSON
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
                content = content.rsplit("\n", 1)[0]
                if content.endswith("```"):
                    content = content[:-3]

            parsed = json.loads(content)
            return parsed

        except Exception as e:
            return {"intent": "chat", "title": "未分类内容", "tags": [], "summary": str(e), "target": "inbox"}

    def generate_article(self, text):
        """根据灵感生成文章"""
        prompt = f"""根据以下内容生成一篇完整的公众号风格文章。

素材：{text}

要求：
- 标题吸引人
- 开头有吸引力
- 正文逻辑清晰
- 结尾有行动号召
- 字数 800-1500 字
"""

        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "你是一个专业的内容创作者，擅长写公众号文章。"},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 4000,
                },
                timeout=120,
            )

            if resp.status_code != 200:
                return f"生成失败：{resp.text}"

            result = resp.json()
            return result["choices"][0]["message"]["content"]

        except Exception as e:
            return f"生成出错：{str(e)}"

    def generate_copywriting(self, text):
        """根据素材生成营销文案"""
        prompt = f"""根据以下素材，生成3条不同风格的朋友圈推广文案。

素材：{text}

要求：
- 每条50-150字
- 风格1：专业权威型
- 风格2：亲和故事型
- 风格3：紧迫促销型
- 每条配一个 emoji 标题
"""

        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "你是一个营销文案专家。"},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.8,
                    "max_tokens": 2000,
                },
                timeout=60,
            )

            if resp.status_code != 200:
                return f"生成失败：{resp.text}"

            result = resp.json()
            return result["choices"][0]["message"]["content"]

        except Exception as e:
            return f"生成出错：{str(e)}"
