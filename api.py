from flask import Flask, request, jsonify
import requests
from Apikey import key 

mykey = key()
my_api_key = mykey.get_key()

url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

app = Flask(__name__)
headers = {
    "Authorization": my_api_key,
    "Content-Type": "application/json"
}

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    messages = data.get('messages', [])
    prompt = data.get('prompt', '')

    # 构建正确的 messages 格式
    chat_messages = []
    
    # 添加历史消息
    for msg in messages:
        chat_messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        })
    
    # 添加当前用户输入
    chat_messages.append({
        "role": "user",
        "content": prompt
    })

    payload = {
        "model": "glm-4.6v-Flash",
        "messages": chat_messages,
        "stream": False,
        "temperature": 1
    }

    # 打印请求信息，方便调试
    print("==================== 收到请求 ====================")
    print(f"历史消息数: {len(messages)}")
    print(f"当前提示: {prompt[:100]}...")  # 只打印前100字符

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        # 检查响应状态
        if response.status_code != 200:
            return jsonify({
                "content": f"智谱API返回错误: {response.status_code} - {response.text}"
            }), 200
        
        response_json = response.json()
        
        # 提取实际的回复内容
        if "choices" in response_json and len(response_json["choices"]) > 0:
            content = response_json["choices"][0].get("message", {}).get("content", "")
            print(f"返回内容长度: {len(content)}")
            print(f"返回内容预览: {content[:100]}...")  # 只打印前100字符
            return jsonify({"content": content})
        else:
            return jsonify({"content": f"API返回格式异常: {response_json}"})
            
    except requests.exceptions.Timeout:
        return jsonify({"content": "智谱API请求超时"})
    except requests.exceptions.ConnectionError:
        return jsonify({"content": "无法连接到智谱API"})
    except Exception as e:
        return jsonify({"content": f"请求异常: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=False, port=5000, host='0.0.0.0')