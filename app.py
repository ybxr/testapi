# -*- coding: utf-8 -*-
import re
import json
import requests
from CHATAI import ChatAi,SqlMsg
from flask import Flask, request, jsonify, render_template, Response

app = Flask(__name__)
chat_ai = ChatAi()

@app.route("/", methods=["GET"])
def index():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    messages = request.form.get("prompts", None)
    prompts = json.loads(messages)[-1]["content"]
    try:
        data = chat_ai.get_massage(prompts)
        resp = requests.post(
            url=data["url"],
            headers=data["headers"],
            json=data["json"],
            stream=True,
            timeout=(10, 10)
        )
        # print(resp.text)
    except requests.exceptions.Timeout:
        return jsonify({"error": {"message": "请求超时，请稍后再试！", "type": "timeout_error", "code": ""}})

    # 迭代器实现流式响应
    def generate():
        errorStr = ""
        for chunk in resp.iter_content(chunk_size=1024):
            if chunk:
                # print(chunk)
                streamStr = chunk.decode("utf-8", errors="ignore")
                data = r"".join(re.findall('{"data":"(.*?)","code":0,"message":"成功"}',streamStr)).replace("\\n","\n")
                yield data
        # 如果出现错误，此时错误信息迭代器已处理完，app_context已经出栈，要返回错误信息，需要将app_context手动入栈
        if errorStr != "":
            with app.app_context():
                yield errorStr

    return Response(generate(), content_type='application/octet-stream')

if __name__ == '__main__':
    app.run(port=5000)