"""Streamlit 前端 — Agentic RAG Research Copilot"""

import uuid

import streamlit as st

from app.orchestrator import ask

st.set_page_config(
    page_title="Agentic RAG Research Copilot",
    page_icon="🧠",
    layout="wide",
)

TASK_LABELS = {
    "qa": "💬 科研问答",
    "paper_summary": "📄 论文总结",
    "experiment_design": "🔬 实验设计",
    "research_analysis": "🔍 综合研究",
}

WORKFLOW_LABELS = {
    "qa_workflow": "QA Workflow",
    "paper_workflow": "Paper Workflow",
    "experiment_workflow": "Experiment Workflow",
    "research_workflow": "Research Workflow",
}

st.title("🧠 Agentic RAG Research Copilot")
st.caption(
    "Router · Planner · Executor · Critic · Writer · Reflection Loop · Hybrid RAG"
)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Copilot 状态")
    st.text(f"Session: {st.session_state.session_id[:8]}...")
    st.markdown("**支持意图**")
    for k, v in TASK_LABELS.items():
        st.markdown(f"- {v}")
    if st.button("新会话"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("task_type"):
            st.caption(TASK_LABELS.get(msg["task_type"], msg["task_type"]))
        st.markdown(msg["content"])
        if msg.get("meta"):
            with st.expander("Agent 决策链路"):
                st.json(msg["meta"])
        if msg.get("sources"):
            with st.expander("引用来源"):
                for i, src in enumerate(msg["sources"], 1):
                    st.markdown(f"**[{i}]** {src['source']} (p.{src['page']})")
                    st.text(src["content"])

if question := st.chat_input("输入科研问题（问答 / 论文总结 / 实验设计 / 综合研究）..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Copilot 处理中：Router → Plan → Execute → Critic → Reflect → Write..."):
            try:
                result = ask(question, session_id=st.session_state.session_id)
                label = TASK_LABELS.get(result["intent"], result["intent"])
                wf = WORKFLOW_LABELS.get(result["workflow"], result["workflow"])
                st.caption(
                    f"{label} | {wf} | 迭代 {result['iterations']} 轮 | "
                    f"工具: {', '.join(result.get('tools', []))}"
                )
                st.markdown(result["answer"])
                meta = {
                    "intent": result["intent"],
                    "workflow": result["workflow"],
                    "confidence": result["confidence"],
                    "iterations": result["iterations"],
                    "plan_steps": result.get("plan_steps", []),
                    "critic_final": result.get("critic_final"),
                    "trace": result.get("trace", []),
                    "retrieval_count": result.get("retrieval_count"),
                    "final_count": result.get("final_count"),
                }
                with st.expander("Agent 决策链路"):
                    st.json(meta)
                if result.get("evaluation") and result["evaluation"].get("enabled"):
                    with st.expander("RAGAS 评估"):
                        st.json(result["evaluation"])
                if result["sources"]:
                    with st.expander("引用来源"):
                        for i, src in enumerate(result["sources"], 1):
                            st.markdown(f"**[{i}]** {src['source']} (p.{src['page']})")
                            st.text(src["content"])
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": result["answer"],
                        "task_type": result["intent"],
                        "sources": result["sources"],
                        "meta": meta,
                    }
                )
            except Exception as e:
                st.error(f"出错了：{e}")
