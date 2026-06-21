"""论文总结 Pipeline → 结构化输出"""

from app.agent.prompts import PAPER_SUMMARY_PROMPT
from app.pipelines.base import BasePipeline
from app.utils import parse_llm_json


class PaperSummaryPipeline(BasePipeline):
    prompt_template = PAPER_SUMMARY_PROMPT
    output_format = "structured"

    def _parse_output(self, content: str) -> dict:
        try:
            structured = parse_llm_json(content)
            lines = [f"**{k}**: {v}" for k, v in structured.items()]
            return {"answer": "\n\n".join(lines), "structured": structured}
        except Exception:
            return {"answer": content, "structured": None}
