"""
Agente de Compras - Hotel Austral
===================================
Agente conversacional (LangChain + Cohere) que ayuda a decidir a que
proveedor pedir cada producto, minimizando la cantidad de proveedores
distintos por pedido, y que sugiere proveedores alternativos para
productos que no estan en la lista de precios exacta.
"""

import os
import pandas as pd
from langchain_cohere import ChatCohere
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

from optimizador import cargar_datos, optimizar_pedido, claves_disponibles
from catalogo_semantico import construir_vectorstore, buscar_proveedor_similar

RUTA_PRECIOS = os.path.join(os.path.dirname(__file__), "..", "data", "procesados", "precios.csv")
RUTA_PROVEEDORES = os.path.join(os.path.dirname(__file__), "..", "data", "procesados", "proveedores.csv")
MODELO_COHERE = os.environ.get("COHERE_MODEL", "command-a-03-2025")

_precios, _proveedores = cargar_datos(RUTA_PRECIOS, RUTA_PROVEEDORES)
_vectorstore = None  # se construye de forma perezosa (lazy) - requiere API key de Cohere


def _get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = construir_vectorstore()
    return _vectorstore


@tool
def optimizar_pedido_tool(productos: list[str]) -> str:
    """
    Dado un listado de claves de producto (ver 'listar_productos_disponibles'),
    calcula el pedido consolidado optimo: a que proveedor pedir cada producto
    para minimizar la cantidad de proveedores distintos, aplicando la regla de
    negocio del 15% de diferencia de precio + condicion de pago.
    """
    resultado = optimizar_pedido(productos, _precios, _proveedores)
    lineas_texto = []
    for proveedor, lineas in resultado.pedido_por_proveedor().items():
        productos_txt = ", ".join(f"{l.producto} (${l.precio}, {l.motivo})" for l in lineas)
        lineas_texto.append(f"- {proveedor}: {productos_txt}")

    salida = "\n".join(lineas_texto)
    salida += f"\n\nTotal de proveedores necesarios: {resultado.cantidad_proveedores()}"
    salida += f"\nTotal estimado del pedido: ${resultado.total_estimado():,.2f}"
    if resultado.productos_sin_proveedor:
        salida += f"\n\nSin match exacto en la lista de precios: {resultado.productos_sin_proveedor}"
        salida += " (usa 'buscar_proveedor_similar_tool' para sugerir un proveedor por similitud)"
    return salida


@tool
def listar_productos_disponibles_tool() -> str:
    """Devuelve la lista de claves de producto que tienen precio cargado y pueden usarse en optimizar_pedido_tool."""
    return ", ".join(claves_disponibles(_precios))


@tool
def buscar_proveedor_similar_tool(producto: str) -> str:
    """
    Para un producto que NO esta en la lista de precios exacta (por nombre o
    medida distinta), busca por similitud semantica en el catalogo ampliado
    de proveedores y sugiere a quien preguntarle, basado en productos
    parecidos que ese proveedor ya vende.
    """
    vs = _get_vectorstore()
    resultados = buscar_proveedor_similar(vs, producto, k=3)
    if not resultados:
        return "No se encontraron proveedores con productos similares en el catalogo."
    lineas = [
        f"- {r['proveedor']}: vende '{r['producto_encontrado']}' (categoria: {r['categoria']}, similitud {r['similitud']})"
        for r in resultados
    ]
    return "\n".join(lineas)


SYSTEM_PROMPT = """Sos el asistente de compras del Hotel Austral (Viedma).
Tu trabajo es ayudar a decidir a que proveedor pedir cada producto, buscando
siempre minimizar la cantidad de proveedores distintos en un mismo pedido,
sin sacrificar precio ni condiciones de pago.

Reglas:
- Para pedidos con productos que SI tienen precio cargado, usa optimizar_pedido_tool.
  Antes, si no estas seguro de la clave exacta, usa listar_productos_disponibles_tool.
- Para productos que el usuario menciona pero no estan en la lista exacta
  (medida distinta, nombre distinto), usa buscar_proveedor_similar_tool para
  sugerir un proveedor alternativo por similitud.
- Respondé siempre en español rioplatense, de forma clara y organizada por
  proveedor. No inventes precios ni proveedores que no esten en las tools.
"""


def crear_agente() -> AgentExecutor:
    llm = ChatCohere(model=MODELO_COHERE, temperature=0)
    tools = [optimizar_pedido_tool, listar_productos_disponibles_tool, buscar_proveedor_similar_tool]

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    agente = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agente, tools=tools, verbose=True)


if __name__ == "__main__":
    executor = crear_agente()
    pregunta = (
        "Necesito pedir papel higienico, aceite, leche, queso barra y pan blanco. "
        "Armame el pedido consolidado."
    )
    respuesta = executor.invoke({"input": pregunta})
    print("\n=== RESPUESTA ===")
    print(respuesta["output"])
