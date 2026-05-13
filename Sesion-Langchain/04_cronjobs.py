import os
import logging
import schedule
import time
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import tool

load_dotenv()

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/agentes_autonomos.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("agentes_autonomos")

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
        "messages": [
            {"role": "system", "content": "Eres un investigador experto. Busca información precisa y actualizada."},
            {"role": "user", "content": pregunta}]
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
        "messages": [
            {"role": "system", "content": "Eres un analista de datos. Extrae insights clave de la información."},
            {"role": "user", "content": datos}
        ]
    })
    return resultado["messages"][-1].content


supervisor = create_agent(
    model=llm,
    tools=[investigar, analizar],
    system_prompt=(
        "Eres el supervisor de un equipo de investigación. "
        "Tienes acceso a: investigar (búsqueda web) y analizar (análisis de datos). "
        "Coordina el equipo para producir informes completos."
    ),
)


def ejecutar_agente_diario():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logger.info("[%s] Iniciando agente de informes", timestamp)
    try:
        resultado = supervisor.invoke({
            "messages": [
                {"role": "system", "content": "Eres el supervisor de un equipo de investigación. Tienes acceso a: investigar (búsqueda web) y analizar (análisis de datos). Coordina el equipo para producir informes completos."},
                {"role": "user", "content": "Genera un resumen del mercado tecnológico de hoy"}
            ]
        })
        os.makedirs("informes", exist_ok=True)
        with open(f"informes/informe_{datetime.now().date()}.txt", "w") as f:
            f.write(resultado["messages"][-1].content)
        logger.info("[%s] Informe generado correctamente", datetime.now())
    except Exception as e:
        logger.exception("[%s] Error generando el informe", timestamp)


def ejecutar_monitoreo():
    """Agente de monitoreo cada 30 minutos."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logger.info("[%s] Monitoreando noticias de IA", timestamp)
    try:
        resultado = investigador.invoke({
            "messages": [
                {"role": "system", "content": "Eres un investigador experto. Busca información precisa y actualizada."},
                {"role": "user", "content": "Últimas noticias sobre IA"}
            ]
        })
        logger.info("Monitoreo: %s", resultado["messages"][-1].content[:200])
    except Exception as e:
        logger.exception("Error en monitoreo")


def main():
    """Configura el sistema de automatización y mantiene activos los trabajos programados.

    El proceso deja definidos tres tipos de ejecución recurrente:
    - un informe diario a las 08:00,
    - un monitoreo periódico cada 30 minutos,
    - y un informe semanal los lunes a las 09:00.

    Mientras el programa está en ejecución, el bucle principal revisa el calendario
    y dispara cada tarea cuando corresponde.
    """
    """    logger.info("Sistema de agentes autónomos activo...")
        logger.info("Tareas programadas:")
        logger.info("  - Informe diario a las 08:00")
        logger.info("  - Monitoreo cada 30 minutos")
        logger.info("  - Informe semanal los lunes a las 09:00")

        schedule.every().day.at("08:00").do(ejecutar_agente_diario)
        schedule.every(30).minutes.do(ejecutar_monitoreo)
        schedule.every().monday.at("09:00").do(ejecutar_agente_diario)

        while True:
            schedule.run_pending()
            time.sleep(60)
    """
    ejecutar_agente_diario()

if __name__ == "__main__":
    main()
