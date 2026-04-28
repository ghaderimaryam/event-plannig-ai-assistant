"""Builds the RAG chain that powers the chat UI."""
from __future__ import annotations

from langchain_chroma import Chroma
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from src.config import MODEL_GEN, TOP_K

SOURCES_MARKER = "\n\n📎 **Sources:**"
def _content_to_text(content) -> str:
    """Normalize Gradio message content into plain text.

    Gradio 6 may pass content as a string, a {"path": str} dict, or a list of
    content blocks like [{"type": "text", "text": "..."}]. We only need text.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "\n".join(parts)
    if isinstance(content, dict):
        return content.get("text", "")
    return str(content)

RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a helpful vendor recommendation assistant for event planning.
Use the following retrieved context from our vendor knowledge base to answer the user's question.
If you don't know the answer or the context doesn't contain relevant information, say so honestly.
Always mention specific vendor names, prices, ratings, and other details when available.
Context:
{context}""",
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ]
)


def _format_docs(docs) -> str:
    return "\n\n".join(d.page_content for d in docs)


def build_chat_fn(vectorstore: Chroma, k: int = TOP_K, temperature: float = 0.3):
    """Return a Gradio-compatible `(message, history) -> str` callable.

    History is owned by Gradio (no globals); we translate it to LangChain messages
    on each turn and strip the appended sources footer so the LLM sees clean text.
    """
    retriever = vectorstore.as_retriever(
        search_type="similarity", search_kwargs={"k": k}
    )
    llm = ChatOpenAI(model=MODEL_GEN, temperature=temperature)
    chain = RAG_PROMPT | llm | StrOutputParser()

    def chat_fn(user_message: str, history: list[dict]) -> str:
        lc_history = []
        for msg in history or []:
            text = _content_to_text(msg.get("content", "")).split(SOURCES_MARKER)[0]
            if msg["role"] == "user":
                lc_history.append(HumanMessage(content=text))
            elif msg["role"] == "assistant":
                lc_history.append(AIMessage(content=text))

        docs = retriever.invoke(user_message)
        answer = chain.invoke(
            {
                "context": _format_docs(docs),
                "chat_history": lc_history,
                "question": user_message,
            }
        )

        return answer

    return chat_fn
