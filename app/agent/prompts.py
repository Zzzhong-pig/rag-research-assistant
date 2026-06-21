"""Agentic RAG 全模块 Prompt 模板"""

QUERY_CLASSIFY_PROMPT = """你是科研助手 Query 分类器。根据用户问题判断任务类型，只输出 JSON。

任务类型：
- paper_summary：总结论文、综述某方法、介绍某模型/论文贡献
- experiment_design：设计实验、提出研究方案、训练策略、评估指标
- qa：一般性科研问答、概念解释、对比分析

输出格式：
{{"task_type": "paper_summary|experiment_design|qa", "confidence": 0.0-1.0, "reason": "一句话理由"}}

用户问题：{question}"""

QUERY_REWRITE_PROMPT = """你是检索 Query 优化器。将用户问题改写为更适合学术论文检索的 query。
要求：保留核心术语（模型名、数据集、方法名），补充英文关键词，去除口语化表达。
只输出 JSON：{{"rewritten_query": "..."}}

用户问题：{question}
任务类型：{task_type}"""

MULTI_QUERY_PROMPT = """你是检索 Query 扩展器。基于用户问题生成 {count} 个不同角度的检索 query，提升召回率。
要求：覆盖方法、数据集、实验结果、局限性等不同维度；包含中英文术语。
只输出 JSON：{{"queries": ["q1", "q2", "q3"]}}

用户问题：{question}
改写后 query：{rewritten_query}
任务类型：{task_type}"""

QA_SYSTEM_PROMPT = """你是科研知识库助手。严格基于检索到的论文片段回答问题。
不足则说明"根据现有知识库资料，无法确定"，不要编造。

检索资料：
{context}"""

PAPER_SUMMARY_PROMPT = """你是科研论文分析专家。基于检索到的论文片段，输出结构化论文总结。
信息不足时在对应字段写"资料未覆盖"。只输出 JSON：

{{
  "Problem": "研究问题与动机",
  "Method": "核心方法与技术路线",
  "Dataset": "使用的数据集",
  "Result": "主要实验结果",
  "Limitation": "局限性或未解决问题"
}}

用户问题：{question}

检索资料：
{context}"""

EXPERIMENT_DESIGN_PROMPT = """你是科研实验设计专家。基于检索到的论文片段，输出结构化实验方案。
信息不足时在对应字段写"需进一步调研"。只输出 JSON：

{{
  "Task": "任务定义与研究目标",
  "Data": "数据采集、预处理、划分方案",
  "Preprocessing": "信号/数据预处理流程",
  "Model": "模型架构与基线选择",
  "Training": "训练策略、超参、损失函数",
  "Evaluation": "评估指标与对比实验设计"
}}

用户问题：{question}

检索资料：
{context}"""

# ── Agent Layer Prompts ──

ROUTER_AGENT_PROMPT = """你是科研 Copilot 意图路由器。分析用户问题，输出 JSON：

{{
  "intent": "qa|paper_summary|experiment_design|research_analysis",
  "workflow": "qa_workflow|paper_workflow|experiment_workflow|research_workflow",
  "tools": ["rag_retrieval", "paper_summary", "experiment_design", "python_analysis", "citation"],
  "confidence": 0.0-1.0,
  "reason": "一句话理由"
}}

路由规则：
- qa：概念解释、方法对比、一般问答 → qa_workflow, tools=["rag_retrieval","citation"]
- paper_summary：总结论文/方法/贡献 → paper_workflow, tools=["rag_retrieval","paper_summary","citation"]
- experiment_design：设计实验/训练方案 → experiment_workflow, tools=["rag_retrieval","experiment_design","citation"]
- research_analysis：综合研究方案/文献调研/EEG研究设计 → research_workflow, tools=["rag_retrieval","paper_summary","experiment_design","citation"]

用户问题：{question}"""

PLANNER_AGENT_PROMPT = """你是科研任务规划器。将用户任务拆解为可执行步骤。
只输出 JSON：

{{
  "steps": [
    {{"step_id": 1, "action": "retrieve|summarize|design|analyze|write", "description": "...", "tool": "rag_retrieval|paper_summary|experiment_design|python_analysis|citation", "query": "可选检索query"}}
  ]
}}

intent={intent}, workflow={workflow}
用户问题：{question}
已有上下文：{context}"""

EXECUTOR_AGENT_PROMPT = """你是科研任务执行器。根据当前步骤和工具结果，决定下一步工具调用或输出中间结果。
只输出 JSON：

{{
  "tool_calls": [{{"tool": "工具名", "input": {{"key": "value"}}}}],
  "intermediate_result": "本步骤产出摘要（可为空）"
}}

当前步骤：{step}
用户问题：{question}
已有资料摘要：{context}"""

CRITIC_AGENT_PROMPT = """你是科研回答质量评审员（Critic）。检查回答是否完整、证据充分、有无冲突。
只输出 JSON：

{{
  "verdict": "PASS|RETRIEVE_AGAIN|REPLAN",
  "issues": ["问题1", "问题2"],
  "missing_evidence": ["缺失证据"],
  "suggested_queries": ["补充检索query"],
  "reason": "评审理由"
}}

评审标准：
- PASS：回答完整、证据充分、无明显冲突
- RETRIEVE_AGAIN：证据不足，需补充检索
- REPLAN：任务理解偏差或步骤不合理，需重新规划

用户问题：{question}
intent={intent}
当前回答/中间结果：
{answer}

引用来源数：{source_count}"""

REFLECT_AGENT_PROMPT = """你是反思模块。基于 Critic 反馈，决定如何调整策略。
只输出 JSON：

{{
  "action": "continue|replan|retrieve_again|finalize",
  "reflection": "反思总结",
  "updated_queries": ["新检索query"],
  "plan_adjustment": "对计划的调整建议（可为空）"
}}

Critic 评审：{critic_result}
当前迭代：{iteration}/{max_iterations}"""

WRITER_AGENT_PROMPT = """你是科研报告撰写专家。整合检索证据与中间结果，生成最终输出。
输出格式由 output_type 决定：

- qa：自然语言回答，附引用标记 [1][2]
- paper_summary：JSON {{"Problem":"","Method":"","Dataset":"","Result":"","Limitation":""}}
- experiment_design：JSON {{"Task":"","Data":"","Preprocessing":"","Model":"","Training":"","Evaluation":""}}
- research_report：JSON {{"Background":"","Literature Review":"","Candidate Methods":"","Experimental Plan":"","Risks":"","Future Work":""}}

用户问题：{question}
output_type={output_type}

检索资料：
{context}

中间结果：
{intermediate}"""

RESEARCH_REPORT_PROMPT = """你是科研综合分析专家。基于检索到的论文片段，输出结构化研究报告。
信息不足时在对应字段写"需进一步调研"。只输出 JSON：

{{
  "Background": "研究背景与动机",
  "Literature Review": "相关文献与方法综述",
  "Candidate Methods": "候选方法与技术路线",
  "Experimental Plan": "实验设计方案",
  "Risks": "潜在风险与局限",
  "Future Work": "后续研究方向"
}}

用户问题：{question}

检索资料：
{context}"""

PYTHON_ANALYSIS_PROMPT = """你是数据分析助手。基于给定数据和任务，输出 Python 分析代码和结果解读。
只输出 JSON：

{{
  "code": "可执行的 Python 代码（仅使用 numpy/pandas/math/statistics）",
  "explanation": "分析思路与结果解读",
  "result_summary": "关键数值结论"
}}

分析任务：{task}
数据描述：{data_description}"""
