## Agente de Compras — Hotel Austral

Proyecto final del challenge **AlurAgente** (Oracle Next Education — Alura Latam, G10).

## Para qué sirve

Este proyecto es una base de aprendizaje para entender cómo se combina un agente
con LLM, reglas determinísticas y búsqueda semántica para resolver una tarea
real de compras.

Si recién estás empezando, el orden recomendado es:

1. Leer la descripción del problema.
2. Revisar la arquitectura.
3. Ejecutar `python prototipo_local.py`.
4. Luego abrir `streamlit run app.py`.

## Descripción del proyecto

Hotel Austral (Viedma, Río Negro) compra insumos a más de una decena de proveedores
distintos (alimentos, limpieza, librería). Cada semana hay que decidir a quién
pedirle cada producto, buscando pagar bien pero también **minimizar la cantidad de
proveedores** con los que hay que coordinar entrega y pago.

Este agente conversacional resuelve dos problemas reales del área de compras del
hotel:

1. **Consolidación de pedidos**: dado un listado de productos, arma el pedido óptimo
   por proveedor aplicando la regla de negocio del hotel (ver más abajo).
2. **Proveedor sugerido para productos no catalogados**: si se necesita un producto
   que no está cargado exactamente (otra medida, otra marca), el agente busca por
   similitud semántica y sugiere a qué proveedor conviene preguntarle, en base a
   productos parecidos que ese proveedor ya provee.

El dataset de proveedores y precios está basado en datos reales de operación del
hotel (relevamientos semanales de compras), con algunos valores estimados donde no
había precio exacto disponible — están marcados como `EST` en los CSV, contra `REAL`
para los que sí salen de los documentos originales.

## Cómo funciona

El flujo principal está dividido en tres capas:

- La interfaz en Streamlit recibe la consulta del usuario.
- El agente interpreta la intención y decide qué herramienta usar.
- La lógica crítica vive en código determinístico, no en el modelo.

Eso hace que el comportamiento sea más fácil de probar y de explicar mientras
aprendés cómo funciona el sistema.

## Arquitectura

```
Usuario
  │
  ▼
Streamlit UI (app.py) ── interfaz de chat
  │
  ▼
Agente (LangChain + ChatCohere) ── src/agente.py
  │
  ├── Tool 1: optimizar_pedido_tool
  │     └── src/optimizador.py → Pandas sobre precios.csv
  │         Regla: diferencia de precio ≤15% → desempata por
  │         (a) cobertura de productos, (b) condición de pago
  │
  ├── Tool 2: buscar_proveedor_similar_tool
  │     └── src/catalogo_semantico.py → Embeddings Cohere + Chroma
  │         sobre catalogo.csv (incluye productos sin precio cargado)
  │
  └── Tool 3: listar_productos_disponibles_tool
        └── devuelve las claves de producto válidas para la Tool 1
```

La decisión de negocio (regla del 15% + condición de pago) es **código
determinístico**, no algo que el LLM "adivina" — así el resultado es siempre
reproducible. El LLM se usa para interpretar la consulta en lenguaje natural,
elegir qué tool llamar, y redactar la respuesta final.

## Qué aprender mirando este proyecto

- Cómo separar una interfaz de usuario de la lógica de negocio.
- Cómo usar un agente sin dejar que el modelo decida reglas críticas.
- Cómo combinar búsqueda semántica con datos tabulares.
- Cómo documentar un proyecto para poder retomarlo después sin perder contexto.

## Estructura de carpetas

```
alura-agente-hotel/
├── app.py                     # Interfaz Streamlit
├── prototipo_local.py         # Prueba el agente sin UI (correr primero)
├── requirements.txt
├── .env.example
├── src/
│   ├── agente.py               # Agente LangChain + Cohere y definición de tools
│   ├── optimizador.py          # Regla de negocio de consolidación de pedidos
│   └── catalogo_semantico.py   # Búsqueda semántica (embeddings)
├── data/
│   ├── precios_originales/     # Archivos tal cual llegan de cada proveedor
│   │   └── precios_casatexeira_general_20260706.pdf
│   └── procesados/             # Datos limpios que usa el agente
│       ├── proveedores.csv     # proveedor, rubro, condición de pago
│       ├── precios.csv         # clave, proveedor, producto, precio (para la Tool 1)
│       └── catalogo.csv        # superset ampliado (para la Tool 2, con o sin precio)
└── docs/
    └── relevamiento/
        └── relevamiento_inicial_desayuno_limpieza_20260706.md
```

### Convención de nombres para nuevas listas de precios

```
precios_<proveedor>_<rubro>_<AAAAMMDD>.<ext>
```
Ejemplo: `precios_saez_almacen_20260718.xlsx`. Van en `data/precios_originales/`
tal como llegan (PDF/Excel/imagen); una vez procesadas a formato limpio se
incorporan a `data/procesados/precios.csv` o `catalogo.csv`.

Para proveedores sin lista formal, se completa a mano `catalogo.csv` con esta
proforma (no requiere precio, solo el nombre del producto y alias):

| clave | proveedor | producto | categoria | precio | unidad | alias | fuente |
|---|---|---|---|---|---|---|---|

## Tecnologías utilizadas

- **Python 3.11**
- **LangChain** + **langchain-cohere** — orquestación del agente y tools
  (la versión está fijada para mantener compatibilidad con `AgentExecutor`)
