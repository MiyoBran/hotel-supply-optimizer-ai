import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import streamlit as st
from agente import crear_agente

st.set_page_config(page_title="Agente de Compras - Hotel Austral", page_icon="🏨")
st.title("🏨 Agente de Compras — Hotel Austral")
st.caption(
    "Consolida pedidos entre proveedores aplicando la regla de negocio del hotel "
    "(diferencia de precio del 15% + condicion de pago), y sugiere proveedores "
    "alternativos para productos que no estan en la lista exacta."
)

if not os.environ.get("COHERE_API_KEY"):
    st.warning(
        "Falta la variable de entorno COHERE_API_KEY. Configurala en un archivo .env "
        "local o en 'Secrets' si estas en Streamlit Community Cloud."
    )
    st.stop()

if "agente" not in st.session_state:
    with st.spinner("Iniciando agente..."):
        st.session_state.agente = crear_agente()
        st.session_state.historial = []

with st.expander("💡 Ejemplos de preguntas"):
    st.markdown(
        "- *Necesito pedir papel higienico, aceite, leche, queso barra y pan blanco. "
        "Armame el pedido consolidado.*\n"
        "- *Busco bolsa de arranque 20x40, no se a quien pedirle.*\n"
        "- *Que productos tienen precio cargado?*"
    )

for mensaje in st.session_state.historial:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["contenido"])

consulta = st.chat_input("Escribi tu pedido o consulta...")

if consulta:
    st.session_state.historial.append({"rol": "user", "contenido": consulta})
    with st.chat_message("user"):
        st.markdown(consulta)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            respuesta = st.session_state.agente.invoke({"input": consulta})
            texto = respuesta["output"]
            st.markdown(texto)

    st.session_state.historial.append({"rol": "assistant", "contenido": texto})
