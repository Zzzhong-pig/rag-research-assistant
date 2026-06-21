"""通用工具函数"""

import json
import re
from pathlib import Path


def parse_llm_json(text: str) -> dict | list:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    return json.loads(text)


def format_sources(docs: list, max_len: int = 200) -> list[dict]:
    sources = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        sources.append(
            {
                "content": doc.page_content[:max_len] + ("..." if len(doc.page_content) > max_len else ""),
                "source": str(Path(source).name) if source != "unknown" else source,
                "page": doc.metadata.get("page", "N/A"),
            }
        )
    return sources
