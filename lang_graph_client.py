from __future__ import annotations

import os
from typing import TypedDict

from dotenv import load_dotenv
from fastmcp import Client
from langgraph.graph import StateGraph, END


class AppState(TypedDict, total=False):
    query: str
    search_result: str
    clipboard_status: str
    email_status: str


load_dotenv()


async def node_web_search(state: AppState) -> AppState:
    query = state.get("query", "")
    async with Client("server.py") as client:
        result = await client.call_tool("web_search", {"query": query})
    return {"search_result": str(result)}


async def node_write_clipboard(state: AppState) -> AppState:
    text = state.get("search_result", "")
    async with Client("server.py") as client:
        result = await client.call_tool("write_clipboard", {"text": text})
    return {"clipboard_status": str(result)}


async def node_send_email(state: AppState) -> AppState:
    recipient = os.getenv("EMAIL_TO") or os.getenv("GMAIL_USER")
    if not recipient:
        return {"email_status": "❌ Set EMAIL_TO or GMAIL_USER in environment"}

    subject = f"LangGraph Demo: {state.get('query', '')}".strip()
    body = f"Clipboard contents sent via MCP tools and LangGraph.\n\n{state.get('search_result', '')}"

    async with Client("server.py") as client:
        result = await client.call_tool(
            "send_gmail",
            {"to": recipient, "subject": subject or "LangGraph Demo", "body": body},
        )
    return {"email_status": str(result)}


def build_app():
    graph = StateGraph(AppState)
    graph.add_node("web_search", node_web_search)
    graph.add_node("write_clipboard", node_write_clipboard)
    graph.add_node("send_email", node_send_email)

    graph.set_entry_point("web_search")
    graph.add_edge("web_search", "write_clipboard")
    graph.add_edge("write_clipboard", "send_email")
    graph.add_edge("send_email", END)

    return graph.compile()


if __name__ == "__main__":
    import asyncio

    async def main():
        app = build_app()
        final_state = await app.ainvoke({"query": "What is the capital of France?"})
        print("Final state:", final_state)

    asyncio.run(main())


