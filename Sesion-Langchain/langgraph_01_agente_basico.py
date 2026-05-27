"""LangGraph version of the basic agent for Studio visualization."""

import os
import operator
from typing import Annotated, Literal, TypedDict

from dotenv import load_dotenv
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

load_dotenv()


def crear_modelo_chat() -> ChatOpenAI:
    """Create the chat model used by the agent."""

    return ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0,
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
    )


llm = crear_modelo_chat()


@tool
def calcular_precio(cantidad: float, precio_unitario: float) -> str:
    """Calculate the total price of an order."""

    total = cantidad * precio_unitario
    return f"El precio total es: {total:.2f} EUR"


@tool
def celsius_to_fahrenheit(celsius: float) -> str:
    """Convert Celsius values to Fahrenheit."""

    fahrenheit = (celsius * 9 / 5) + 32
    return f"{celsius}°C son {fahrenheit:.2f}°F"


@tool
def resumir_texto(texto: str) -> str:
    """Summarize the provided text."""

    resumen_llm = crear_modelo_chat()
    respuesta = resumen_llm.invoke(
        f"Resume el siguiente texto en 2-3 oraciones:\n\n{texto}"
    )
    return respuesta.content


tools = [
    DuckDuckGoSearchRun(),
    calcular_precio,
    celsius_to_fahrenheit,
    resumir_texto,
]
tools_by_name = {tool_item.name: tool_item for tool_item in tools}
llm_with_tools = llm.bind_tools(tools)
system_prompt = (
    "Eres un asistente útil. Responde en español y usa herramientas cuando "
    "sea necesario."
)


class MessagesState(TypedDict):
    """State container for the agent messages."""

    messages: Annotated[list[AnyMessage], operator.add]


def llm_call(state: MessagesState) -> dict[str, list[AnyMessage]]:
    """Generate the next assistant message."""

    return {
        "messages": [
            llm_with_tools.invoke(
                [SystemMessage(content=system_prompt)] + state["messages"]
            )
        ]
    }


def tool_node(state: MessagesState) -> dict[str, list[ToolMessage]]:
    """Execute every tool requested by the model."""

    results: list[ToolMessage] = []
    last_message = state["messages"][-1]

    for tool_call in last_message.tool_calls:
        herramienta = tools_by_name[tool_call["name"]]
        observation = herramienta.invoke(tool_call["args"])
        results.append(
            ToolMessage(content=observation, tool_call_id=tool_call["id"])
        )

    return {"messages": results}


def should_continue(state: MessagesState) -> Literal["tool_node", END]:
    """Route to the tool node when the model asks for a tool."""

    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tool_node"

    return END


agent_builder = StateGraph(MessagesState)
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    ["tool_node", END],
)
agent_builder.add_edge("tool_node", "llm_call")

agent = agent_builder.compile()


if __name__ == "__main__":
    sample_query = (
        "Busca el precio del oro hoy y calcula cuánto cuestan 5 onzas"
    )
    resultado = agent.invoke(
        {
            "messages": [
                HumanMessage(content=sample_query)
            ]
        }
    )
    print(resultado["messages"][-1].content)