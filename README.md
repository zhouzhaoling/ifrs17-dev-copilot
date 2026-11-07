# IFRS17 研发效能辅助系统 (多 Agent + AI Loop 架构演进)

本项目是 **IFRS17 智能财务分析平台 (V1)** 的下一代演进方向（V2.0）。

从“单 Agent + 固定长工作流”走向**“多 Agent + 标准化 Skill 体系”**。本项目重点验证了如何通过**配置化编排**替代硬编码路由，并引入**自动化回归测试**与**AI 自循环反思**，解决大模型应用中“改一个坏一片”的规模化落地难题。

## 🏗️ 架构演进：从硬编码到配置驱动

- **V1.0 时代**：硬编码 Router 节点，新增业务场景需修改核心代码，维护成本极高。
- **V2.0 时代（本项目）**：
  - **配置化编排**：路由规则固化在 `config/agent.md`，新增场景不改 Python 代码。
  - **动态 Skill 加载**：能力封装在 `skills/*.md`，通过 YAML front-matter 界定边界与工具。
  - **自动化回归**：基于 `tests/regression_set.json` 实现 AI 驱动的全量测试集回归，解决“改一个坏一片”的痛点。

## 🛠️ 技术栈
- **核心框架**：Python 3.10, LangGraph
- **大模型服务**：Ollama 本地私有化部署 (Qwen2.5-7B)
- **工具调度**：LangChain Tool Calling

## 📂 核心目录结构

```text
ifrs17-dev-copilot/
├── config/
│   └── agent.md            # 全局路由配置（单一事实来源）
├── skills/
│   ├── diff_analysis.md    # 差异分析技能（定义了适用的业务边界）
│   ├── smart_query.md      # 智能问数技能
│   └── report_gen.md       # 报告生成技能
├── core/
│   ├── skill_loader.py     # 解析 MD 的 SkillLoader
│   └── graph.py            # 极简的 LangGraph 编排（Router + Executor）
├── tests/
│   └── regression_set.json # 自动化回归测试集
└── main.py                 # 执行回归测试的入口
```

## 🚀 快速启动

### 1. 准备环境
```bash
# 安装依赖
pip install langgraph langchain-ollama pyyaml

# 确保本地已启动 Ollama 并拉取模型
ollama run qwen2.5:7b
```

### 2. 运行自动化回归测试
```bash
python main.py
```
**预期结果**：系统会自动跑通 3 个业务场景的用例，并打印 `3/3 通过`。终端将展示完整的路由决策与动态工具调用日志。

## 💡 核心设计亮点

1. **边界先行**：在 `skills/*.md` 中强制要求填写“适用边界”与“排斥条件”，从设计层面杜绝模型误调用。
2. **动态工具挂载**：Python 代码本身不写死绑定哪个工具，而是由 `agent.md` 解析 `tools: query_db` 字段动态注入，实现业务与代码彻底解耦。
3. **回归驱动开发**：在 `main.py` 中集成了断言机制，未来修改任何 Prompt 或配置，跑一遍回归即可确保历史能力不退化。

## 📝 演进规划 (TODO)
- [ ] 引入 **Reflection (反思) 节点**：当测试用例 FAIL 时，自动让大模型分析原因并沉淀到本地记忆库中。
- [ ] 将本地 `query_db` 工具替换为标准的 **MCP Server**，实现跨部门工具复用。