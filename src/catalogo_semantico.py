"""
Busqueda semantica sobre el catalogo de proveedores - Hotel Austral
=====================================================================
No todos los proveedores tienen lista de precios formal. Este modulo permite
preguntar por un producto que no esta cargado exactamente y encontrar, por
similitud, que proveedor probablemente lo tenga - basado en otros productos
similares que ese proveedor ya vende (ej: pido "bolsa de arranque 20x40" y el
sistema encuentra que Casa Texeira vende "bolsa arranque 30x40", del mismo
proveedor y familia de producto).

Usa embeddings de Cohere + un vector store en memoria (Chroma).
"""

import os
import pandas as pd
from langchain_cohere import CohereEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

RUTA_CATALOGO_DEFAULT = os.path.join(os.path.dirname(__file__), "..", "data", "procesados", "catalogo.csv")


def _fila_a_documento(fila: pd.Series) -> Document:
    texto = f"{fila['producto']} | categoria: {fila['categoria']} | alias: {fila.get('alias', '')}"
    return Document(
        page_content=texto,
        metadata={
            "proveedor": fila["proveedor"],
            "producto": fila["producto"],
            "categoria": fila["categoria"],
            "precio": fila["precio"] if pd.notna(fila["precio"]) else None,
            "unidad": fila.get("unidad", ""),
            "fuente": fila.get("fuente", ""),
        },
    )


def construir_vectorstore(ruta_catalogo: str = RUTA_CATALOGO_DEFAULT) -> Chroma:
    df = pd.read_csv(ruta_catalogo)
    documentos = [_fila_a_documento(fila) for _, fila in df.iterrows()]
    embeddings = CohereEmbeddings(model="embed-multilingual-v3.0")
    return Chroma.from_documents(documentos, embeddings, collection_name="catalogo_hotel_austral")


def buscar_proveedor_similar(vectorstore: Chroma, producto_query: str, k: int = 3) -> list[dict]:
    """
    Devuelve los k productos/proveedores mas similares a la consulta, aunque
    el producto exacto no este cargado. Sirve para sugerir "a quien preguntarle".
    """
    resultados = vectorstore.similarity_search_with_score(producto_query, k=k)
    salida = []
    for doc, score in resultados:
        salida.append(
            {
                "proveedor": doc.metadata["proveedor"],
                "producto_encontrado": doc.metadata["producto"],
                "categoria": doc.metadata["categoria"],
                "precio": doc.metadata["precio"],
                "similitud": round(1 - score, 3),  # menor distancia = mayor similitud
            }
        )
    return salida


if __name__ == "__main__":
    vs = construir_vectorstore()
    consulta = "bolsa de arranque 20x40"
    print(f"Buscando proveedor para: '{consulta}'\n")
    for r in buscar_proveedor_similar(vs, consulta):
        print(f"  - {r['proveedor']}: {r['producto_encontrado']} (similitud {r['similitud']})")
