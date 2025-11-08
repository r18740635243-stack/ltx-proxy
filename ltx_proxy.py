# ltx_proxy.py
# 免费 LTX Studio 代理 (Render 部署版)
# 用于解决中国大陆服务器无法访问 api.ltxstudio.com 的问题

from flask import Flask, request, jsonify, Response
import requests
import os

app = Flask(__name__)

LTX_API_URL = "https://api.ltxstudio.com/v1/videos"
LTX_API_KEY = os.getenv("LTX_API_KEY", "")
SHARED_SECRET = os.getenv("SHARED_SECRET", "")  # 可选访问密钥保护

@app.route("/ltx", methods=["POST"])
def proxy_ltx():
    if SHARED_SECRET:
        token = request.headers.get("X-Proxy-Token") or request.json.get("proxy_token")
        if token != SHARED_SECRET:
            return jsonify({"error": "Unauthorized"}), 401

    headers = {
        "Authorization": f"Bearer {LTX_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(LTX_API_URL, headers=headers, json=request.get_json(), timeout=180)
        return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type','application/json'))
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "proxy_error", "detail": str(e)}), 502

@app.route("/", methods=["GET"])
def index():
    return jsonify({"ok": True, "note": "LTX proxy running. POST /ltx with same JSON you'd send to LTX."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
