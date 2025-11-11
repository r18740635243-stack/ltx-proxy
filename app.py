@app.route("/internal-ltx", methods=["POST"])
def internal_ltx():
    data = request.get_json()
    prompt = data.get("prompt")
    resolution = data.get("resolution", "720p")

    payload = {
        "prompt": prompt,
        "resolution": resolution
    }

    headers = {
        "Authorization": f"Bearer {LTX_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # 直接访问 LTX Studio 官方 API
        r = requests.post("https://api.ltxstudio.com/v1/videos", headers=headers, json=payload)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
