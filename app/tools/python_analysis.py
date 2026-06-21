"""Tool 4: Python Analysis（受限沙箱）"""

import math
import statistics
from typing import Any

from app.agent.prompts import PYTHON_ANALYSIS_PROMPT
from app.llm import get_llm
from app.tools.base import BaseTool
from app.utils import parse_llm_json

_SAFE_BUILTINS = {
    "abs": abs,
    "min": min,
    "max": max,
    "sum": sum,
    "len": len,
    "round": round,
    "range": range,
    "sorted": sorted,
    "enumerate": enumerate,
    "zip": zip,
    "float": float,
    "int": int,
    "str": str,
    "list": list,
    "dict": dict,
    "print": print,
}


class PythonAnalysisTool(BaseTool):
    name = "python_analysis"
    description = "执行受限 Python 数据分析（numpy/pandas/math/statistics）"

    def run(self, task: str, data: dict | list | None = None, data_description: str = "", **_) -> dict:
        llm = get_llm()
        desc = data_description or str(data)[:500] if data else "无额外数据"
        try:
            resp = llm.invoke(PYTHON_ANALYSIS_PROMPT.format(task=task, data_description=desc))
            parsed = parse_llm_json(resp.content)
        except Exception as e:
            return {"success": False, "error": f"分析规划失败: {e}"}

        code = parsed.get("code", "")
        exec_result = self._safe_exec(code, data)
        return {
            "code": code,
            "explanation": parsed.get("explanation", ""),
            "result_summary": parsed.get("result_summary", ""),
            "exec_output": exec_result,
        }

    def _safe_exec(self, code: str, data: Any) -> str:
        if not code.strip():
            return "无代码执行"
        try:
            import numpy as np
            import pandas as pd
        except ImportError:
            np = None  # type: ignore
            pd = None  # type: ignore

        namespace: dict[str, Any] = {
            "__builtins__": _SAFE_BUILTINS,
            "math": math,
            "statistics": statistics,
            "data": data,
        }
        if np is not None:
            namespace["np"] = np
        if pd is not None:
            namespace["pd"] = pd

        output_lines: list[str] = []

        def _capture_print(*args, **kwargs):
            output_lines.append(" ".join(str(a) for a in args))

        namespace["print"] = _capture_print

        try:
            exec(code, namespace)  # noqa: S102
            result = namespace.get("result")
            if result is not None:
                output_lines.append(f"result = {result}")
            return "\n".join(output_lines) or "执行完成，无输出"
        except Exception as e:
            return f"执行错误: {e}"
