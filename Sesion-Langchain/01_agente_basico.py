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

@tool
def celsius_to_fahrenheit(celsius: float) -> str:
    """Convierte temperaturas de Celsius a Fahrenheit."""
    fahrenheit = (celsius * 9/5) + 32
    return f"{celsius}°C son {fahrenheit:.2f}°F"

@tool
def resumir_texto(texto: str) -> str:
    """Genera un resumen del texto proporcionado."""
    resumen_llm = ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0,
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
    )
    respuesta = resumen_llm.invoke(f"Resume el siguiente texto en 2-3 oraciones:\n\n{texto}")
    return respuesta.content

tools = [DuckDuckGoSearchRun(), calcular_precio, celsius_to_fahrenheit, resumir_texto]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="Eres un asistente útil. Responde en español y usa herramientas cuando sea necesario.",
)

resultado = agent.invoke({
    "messages": [
        {"role": "user", "content": "Busca el precio del oro hoy y calcula cuánto cuestan 5 onzas"}
    ]
})
print(resultado["messages"][-1].content)
