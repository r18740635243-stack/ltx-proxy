from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# === 读取环境变量（从 Render 设置中读取 API 密钥）===
LTX_API_KEY = os.getenv("LTX_API_KEY")
SHARED_SECRET = os.getenv("SHARED_SECRET")

# === Cloudflare Worker 地址（替换为你自己的 Worker 链接）===
CLOUDFLARE_WORKER_URL = "https://flat-dream-2ae2.r18740635243.workers.dev"


# === 首页测试接口 ===
@app.route('/')
def home():
    return jsonify({
        "message": "LTX proxy is running via Cloudflare Worker",
        "endpoints": ["/ping", "/ltx"]
    })


# === 健康检测接口 ===
@app.route('/ping')
def ping():
    return jsonify({"status": "ok"})


# === 主要的 LTX Studio 转发接口 ===
@app.route("/ltx", methods=["POST"])
def proxy_ltx():
    try:
        data = request.get_json()
        prompt = data.get("prompt")
        resolution = data.get("resolution", "720p")

        if not prompt:
            return jsonify({"error": "Missing 'prompt' field"}), 400

        payload = {
            "prompt": prompt,
            "resolution": resolution
        }

        headers = {
            "Authorization": f"Bearer {LTX_API_KEY}",
            "Content-Type": "application/json"
        }

        # 向 LTX Studio 发送请求
        r = requests.post("https://api.ltxstudio.com/v1/videos", headers=headers, json=payload)

        # 返回 LTX Studio 的原始响应
        return jsonify(r.json()), r.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# === 启动 Flask 服务 ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
