<table bgcolor="#ffffff" width="100%" style="width: 100%; border-collapse: collapse; border: 1px solid #d0d0d0; background-color: #ffffff !important; font-family: Arial, sans-serif; opacity: 1 !important;">
  <tr bgcolor="#ffffff" style="background-color: #ffffff !important;">
    <td align="center" bgcolor="#ffffff" style="padding: 25px; vertical-align: middle; background-color: #ffffff !important;">
      <div style="background-color: #ffffff !important; padding: 10px;">
        <img src="https://talentodigitalextremadura.com/wp-content/uploads/2025/05/junta-ext-transforma2.png" height="140" style="height: 140px; width: auto; display: inline-block; background-color: #ffffff !important;">
      </div>
      <hr style="border: 0; border-top: 1px solid #dddddd; width: 85%; margin: 20px auto;">
      <table width="100%" bgcolor="#ffffff" style="width: 100%; border-collapse: collapse; background-color: #ffffff !important;">
        <tr bgcolor="#ffffff" style="background-color: #ffffff !important;">
          <td align="center" width="33.3%" bgcolor="#ffffff" style="padding: 10px; background-color: #ffffff !important; border: none;">
            <img src="https://talentodigitalextremadura.com/wp-content/uploads/2024/10/Grafismo-UEx-Color-3.png" height="110" style="height: 110px; width: auto; background-color: #ffffff !important;">
          </td>
          <td align="center" width="33.3%" bgcolor="#ffffff" style="padding: 10px; background-color: #ffffff !important; border: none;">
            <img src="https://talentodigitalextremadura.com/wp-content/uploads/2026/01/logointia.png" height="110" style="height: 110px; width: auto; background-color: #ffffff !important;">
          </td>
          <td align="center" width="33.3%" bgcolor="#ffffff" style="padding: 10px; background-color: #ffffff !important; border: none;">
            <img src="https://talentodigitalextremadura.com/wp-content/uploads/2024/10/Group-59651.png" height="110" style="height: 110px; width: auto; background-color: #ffffff !important;">
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>

# Construcción de Agentes Autónomos

Este proyecto reúne cuatro ejemplos progresivos para aprender a construir agentes con LangChain en Python. La idea es ir desde un agente básico hasta un sistema con automatización programada que ejecuta tareas por sí solo.

## Qué es un sistema de agentes autónomos

Un sistema de agentes autónomos es una arquitectura en la que uno o varios agentes pueden:

- entender una tarea en lenguaje natural,
- decidir qué herramientas usar,
- encadenar pasos para resolver un objetivo,
- mantener memoria o estado cuando hace falta,
- y ejecutar acciones de forma repetida o programada sin intervención manual constante.

En este repositorio, la autonomía se construye de forma incremental: primero un agente simple, luego memoria de conversación, después coordinación entre agentes, y finalmente automatización con tareas programadas.

## Requisitos

- Python 3.13 o compatible con el entorno del proyecto.
- Una clave de `OPENROUTER_API_KEY` en tu entorno.
- Dependencias instaladas desde `requirements.txt`.

Si aún no las tienes instaladas:

```bash
uv pip install -r requirements.txt
```

## Estructura de los ejemplos

### 1. `01_agente_basico.py`

Este ejemplo muestra la base mínima de un agente.

- Configura un modelo `ChatOpenAI` apuntando a OpenRouter.
- Expone herramientas sencillas como cálculo de precio, conversión de temperatura, resumen de texto y búsqueda web.
- Usa `create_agent`, que es el patrón actual de LangChain v1.

Sirve para entender cómo un agente decide cuándo llamar herramientas y cómo devolver una respuesta final.

### 2. `02_agente_memoria.py`

Este ejemplo añade memoria de conversación.

- Usa `InMemorySaver` como checkpointer.
- Mantiene la conversación entre invocaciones con un mismo `thread_id`.
- Demuestra cómo el agente recuerda información previa, por ejemplo el nombre de la persona.
- Incluye una cadena LCEL adicional para buscar contexto en la web y generar una respuesta con ese contexto.

La idea central es que el agente ya no responde como una sola consulta aislada, sino como una conversación con estado.

### 3. `03_sistema_multiagente.py`

Este ejemplo muestra coordinación entre agentes.

- Hay un agente investigador que busca información.
- Hay un agente analista que trabaja con datos y cálculos.
- Hay un supervisor que usa a los otros dos como herramientas.

Este patrón sirve cuando quieres dividir responsabilidades: un agente encuentra información, otro la procesa y un supervisor organiza el resultado final.

### 4. `04_cronjobs.py`

Este es el ejemplo más cercano a un sistema de agentes autónomos en producción.

