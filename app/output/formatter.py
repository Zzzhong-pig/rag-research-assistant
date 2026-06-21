"""结构化输出格式化"""

PAPER_SUMMARY_FIELDS = ["Problem", "Method", "Dataset", "Result", "Limitation"]
EXPERIMENT_FIELDS = ["Task", "Data", "Preprocessing", "Model", "Training", "Evaluation"]
RESEARCH_REPORT_FIELDS = [
    "Background",
    "Literature Review",
    "Candidate Methods",
    "Experimental Plan",
    "Risks",
    "Future Work",
]


def format_structured(task_type: str, structured: dict | None) -> str:
    if not structured:
        return ""

    if task_type == "paper_summary":
        fields = PAPER_SUMMARY_FIELDS
    elif task_type == "experiment_design":
        fields = EXPERIMENT_FIELDS
    elif task_type == "research_analysis":
        fields = RESEARCH_REPORT_FIELDS
    else:
        return ""

    lines = []
    for field in fields:
        if field in structured:
            lines.append(f"### {field}\n{structured[field]}")
    return "\n\n".join(lines)
