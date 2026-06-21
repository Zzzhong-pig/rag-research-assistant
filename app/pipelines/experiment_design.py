"""实验设计 Pipeline → 结构化输出"""

from app.agent.prompts import EXPERIMENT_DESIGN_PROMPT
from app.pipelines.base import BasePipeline
from app.utils import parse_llm_json


class ExperimentDesignPipeline(BasePipeline):
    prompt_template = EXPERIMENT_DESIGN_PROMPT
    output_format = "structured"

    def _parse_output(self, content: str) -> dict:
        try:
            structured = parse_llm_json(content)
            lines = [f"**{k}**: {v}" for k, v in structured.items()]
            return {"answer": "\n\n".join(lines), "structured": structured}
        except Exception:
            return {"answer": content, "structured": None}
