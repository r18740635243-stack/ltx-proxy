# app.py
from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# 从 Render 环境变量读取密钥
LTX_API_KEY = os.getenv("LTX_API_KEY", "")

# 主页：显示已暴露的端点，便于排查
@app.route("/")
def home():
    return jsonify({
        "message": "LTX proxy is running on Render",
        "endpoints": ["/ping", "/ltx", "/internal-ltx", "/routes"]
    })

# 健康检查
@app.route("/ping")
def ping():
    return jsonify({"status": "ok"})

# 列出当前所有路由（诊断用）
@app.route("/routes")
def routes():
    rules = sorted([r.rule for r in app.url_map.iter_rules()])
    return jsonify({"routes": rules})

def _call_ltx_api(prompt: str, resolution: str = "720p"):
    if not LTX_API_KEY:
        return {"error": "LTX_API_KEY is empty/not set in Render env"}, 500

    payload = {
        "prompt": prompt,
        "resolution": resolution or "720p"
    }
    headers = {
        "Authorization": f"Bearer {LTX_API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        r = requests.post(
            "https://api.ltxstudio.com/v1/videos",
            headers=headers,
            json=payload,
            timeout=60
        )
        # 直接把上游的 JSON 返回
        return r.json(), r.status_code
    except Exception as e:
        return {"error": str(e)}, 500

# 公开给你直接调用的端点
@app.route("/ltx", methods=["POST"])
def ltx():
    try:
        data = request.get_json(force=True, silent=True) or {}
        prompt = data.get("prompt")
        resolution = data.get("resolution", "720p")
        if not prompt:
            return jsonify({"error": "missing 'prompt'"}), 400
        body, status = _call_ltx_api(prompt, resolution)
        return jsonify(body), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 供 Cloudflare Worker 转发用（路径与 Worker 中保持一致）
@app.route("/internal-ltx", methods=["POST"])
def internal_ltx():
    try:
        data = request.get_json(force=True, silent=True) or {}
        prompt = data.get("prompt")
        resolution = data.get("resolution", "720p")
        if not prompt:
            return jsonify({"error": "missing 'prompt'"}), 400
        body, status = _call_ltx_api(prompt, resolution)
        return jsonify(body), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # 本地/Render 通用
    app.run(host="0.0.0.0", port=10000)
