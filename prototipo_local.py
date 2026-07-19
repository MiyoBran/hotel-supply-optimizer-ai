"""
Prototipo local - correr esto primero, ANTES de tocar Streamlit ni deploy.
Sirve para validar que el agente responde bien con distintas preguntas.

Uso:
    python prototipo_local.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agente import crear_agente

PREGUNTAS_DE_PRUEBA = [
    "Necesito pedir papel higienico, aceite, leche, queso barra y pan blanco. Armame el pedido consolidado.",
    "Busco bolsa de arranque 20x40, no tengo proveedor cargado para esa medida.",
    "Que productos tienen precio cargado actualmente?",
]

if __name__ == "__main__":
    if not os.environ.get("COHERE_API_KEY"):
        print("Falta la variable de entorno COHERE_API_KEY (definila en un .env o export).")
        sys.exit(1)

    executor = crear_agente()
    for pregunta in PREGUNTAS_DE_PRUEBA:
        print(f"\n{'='*70}\nPREGUNTA: {pregunta}\n{'='*70}")
        respuesta = executor.invoke({"input": pregunta})
        print(f"\nRESPUESTA:\n{respuesta['output']}")
