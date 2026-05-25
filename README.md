# MiniCodeAgent 项目说明

MiniCodeAgent 是一个轻量级代码智能体（Code Agent）示例项目，旨在帮助理解类似 Codex、Trae、Claude Code 等智能体的运行原理。  
目前仅完整实现 **WRITE** 操作，其他操作（READ、DIR）仅预留工具方法，尚未集成二次调用逻辑。

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `api.py` | Flask Web 服务接口，负责与大模型交互并返回结果。 |
| `Apikey.py` | 存储大模型 API Key，通过 `get` 方法获取。 |
| `CodeAgent.py` | 核心逻辑，包括数据存储、工具方法定义及 Agent 主流程。 |

---

## 运行步骤

1. 修改 `Apikey.py` 中的 `API_KEY` 为你的有效大模型密钥。
2. 根据所用模型的返回格式，调整 `api.py` 中的结果解析逻辑。
3. 启动后端服务：  
   ```bash
   python api.py
   ```
4. 启动智能体：  
   ```bash
   python CodeAgent.py
   ```
5. 输入需要写入的内容，如果一次不行需要多次调用，或者修改规则提示词。

---

## 注意事项

- **项目性质**：本为演示代码，存在安全风险与逻辑不严谨之处，**不可用于生产环境**。深入学习建议参考 [LangChain](https://www.langchain.com/)。
- **API 适配**：请严格依据所使用大模型的官方文档，正确处理返回结构。
- **功能现状**：
  - WRITE：完整支持
  - READ / DIR：工具方法已完成，但缺少二次调用逻辑，当前无法在 Agent 流程中自动触发。
- **架构图**：项目结构可参考 `架构.drawio`，建议使用 [draw.io](https://app.diagrams.net/) 在线查看。

---

## 学习建议

如希望构建更完整、安全的智能体应用，推荐学习以下内容：

- 工具调用（Function Calling / Tool Use）
- 记忆与上下文管理
- 规划与任务分解策略（如 ReAct, CoT）
- 安全约束与沙盒执行环境

---
Ciallo～(∠・ω< )⌒★
