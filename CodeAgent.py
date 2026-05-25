from datetime import datetime
import json
import os
import requests
# 全局配置
LLM_API_URL = "http://localhost:5000/api/chat"
SAVE_JSON_FILE = "agent_context.json"

# 上下文记忆
"""
    新增对话
    提取接口需要的标准上下文格式
    保存文件
    加载历史对话
"""
class ContextMemory:
    def __init__(self):
        self.history = []
    
    def add_record(self, role: str, content: str):
        self.history.append({
            "role": role, 
            "content": content,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    
    def get_llm_context(self):
        return [{"role": record["role"], "content": record["content"]} for record in self.history]
    
    def save_history(self):
        with open(SAVE_JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)

    def load_history(self):
        try:
            with open(SAVE_JSON_FILE, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
        except:
            self.history = []

# 本地文件操作工具
"""
    列出目录文件
    读取文件内容
    写入文件内容
"""
class LocalFileTools:

    @staticmethod
    def list_folder(path:str = "./") -> str:
        try:
            return "\n".join(os.listdir(path))
        except Exception as e:
            return f"文件读取失败:{str(e)}"
        
    @staticmethod
    def read_target_file(file_path:str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"文件读取失败:{str(e)}"
        
    @staticmethod
    def write_target_file(file_path:str, content:str) -> str:
        try:
            dir_name = os.path.dirname(file_path)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name)
            with open(file_path, "w", encoding='utf-8') as f:
                f.write(content)
            return f"文件写入成功:{file_path}"
        except Exception as e:
            return f"文件写入失败:{str(e)}"

class CodeAgent:
    def __init__(self):
        self.memory = ContextMemory()
        self.tools = LocalFileTools()
        self.system_rule = """
你是本地的代码开发助手。你的所有回复必须严格遵守以下格式，不要添加任何额外的说明文字：

【操作规则】
- 如果用户要求创建/写入文件：回复格式必须为 [WRITE]文件名.后缀|文件完整内容
  例如：[WRITE]hello.py|print("Hello, World!")
  
- 如果用户要求读取文件：回复格式必须为 [READ]文件路径
  例如：[READ]hello.py
  
- 如果用户要求查看目录：回复格式必须为 [DIR]文件夹路径
  例如：[DIR]./
  
- 如果用户进行普通对话或要求显示代码（不涉及文件操作）：直接输出纯代码或回复内容，不要添加任何标记

【重要】
1. 回复中只能包含上述格式的内容，不要添加"1.写入操作："、"以下是代码："等额外文字
2. 文件路径只需要文件名和后缀，如 hello.py，不需要完整路径
3. 不要添加任何解释性文字，直接输出操作指令或代码
4. 严格以 [WRITE]、[READ]、[DIR] 或普通内容开头
5.代码方面，只需要输出代码本身，不要添加任何说明文字或注释，以及不要输出任何非代码内容

现在开始执行用户的指令。
"""

    def request_llm_api(self, user_input: str) -> str:
        full_prompt = f"{self.system_rule}\n用户当前需求：{user_input}"
        post_data = {
            "messages": self.memory.get_llm_context(),
            "prompt": full_prompt
        }

        try:
            # 未设置超时时间
            response = requests.post(LLM_API_URL, json=post_data)
            res_json = response.json()
            print(f"LLM返回内容: {res_json.get('content', '')}")
            return res_json.get("content", "")
        except Exception as e:
            return f"接口请求异常:{str(e)}"

    def parse_action_command(self, response_text: str):
        print("解析LLM返回的文本，判断是否包含操作指令，并执行相应的工具函数")
        print(f"LLM返回的原始文本: {response_text}")
        print("=============================")
        """解析LLM返回的文本，判断是否包含操作指令，并执行相应的工具函数"""
        # 清楚文本中开头的空格，换行符等
        response_text = response_text.strip()
        
        if response_text.startswith("[WRITE]"):
            split_data = response_text.replace("[WRITE]", "").split("|", 1)
            if len(split_data) == 2:
                return "write", split_data[0].strip(), split_data[1]
        elif response_text.startswith("[READ]"):
            target_path = response_text.replace("[READ]", "").strip()
            return "read", target_path, ""
        elif response_text.startswith("[DIR]"):
            target_dir = response_text.replace("[DIR]", "").strip()
            return "dir", target_dir, ""
        
        return "chat","", response_text
  
    def run_task(self, user_input: str) -> str:
        print("user_input: ", user_input)
        self.memory.add_record("user", user_input)

        llm_result = self.request_llm_api(user_input)
        action, path, content = self.parse_action_command(llm_result)

        if action == "write":
            final_reply = self.tools.write_target_file(path, content)
        elif action == "read":
            final_reply = self.tools.read_target_file(path)
        elif action == "dir":
            final_reply = self.tools.list_folder(path)
        else:
            final_reply = llm_result

        self.memory.add_record("assistant", final_reply)
        self.memory.save_history()

        return final_reply
    
if __name__ == "__main__":
    agent = CodeAgent()
    user_text = input("请输入你的需求：")
    if user_text.strip().lower() == ["exit", "quit"]:
        exit()
    result = agent.run_task(user_text)
    print(result)
    
    