- Reutiliza el patrón multiagente del ejemplo 3.
- Ejecuta el agente diario como una tarea automatizable.
- Sirve como base para integrarlo con un cronjob del sistema operativo.

Aquí está la parte importante de la automatización: el sistema no espera a que un usuario lo invoque manualmente, sino que puede ser disparado por un programador de tareas del sistema. Esa es la diferencia entre un demo interactivo y un sistema autónomo operativo.

En términos prácticos, este archivo representa una capa de orquestación:

- recoge eventos del tiempo,
- dispara un agente,
- guarda resultados en archivos,
- y registra errores si algo falla.

## Cómo crear y configurar un cronjob

Un cronjob es una tarea programada por el sistema operativo. En este proyecto, el enfoque más simple es dejar que `04_cronjobs.py` genere el informe y luego hacer que `cron` lo ejecute todos los días a una hora concreta.

### 1. Asegura el entorno

- Ten instalado el entorno virtual o `uv`.
- Define `OPENROUTER_API_KEY` en el entorno desde el que se ejecutará el cron.
- Comprueba la ruta real del intérprete de Python que usará `cron`.

Puedes obtener la ruta con:

```bash
which python
```

Si usas `uv`, también puedes apoyarte en el entorno del proyecto para resolver la ruta correcta.

### 2. Abre el editor de cron

```bash
crontab -e
```

Si es la primera vez, el sistema te pedirá elegir un editor.

### 3. Añade una entrada

Ejemplo para ejecutar el informe diario a las 08:00 todos los días:

```cron
0 8 * * * cd /Users/emi/Desktop/Projects/Construccion-Agentes-Autonomos && /ruta/al/python /Users/emi/Desktop/Projects/Construccion-Agentes-Autonomos/04_cronjobs.py >> /Users/emi/Desktop/Projects/Construccion-Agentes-Autonomos/logs/cron.log 2>&1
```

Qué significa cada parte:

- `0 8 * * *`: minuto 0, hora 8, todos los días.
- `cd ... &&`: coloca el trabajo en la raíz del proyecto para que encuentre archivos como `informes/` y `logs/`.
- `/ruta/al/python`: reemplázalo por el intérprete correcto de tu entorno.
- `>> ... 2>&1`: guarda salida normal y errores en un log.

### 4. Verifica la ejecución

Después de guardar el `crontab`, puedes comprobar que está cargado con:

```bash
crontab -l
```

Si quieres probar el script manualmente antes de confiarlo al cron, ejecuta:

```bash
uv run 04_cronjobs.py
```

### 5. Recomendaciones de configuración

- Usa rutas absolutas en `cron`.
- Redirige la salida a un archivo para poder depurar fallos.
- Asegúrate de que el directorio `informes/` sea escribible.
- Mantén la variable `OPENROUTER_API_KEY` disponible para el proceso de cron.

Con esta configuración, el sistema operativo dispara el script de forma automática y el ejemplo 4 actúa como una tarea autónoma programada.

## Cómo ejecutar cada ejemplo

```bash
uv run 01_agente_basico.py
uv run 02_agente_memoria.py
uv run 03_sistema_multiagente.py
uv run 04_cronjobs.py
```

## Visualizar `01_agente_basico` con LangGraph

Este repositorio incluye una versión equivalente del agente básico lista para
LangGraph Studio en [langgraph_01_agente_basico.py](langgraph_01_agente_basico.py).
El archivo [langgraph.json](langgraph.json) expone el grafo como `agent` para
que `langgraph dev` pueda cargarlo y dibujarlo.

Instala la CLI de LangGraph si no la tienes:

```bash
pip install -U "langgraph-cli[inmem]"
```

Después, desde la raíz del proyecto, arranca el servidor de desarrollo:

```bash
langgraph dev
```

Con eso podrás abrir Studio y ver el grafo del agente, incluyendo las llamadas
a herramientas.

El ejemplo 4 está pensado para ser disparado automáticamente por un cronjob o ejecutarse manualmente cuando quieras generar el informe.

## Ideas de evolución

- Cambiar `InMemorySaver` por un checkpointer persistente para producción.
- Añadir más herramientas especializadas.
- Registrar salidas en una base de datos en lugar de archivos planos.
- Separar los agentes en servicios independientes si el sistema crece.

## Resumen

Este proyecto enseña una progresión clara:

1. un agente básico que usa herramientas,
2. un agente con memoria,
3. un sistema multiagente coordinado,
4. y una capa de automatización que convierte todo eso en un flujo programado y continuo.

El ejemplo 4 es la pieza que mejor representa un sistema de agentes autónomos, porque no solo razona y usa herramientas, sino que también actúa de forma recurrente sin intervención humana.
