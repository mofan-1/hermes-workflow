"""
Hermes Workflow Server - 飞书 AI 知识管理工作流后端

飞书机器人接收消息 → AI 理解分类 → 自动写入 Obsidian 知识库

启动方式：
  python main.py

环境变量（或 .env 文件）：
  FEISHU_APP_ID=你的飞书应用ID
  FEISHU_APP_SECRET=你的飞书应用Secret
  DEEPSEEK_API_KEY=你的DeepSeek API Key
  INBOX_VAULT_PATH=~/hermes-workflow/inbox-vault
  DEEP_VAULT_PATH=~/hermes-workflow/deep-vault
"""

import os
import json
import hashlib
import hmac
import base64
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# 加载 .env 文件（如果存在）
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
if os.path.exists(dotenv_path):
    with open(dotenv_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip().strip("'\"")
            if not os.environ.get(key):
                os.environ[key] = value

from config import load_config, check_config
from ai import AIProcessor
from vault_writer import VaultWriter


# 全局实例
config = load_config()
ai = AIProcessor(config)
vault = VaultWriter(config)


class FeishuHandler(BaseHTTPRequestHandler):
    """处理飞书 Webhook 请求"""

    def do_GET(self):
        """健康检查"""
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "time": datetime.now().isoformat()}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """处理飞书事件回调"""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            self._respond(400, {"error": "无效的 JSON"})
            return

        # 飞书 URL 验证（首次配置时）
        if data.get("type") == "url_verification":
            self._respond(200, {"challenge": data.get("challenge")})
            return

        # 验证签名（生产环境建议开启）
        # if not self._verify_signature(body):
        #     self._respond(403, {"error": "签名验证失败"})
        #     return

        # 处理消息事件
        if data.get("type") == "event_callback" or data.get("header", {}).get("event_type"):
            self._handle_event(data)
            return

        self._respond(200, {"ok": True})

    def _verify_signature(self, body):
        """验证飞书 Webhook 签名（可选）"""
        try:
            timestamp = self.headers.get("X-Lark-Request-Timestamp", "")
            nonce = self.headers.get("X-Lark-Request-Nonce", "")
            signature = self.headers.get("X-Lark-Signature", "")
            app_secret = config["feishu"]["app_secret"]

            if not timestamp or not nonce or not signature:
                return True  # 没有签名信息时不验证

            # 计算签名
            sign_str = timestamp + nonce + body.decode("utf-8")
            expected = base64.b64encode(
                hmac.new(app_secret.encode(), sign_str.encode(), hashlib.sha256).digest()
            ).decode()

            return expected == signature
        except Exception:
            return True  # 验证出错时不阻塞

    def _handle_event(self, data):
        """处理飞书事件"""
        try:
            # 兼容新旧事件格式
            event = data.get("event", data.get("header", {}))
            event_type = event.get("event_type") or data.get("header", {}).get("event_type", "")

            # 只处理消息事件
            if "message" not in event_type and "im.message" not in event_type:
                self._respond(200, {"ok": True})
                return

            # 解析消息内容
            message = event.get("message", {})
            msg_type = message.get("message_type", "")
            content_str = message.get("content", "{}")

            # 只处理文本消息
            if msg_type != "text":
                self._respond(200, {"ok": True})
                return

            # 解析文本内容
            try:
                content = json.loads(content_str)
                text = content.get("text", "")
            except json.JSONDecodeError:
                text = content_str

            # 去掉 @机器人 前缀
            import re
            text = re.sub(r"@_user_\d+\s*", "", text).strip()

            if not text:
                self._respond(200, {"ok": True})
                return

            print(f"\n📩 收到消息: {text[:50]}...")

            # AI 分析意图
            analysis = ai.analyze_content(text)
            intent = analysis.get("intent", "chat")
            target = analysis.get("target", "inbox")
            print(f"🧠 AI 分析: intent={intent}, target={target}")

            # 根据意图处理
            if intent == "process":
                # 加工请求 → 深加工知识库
                content_type = "article"
                if "文案" in text or "广告" in text:
                    content_type = "copywriting"
                    result = ai.generate_copywriting(text)
                elif "碰撞" in text or "角度" in text or "观点" in text:
                    content_type = "collision"
                    result = ai.generate_article(f"从不同角度分析：{text}")
                elif "洞察" in text or "深度" in text:
                    content_type = "insight"
                    result = ai.generate_article(f"深度分析：{text}")
                else:
                    result = ai.generate_article(text)

                filepath = vault.save_to_deep(result, analysis, content_type)
                print(f"✅ 已保存到深加工库: {filepath}")

            else:
                # 灵感/聊天/其他 → 收件箱知识库
                filepath = vault.save_to_inbox(text, analysis)
                print(f"✅ 已保存到收件箱: {filepath}")

            self._respond(200, {"ok": True})

        except Exception as e:
            print(f"❌ 处理出错: {e}")
            self._respond(200, {"ok": True})

    def _respond(self, status, data):
        """发送响应"""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        """精简日志"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0] if args else ''}")


def main():
    """启动服务器"""
    missing = check_config(config)
    if missing:
        print("❌ 缺少必要配置：")
        for item in missing:
            print(f"   - {item}")
        print("\n请设置环境变量或在 .env 文件中配置。")
        print("参考 README.md 中的配置说明。")
        return

    # 初始化知识库
    paths = vault.init_vaults()
    print(f"📁 收件箱知识库: {paths['inbox']}")
    print(f"🔨 深加工知识库: {paths['deep']}")

    host = config["server"]["host"]
    port = config["server"]["port"]

    print(f"\n🚀 Hermes Workflow Server 启动成功！")
    print(f"📡 监听地址: http://{host}:{port}")
    print(f"🔗 Webhook URL: http://你的公网IP:{port}")
    print(f"📋 健康检查: http://localhost:{port}/health")
    print("\n在飞书上跟机器人对话，内容会自动存入 Obsidian 知识库。\n")

    server = HTTPServer((host, port), FeishuHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 服务已停止")
        server.server_close()


if __name__ == "__main__":
    main()