- **Cohere Command A** (`command-a-03-2025`) — modelo por defecto para el agente
- **Cohere** (`command-r-plus` para chat, `embed-multilingual-v3.0` para embeddings)
- **Chroma** — vector store en memoria para la búsqueda semántica
- **Pandas** — lógica de negocio sobre los CSV
- **Streamlit** — interfaz de usuario, deploy en Streamlit Community Cloud (gratuito,
  no requiere OCI ni tarjeta de crédito)

## Instrucciones de instalación

```bash
git clone <url-del-repo>
cd alura-agente-hotel
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# completar .env con tu COHERE_API_KEY (gratis en https://dashboard.cohere.com/api-keys)
```

El directorio `.venv/` no se sube al repositorio: cada persona lo recrea en su
máquina al clonar el proyecto.

Probar primero en local, sin interfaz:
```bash
python prototipo_local.py
```

Correr la app completa:
```bash
streamlit run app.py
```

### Deploy en Streamlit Community Cloud

1. Subir el repo a GitHub (público).
2. En [share.streamlit.io](https://share.streamlit.io/), conectar el repo y
   seleccionar `app.py` como archivo principal.
3. En **Settings → Secrets**, agregar `COHERE_API_KEY = "tu_api_key"`.
4. Deploy. No requiere tarjeta de crédito ni OCI.

## Evidencia de despliegue en la nube

El challenge pide mostrar que la app fue desplegada y funciona en la nube. En
este proyecto alcanza con un despliegue público en Streamlit Community Cloud u
otra plataforma equivalente; no es obligatorio usar OCI.

Para completar la entrega conviene incluir:

- El enlace público de la app: https://hotel-supply-optimizer-ai.streamlit.app/
- Una captura de pantalla de la aplicación funcionando: [docs/Agente-de-Compras-Austral.png](docs/Agente-de-Compras-Austral.png)
- La plataforma usada y la fecha del deploy.

La versión recomendada de esta evidencia está documentada en
[docs/challenge/evidencia-deploy.md](docs/challenge/evidencia-deploy.md).

## Flujo recomendado para probarlo

1. Crear el entorno virtual e instalar dependencias.
2. Definir `COHERE_API_KEY` en `.env`.
3. Ejecutar `python prototipo_local.py` y revisar que responda a las preguntas de ejemplo.
4. Ejecutar `streamlit run app.py`.
5. Probar una consulta de consolidación y otra de proveedor sugerido.

## Documentación del challenge

Las recomendaciones del challenge se adaptaron a este proyecto en una carpeta
específica:

- [Preguntas frecuentes](docs/challenge/faq.md)
- [Política de privacidad y manejo de datos](docs/challenge/privacidad.md)
- [Términos de uso](docs/challenge/terminos.md)

Estas páginas complementan el README y el paso a paso con la parte más
importante para la entrega: qué hace el agente, qué datos usa y cuáles son sus
límites.

## Ejemplos de preguntas y respuestas

**Pregunta:** *"Necesito pedir papel higiénico, aceite, leche, queso barra y pan
blanco. Armame el pedido consolidado."*

**Respuesta esperada:**
```
- TITO: Papel higiénico ($1500, más barato, diferencia > 15% con el resto)
- QUILLAKAS: Aceite ($20500, diferencia ≤15%, gana por cubrir más productos)
- SAEZ: Leche ($1594), Queso barra ($9300)
- BIMBO: Pan blanco ($2800, diferencia ≤15%, gana por mejor condición de pago)

Total de proveedores necesarios: 4
Total estimado del pedido: $35.694
```

**Pregunta:** *"Busco bolsa de arranque 20x40, no tengo proveedor cargado para esa
medida."*

**Respuesta esperada:** el agente identifica que Casa Texeira vende "Bolsa Arranque
AD 30x40x750gr" — misma familia de producto — y sugiere consultarle ahí antes de
buscar un proveedor nuevo.

**Pregunta:** *"¿Qué productos tienen precio cargado actualmente?"*

**Respuesta esperada:** lista de claves de producto (papel_higienico, aceite,
leche, queso_barra, pan_blanco, naranjas, banana, huevos, etc.)

## Notas para aprender

- Si el agente falla, revisá primero `src/agente.py`.
- Si el precio o proveedor sugerido parece incorrecto, revisá `src/optimizador.py`.
- Si no encuentra productos parecidos, revisá `src/catalogo_semantico.py` y el
  contenido de `data/procesados/catalogo.csv`.
- El prototipo local es más útil que Streamlit para detectar errores de lógica.

## Evolución futura (fuera del alcance de este challenge)

Estas ideas surgieron durante el diseño pero se dejaron fuera de esta entrega por
tiempo, documentadas para una futura iteración:

- **Tracking de pedidos**: seguimiento semanal de qué proveedor recibió el pedido,
  si llegó, si llegó completo, y el estado del pago (cuenta corriente / saldo
  pendiente).
- **Clasificación automática de mensajes de WhatsApp**: hoy cada área del hotel
  informa requerimientos por WhatsApp en texto libre; se podría automatizar la
  clasificación por rubro (librería, frutas y verduras, limpieza, almacén) antes de
  pasar por el agente de optimización.
- **Ampliación del catálogo**: incorporar más listas de precios de proveedores
  (ver convención de nombres arriba) para que la búsqueda semántica cubra más
  del universo de compras real del hotel.
- **Normalización de unidades**: algunos ítems de Casa Texeira vienen en
  presentaciones por caja/bulto que no están normalizadas a precio unitario;
  antes de incluirlos en la regla estricta del 15% conviene verificar el
  contenido exacto de cada presentación.
