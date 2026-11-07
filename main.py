import json
import os
from core.graph import app_graph, llm

def run_regression_tests():
    print("==================================================")
    print("🚀 启动 AI 驱动的全量测试集回归（Regression Test）")
    print("==================================================")
    
    # 确保 memory 文件夹存在
    os.makedirs("memory", exist_ok=True)
    mem_path = "memory/reflection.json"
    if not os.path.exists(mem_path):
        with open(mem_path, "w", encoding="utf-8") as f:
            json.dump([], f)

    # 读取测试集
    with open("tests/regression_set.json", "r", encoding="utf-8") as f:
        tests = json.load(f)

    passed = 0
    total = len(tests)

    for test in tests:
        print(f"\n[TestCase {test['id']}] 用户输入: {test['input']}")
        
        # 执行图
        init_state = {"user_query": test["input"]}
        result = app_graph.invoke(init_state)
        
        selected = result["selected_skill"]
        expected = test["expected_skill"]
        
        if selected == expected:
            print(f"✅ [PASS] 预期: {expected} | 实际: {selected}")
            passed += 1
        else:
            print(f"❌ [FAIL] 预期: {expected} | 实际: {selected}")
            
            # 👇 AI 反思机制
            print("🤖 [AI Loop] 触发反思，正在沉淀避坑规则...")
            reflection_prompt = f"""
            测试用例输入: {test['input']}
            预期路由: {expected}
            实际路由: {selected}
            大模型给出的回答: {result['final_answer']}
            
            请分析为什么路由错了，并总结出一条简短的【避坑规则】。
            只需输出规则本身，格式如：“当用户提到XXX时，务必路由到XXX”。
            """
            
            rule = llm.invoke(reflection_prompt).content.strip()
            
            rules = []
            if os.path.exists(mem_path):
                with open(mem_path, "r", encoding="utf-8") as f:
                    rules = json.load(f)
            
            if rule not in rules:
                rules.append(rule)
                with open(mem_path, "w", encoding="utf-8") as f:
                    json.dump(rules, f, ensure_ascii=False, indent=2)
                print(f"✅ 新规则已沉淀: {rule}")
            else:
                print(f"ℹ️ 规则已存在，跳过沉淀。")

    print("\n==================================================")
    print(f"🏁 回归测试完成: {passed}/{total} 通过。")
    print("==================================================")


def manual_evolution_test():
    print("\n" + "="*50)
    print("🩺 启动手动进化模拟：模拟一次业务专家的纠错 (Human Feedback)")
    print("="*50)

    # 1. 模拟一次真实的业务场景：大模型因为不懂黑话，路由错了
    user_query = "老张说北京账套和平账打架了，帮我拉出来看看"
    
    # 假设大模型这次抽风了，把它交给了单点查数
    wrong_skill = "smart_query" 
    correct_skill = "diff_analysis"
    
    print(f"👨‍💻 业务专家输入: {user_query}")
    print(f"❌ 系统错误路由到了: {wrong_skill} (这本该是一次差异排查)")
    print(f"✅ 专家纠正路由为: {correct_skill}")

    # 2. 触发 AI Reflection
    print("\n🤖 [AI Loop] 正在分析专家反馈，提取避坑规则...")
    
    reflection_prompt = f"""
    业务场景：用户输入 '{user_query}'
    系统错误地使用了 {wrong_skill}，但专家指出应该使用 {correct_skill}。
    请总结出一条简短的【避坑规则】，格式为：“当用户提到XXX时，务必路由到XXX”。
    只输出规则本身，不要标点。
    """
    
    rule = llm.invoke(reflection_prompt).content.strip()
    print(f"✅ 反思成功，提取出新规则: 「{rule}」")

    # 3. 将规则写入记忆
    mem_path = "memory/reflection.json"
    rules = []
    if os.path.exists(mem_path):
        with open(mem_path, "r", encoding="utf-8") as f:
            rules = json.load(f)
    
    # 防止重复添加
    if rule not in rules:
        rules.append(rule)
        with open(mem_path, "w", encoding="utf-8") as f:
            json.dump(rules, f, ensure_ascii=False, indent=2)
        print("💾 规则已成功沉淀至本地记忆库 memory/reflection.json！")
    else:
        print("ℹ️ 该规则已存在于记忆库中。")

    print("\n✨ 进化完成！下一次即使模型再犯傻，Router 也会因为读取了这条记忆，而强制纠正它的路由！")
    print("="*50 + "\n")


if __name__ == "__main__":
    # 1. 先跑一遍回归测试，证明当前系统是健康的
    run_regression_tests()
    
    # 2. 演示一次人工反馈是如何让系统进化的
    manual_evolution_test()