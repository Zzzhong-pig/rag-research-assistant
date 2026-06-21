"""通用问答 Pipeline"""

from langchain_core.prompts import ChatPromptTemplate

from app.agent.prompts import QA_SYSTEM_PROMPT
from app.llm import get_llm
from app.pipelines.base import BasePipeline


class QAPipeline(BasePipeline):
    def run(self, question: str, docs):
        llm = get_llm()
        context = self._build_context(docs)
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", QA_SYSTEM_PROMPT.format(context=context)),
                ("human", "{question}"),
            ]
        )
        chain = prompt | llm
        resp = chain.invoke({"question": question})
        return {"answer": resp.content, "structured": None}
