import os
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from core.skill_loader import SkillLoader
from langchain_core.tools import tool
import json

# 1. 定义全局 State
class AgentState(TypedDict):
    user_query: str
    selected_skill: str
    final_answer: str

loader = SkillLoader()
llm = ChatOllama(model="qwen2.5:7b", temperature=0)

# ==========================================
# 节点 1：路由大脑（读取 agent.md 规则 + 历史踩坑记忆）
# ==========================================
def router_node(state: AgentState):
    print("\n>>> [Router] 正在根据 config/agent.md 与 历史踩坑记忆 决定调用哪个 Skill...")
    
    # 1. 读取全局配置
    with open("config/agent.md", "r", encoding="utf-8") as f:
        agent_config = f.read()

    # 2. 👇 新增：读取历史踩坑规则（记忆回注）
    history_rules = ""
    mem_path = "memory/reflection.json"
    
    if os.path.exists(mem_path):
        try:
            with open(mem_path, "r", encoding="utf-8") as f:
                rules = json.load(f)
                if rules:
                    # 将 JSON 数组转换为带短横线的列表文本，方便大模型阅读
                    rule_text = "\n".join([f"- {r}" for r in rules])
                    history_rules = f"\n【历史踩坑规则（必须严格遵守）】\n{rule_text}\n"
        except Exception as e:
            print(f"⚠️ 读取历史记忆失败: {e}")

    # 3. 组装 Prompt
    prompt = f"""
    你是一个企业级 AI 路由专家。请严格根据以下【路由规则配置表】和【历史踩坑规则】，判断用户输入应该使用哪个 Skill。
    
    【路由规则配置】
    {agent_config}
    {history_rules}
    【用户输入】
    {state['user_query']}
    
    要求：只输出选中的 Skill 名称（如 diff_analysis, smart_query, report_gen），不要输出任何标点或其他文字。
    """
    
    response = llm.invoke(prompt).content.strip()
    print(f">>> [Router] 决策结果: {response}")
    
    return {"selected_skill": response}

# ==========================================
# 节点 2：动态执行器（加载对应的 MD 并执行）
# ==========================================
# 1. 定义你的原子工具
@tool
def query_gl_database(org_name: str) -> str:
    """查询底层总账数据库，获取指定机构的准备金金额明细。"""
    if "上海" in org_name:
        return "上海机构准备金旧账套 1000 万，新账套 1250 万。"
    elif "北京" in org_name:
        return "北京机构准备金旧账套 2000 万，新账套 1990 万。"
    return "未找到数据。"

# 注册工具字典 (Key 对应 MD 文件里配置的 `tools` 名字)
TOOL_REGISTRY = {
    "query_db": query_gl_database 
}

def dynamic_executor_node(state: AgentState):
    skill_name = state["selected_skill"]
    print(f"\n>>> [Executor] 正在动态加载 [{skill_name}.md] 技能...")
    
    try:
        skill_data = loader.load_skill(skill_name)
        prompt_body = skill_data["prompt"]
        meta = skill_data["meta"]
        
        # 2. 动态解析并挂载工具
        required_tools = []
        if "tools" in meta and meta["tools"]:
            tool_names = [t.strip() for t in meta["tools"].split(",")]
            for name in tool_names:
                if name in TOOL_REGISTRY:
                    required_tools.append(TOOL_REGISTRY[name])
        
        print(f">>> [Executor] 解析到所需工具: {[t.name for t in required_tools]}")
        
        final_prompt = f"{prompt_body}\n\n用户输入：{state['user_query']}"
        
        # 3. 绑定工具并调用模型
        llm_with_tools = llm.bind_tools(required_tools) if required_tools else llm
        response = llm_with_tools.invoke(final_prompt)
        
        # 4. 解析工具调用 (使用 getattr 消除编辑器红线)
        if getattr(response, "tool_calls", None):
            tool_call = response.tool_calls[0]
            print(f">>> [Executor] 大模型决定调用工具: {tool_call['name']}")
            
            # 根据模型返回的工具名，在 required_tools 中找到对应的工具对象
            tool_to_execute = next((t for t in required_tools if t.name == tool_call['name']), None)
            
            if tool_to_execute:
                # 捕获工具执行可能产生的异常，防止程序崩溃
                try:
                    tool_result = tool_to_execute.invoke(tool_call['args'])
                except Exception as e:
                    print(f"⚠️ 工具执行异常: {e}")
                    tool_result = f"工具执行失败: {e}"
                    
                print(f">>> [Executor] 工具返回结果: {tool_result}")
                
                # 将工具结果喂给大模型做最终总结
                final_answer = llm.invoke(f"已知工具查询结果：{tool_result}，请根据用户需求生成回答。").content
                return {"final_answer": final_answer}
            else:
                return {"final_answer": f"系统无法找到模型请求的工具: {tool_call['name']}"}
                
        return {"final_answer": response.content}

    except Exception as e:
        print(f"❌ 执行节点发生致命错误: {e}")
        return {"final_answer": f"系统异常: {e}"}

    
# ==========================================
# 组装极简工作流
# ==========================================
workflow = StateGraph(AgentState)
workflow.add_node("router", router_node)
workflow.add_node("executor", dynamic_executor_node)

workflow.add_edge(START, "router")
workflow.add_edge("router", "executor")
workflow.add_edge("executor", END)

# 编译图
app_graph = workflow.compile()