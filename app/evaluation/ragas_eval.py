"""RAGAS 评估层"""

from app.config import ENABLE_RAGAS
from app.logging_config import setup_logging

logger = setup_logging("copilot.evaluation")


def _get_ragas_llm():
    """RAGAS 内部 metric 需要 LLM，复用项目豆包配置"""
    from langchain_openai import ChatOpenAI
    from ragas.llms import LangchainLLMWrapper

    from app.config import DOUBAO_API_KEY, DOUBAO_BASE_URL, DOUBAO_MODEL
    from app.llm import get_llm

    try:
        llm = get_llm()
    except ValueError:
        llm = ChatOpenAI(
            model=DOUBAO_MODEL,
            api_key=DOUBAO_API_KEY,
            base_url=DOUBAO_BASE_URL,
            temperature=0,
        )
    return LangchainLLMWrapper(llm)


def _get_ragas_embeddings():
    """RAGAS answer_relevancy 等指标需要 Embedding"""
    from ragas.embeddings import LangchainEmbeddingsWrapper

    from app.llm import get_embeddings

    return LangchainEmbeddingsWrapper(get_embeddings())


def evaluate_response(question: str, response: dict, ground_truth: str | None = None) -> dict:
    """使用 RAGAS 评估回答质量（可选启用）"""
    if not ENABLE_RAGAS:
        return {"enabled": False}

    try:
        from datasets import Dataset
        from ragas import evaluate
        from ragas.metrics import answer_relevancy, context_precision, faithfulness
    except ImportError as e:
        logger.warning("RAGAS not installed: %s", e)
        return {"enabled": False, "error": "ragas not installed"}

    contexts = [s.get("content", "") for s in response.get("sources", [])]
    if not contexts:
        return {
            "enabled": True,
            "skipped": True,
            "reason": "no contexts for evaluation",
            "faithfulness": None,
            "answer_relevancy": None,
            "context_precision": None,
        }

    data = {
        "question": [question],
        "answer": [response.get("answer", "")],
        "contexts": [contexts],
    }
    metrics = [faithfulness, answer_relevancy]

    if ground_truth:
        data["reference"] = [ground_truth]
        metrics.append(context_precision)

    dataset = Dataset.from_dict(data)

    try:
        ragas_llm = _get_ragas_llm()
        ragas_embeddings = _get_ragas_embeddings()
        result = evaluate(
            dataset,
            metrics=metrics,
            llm=ragas_llm,
            embeddings=ragas_embeddings,
        )
        scores = result.to_pandas().iloc[0].to_dict()
        return {
            "enabled": True,
            "faithfulness": _safe_float(scores.get("faithfulness")),
            "answer_relevancy": _safe_float(scores.get("answer_relevancy")),
            "context_precision": _safe_float(scores.get("context_precision")),
            "hallucination_risk": _hallucination_risk(scores.get("faithfulness")),
        }
    except Exception as e:
        logger.error("RAGAS evaluation failed: %s", e)
        return {"enabled": True, "error": str(e)}


def _safe_float(val) -> float | None:
    try:
        return round(float(val), 4) if val is not None else None
    except (TypeError, ValueError):
        return None


def _hallucination_risk(faithfulness) -> str:
    f = _safe_float(faithfulness)
    if f is None:
        return "unknown"
    if f >= 0.8:
        return "low"
    if f >= 0.5:
        return "medium"
    return "high"
