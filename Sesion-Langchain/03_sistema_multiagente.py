import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_community.tools import DuckDuckGoSearchRun
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

# --- AGENTE INVESTIGADOR ---
investigador = create_agent(
    model=llm,
    tools=[DuckDuckGoSearchRun()],
    system_prompt="Eres un investigador experto. Busca información precisa y actualizada.",
)


@tool
def investigar(pregunta: str) -> str:
    """Investiga un tema en internet. Input: pregunta de investigación."""
    resultado = investigador.invoke({
        "messages": [{"role": "user", "content": pregunta}]
    })
    return resultado["messages"][-1].content


# --- AGENTE ANALISTA ---
analista = create_agent(
    model=llm,
    tools=[calcular_precio],
    system_prompt="Eres un analista de datos. Extrae insights clave de la información.",
)


@tool
def analizar(datos: str) -> str:
    """Analiza datos o información. Input: datos a analizar."""
    resultado = analista.invoke({
        "messages": [{"role": "user", "content": datos}]
    })
    return resultado["messages"][-1].content


# --- AGENTE SUPERVISOR ---
supervisor = create_agent(
    model=llm,
    tools=[investigar, analizar],
    system_prompt=(
        "Eres el supervisor de un equipo de investigación. "
        "Tienes acceso a: investigar (búsqueda web) y analizar (análisis de datos). "
        "Coordina el equipo para producir informes completos."
    ),
)

if __name__ == "__main__":
    resultado = supervisor.invoke({
        "messages": [{"role": "user", "content": "Analiza el mercado de energías renovables en Europa en 2024"}]
    })
    print(resultado["messages"][-1].content)
