import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.tools import tool

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0,
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
)

@tool
def calcular_precio(cantidad: float, precio_unitario: float) -> str:
    """Calcula el precio total de un pedido."""
    total = cantidad * precio_unitario
    return f"El precio total es: {total:.2f} EUR"

tools = [DuckDuckGoSearchRun(), calcular_precio]

checkpointer = InMemorySaver()

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="Eres un asistente financiero experto. Responde siempre en español.",
    checkpointer=checkpointer,
)

chain_prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente financiero experto. Responde siempre en español."),
    ("human", "Pregunta: {pregunta}\n\nContexto web: {contexto}"),
])

config = {"configurable": {"thread_id": "demo-memoria"}}

# Ejemplo con LCEL
def buscar_docs(pregunta):
    search = DuckDuckGoSearchRun()
    return search.run(pregunta)

chain_completa = (
    RunnablePassthrough.assign(contexto=lambda x: buscar_docs(x["pregunta"]))
    | chain_prompt
    | llm
    | StrOutputParser()
)

if __name__ == "__main__":
    resultado = agent.invoke(
        config,
    )
    print(resultado["messages"][-1].content)

    resultado = agent.invoke(
        {"messages": [{"role": "user", "content": "¿Cómo me llamo?"}]},
        config,
    )
    print(resultado["messages"][-1].content)

    # Streaming con LCEL
    print("\n--- Streaming con LCEL ---")
    for chunk in chain_completa.stream({"pregunta": "Explica los mercados financieros"}):
        print(chunk, end="", flush=True)

        {"messages": [{"role": "user", "content": "Mi nombre es Ana. Recuérdalo."}]},