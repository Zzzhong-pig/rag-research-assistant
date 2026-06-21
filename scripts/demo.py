"""Agentic RAG Research Copilot 端到端演示"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import ENABLE_RAGAS
from app.orchestrator import ask

DEMO_QUESTIONS = [
    ("qa", "CBraMod foundation model如何对EEG信号进行建模？"),
    ("paper_summary", "总结EEG-Deformer论文的核心方法和贡献"),
    ("experiment_design", "设计一个基于EEG的运动想象BCI分类实验方案"),
    ("research_analysis", "帮我设计一个EEG情绪识别研究方案"),
]


def main():
    print("=" * 60)
    print("Agentic RAG Research Copilot — 端到端演示")
    print(f"RAGAS 评估: {'已启用' if ENABLE_RAGAS else '未启用（.env 设置 ENABLE_RAGAS=true 开启）'}")
    print("=" * 60)

    passed = 0
    for expected_intent, question in DEMO_QUESTIONS:
        print(f"\n[Q] {question}")
        print("-" * 40)
        try:
            result = ask(question, session_id="demo-e2e")
            intent_ok = result["intent"] == expected_intent
            status = "[OK]" if intent_ok else "[FAIL]"
            if intent_ok:
                passed += 1

            print(f"{status} Intent: {result['intent']} (expected: {expected_intent})")
            print(f"  Workflow: {result['workflow']}")
            print(f"  Tools: {', '.join(result.get('tools', []))}")
            print(f"  Iterations: {result.get('iterations', 1)}")
            print(f"  Confidence: {result.get('confidence', 0):.2f}")
            print(f"  Rewritten: {result.get('rewritten_query', '')}")
            print(f"  Queries: {result.get('queries', [])}")
            print(f"  Sources: {len(result.get('sources', []))} 条")
            critic = result.get("critic_final", {})
            if critic:
                print(f"  Critic: {critic.get('verdict', 'N/A')}")
            print(f"  Answer: {result['answer'][:300]}...")

            if result.get("structured"):
                print(f"  Structured keys: {list(result['structured'].keys())}")

            ev = result.get("evaluation")
            if ev and ev.get("enabled"):
                print(
                    f"  RAGAS: faithfulness={ev.get('faithfulness')} "
                    f"relevancy={ev.get('answer_relevancy')} "
                    f"precision={ev.get('context_precision')} "
                    f"risk={ev.get('hallucination_risk')}"
                )
            elif ENABLE_RAGAS:
                print(f"  RAGAS: {ev}")

        except Exception as e:
            print(f"{status} 失败: {e}")

    print("\n" + "=" * 60)
    print(f"演示完成！意图路由正确: {passed}/{len(DEMO_QUESTIONS)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
