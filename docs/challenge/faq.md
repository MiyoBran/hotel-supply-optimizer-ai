## Preguntas frecuentes

### ¿Qué hace este agente?

Consolida pedidos de compras para el Hotel Austral y sugiere proveedores
similares cuando un producto no aparece cargado exactamente.

### ¿Necesito mi propia API key de Cohere?

Sí. Para correr el proyecto en otra máquina hay que definir `COHERE_API_KEY` en
el archivo `.env` o en los secretos de Streamlit.

### ¿Tengo que subir el entorno virtual al repositorio?

No. El directorio `.venv/` se recrea localmente en cada clon con
`python3 -m venv .venv`.

### ¿Qué hago si `prototipo_local.py` falla?

Revisá en este orden:

1. Que el entorno virtual esté activado.
2. Que `requirements.txt` esté instalado.
3. Que `COHERE_API_KEY` exista y sea válida.
4. Que `COHERE_MODEL` no apunte a un modelo retirado.

### ¿Qué hago si un producto no tiene precio cargado?

Usá la herramienta de búsqueda semántica para encontrar proveedores similares.
Después conviene revisar si el producto debe agregarse al catálogo procesado.

### ¿Se puede usar el agente sin internet?

No del todo. La app necesita acceso a Cohere para el modelo y para los
embeddings.

### ¿Qué modelo usa por defecto?

El valor por defecto es `command-a-03-2025`, pero puede cambiarse con la
variable de entorno `COHERE_MODEL`.