"""命令行单次问答"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag_chain import ask


def main():
    if len(sys.argv) < 2:
        print('用法: python scripts/cli_query.py "你的问题"')
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    result = ask(question)

    print(f"\n问题: {question}")
    print(f"\n回答:\n{result['answer']}")
    print(f"\n引用来源 ({len(result['sources'])} 条):")
    for i, src in enumerate(result["sources"], 1):
        print(f"  [{i}] {src['source']} (p.{src['page']})")


if __name__ == "__main__":
    main()
