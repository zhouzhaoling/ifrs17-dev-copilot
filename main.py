import json
from core.graph import app_graph

def run_regression_tests():
    print("==================================================")
    print("🚀 启动 AI 驱动的全量测试集回归（Regression Test）")
    print("==================================================")
    
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
            print(f"       模型输出内容: {result['final_answer'][:50]}...")

    print("\n==================================================")
    print(f"🏁 回归测试完成: {passed}/{total} 通过。")
    print("==================================================")

if __name__ == "__main__":
    run_regression_tests()