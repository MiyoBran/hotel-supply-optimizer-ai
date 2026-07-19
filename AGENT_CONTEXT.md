---
title: Contexto rapido del proyecto
purpose: Onboarding rapido para agentes que trabajen en este repo
language: es
---

## Resumen

Este repo implementa un agente de compras para el Hotel Austral.
La app toma consultas en lenguaje natural y resuelve dos cosas:

- consolidar pedidos entre proveedores usando una regla deterministica
- sugerir proveedores similares para productos no catalogados exactamente

El flujo principal es:

1. `app.py` expone la interfaz Streamlit.
2. `src/agente.py` arma el agente LangChain + Cohere y registra las tools.
3. `src/optimizador.py` aplica la logica de consolidacion de pedidos.
4. `src/catalogo_semantico.py` hace busqueda semantica sobre el catalogo.

## Archivos clave

- `app.py`: UI principal de Streamlit.
- `prototipo_local.py`: prueba rapida sin interfaz; correr primero.
- `src/agente.py`: orquestacion del agente y definicion de tools.
- `src/optimizador.py`: regla de negocio para elegir proveedor.
- `src/catalogo_semantico.py`: embeddings Cohere + Chroma para sugerencias.
- `data/procesados/precios.csv`: fuente principal para la tool de optimizacion.
- `data/procesados/catalogo.csv`: catalogo ampliado para busqueda semantica.
- `data/procesados/proveedores.csv`: condicion de pago y rubro por proveedor.
- `README.md`: documentacion general del proyecto.
- `Paso-a-paso.md`: guia operativa para instalacion, prueba y deploy.

## Como arrancar

1. Crear o activar el entorno virtual de Python.
2. Instalar dependencias desde `requirements.txt`.
3. Crear `.env` a partir de `.env.example`.
4. Cargar `COHERE_API_KEY` en `.env`.
5. Ejecutar `python prototipo_local.py` para validar el agente sin UI.
6. Si responde bien, ejecutar `streamlit run app.py`.

## Que esperar en local

- `prototipo_local.py` falla rapido si falta `COHERE_API_KEY`.
- `app.py` tambien bloquea la interfaz si falta `COHERE_API_KEY`.
- La primera validacion deberia ser siempre el prototipo local, no Streamlit.

## Regla de negocio

La decision de consolidacion no depende del LLM.
Es codigo deterministico:

- si la diferencia de precio es menor o igual al 15%, se desempata por cobertura de productos y condicion de pago
- si la diferencia supera el 15%, gana la opcion mas barata

Esto hace que el resultado sea reproducible.

## Requisitos para ejecutar

- Python 3.11 o compatible
- dependencias instaladas desde `requirements.txt`
- variable de entorno `COHERE_API_KEY`
- variable opcional `COHERE_MODEL` si queres cambiar el modelo por defecto

Si falta `COHERE_API_KEY`, la app y el prototipo se detienen con advertencia.

## Secuencia recomendada

1. Completar `.env` con `COHERE_API_KEY`.
2. Ejecutar `python prototipo_local.py`.
3. Si responde bien, ejecutar `streamlit run app.py`.
4. Para deploy, usar Streamlit Community Cloud y cargar la key en Secrets.

## Sesion nueva desde cero

Si un agente arranca este repo sin contexto previo, todo esto debe tratarse como pendiente:

- clonar el repo desde `git@github.com:MiyoBran/hotel-supply-optimizer-ai.git`
- abrir el proyecto en VS Code o en la terminal local
- crear y activar un entorno virtual
- instalar dependencias desde `requirements.txt`
- crear `.env` desde `.env.example`
- pegar la `COHERE_API_KEY` real en `.env`
- ejecutar `python prototipo_local.py`
- ejecutar `streamlit run app.py`
- verificar que `.env` no se suba a Git
- configurar el remoto `origin` si no existe
- hacer `git push` a `main`
- configurar Streamlit Community Cloud
- cargar `COHERE_API_KEY` en Secrets
- probar el deploy público
- actualizar el README con evidencia del deploy

## Cosas a tener en cuenta

- `.env` ya esta ignorado por Git.
- En este workspace si hay un repositorio Git inicializado.
- El primer commit puede fallar si la configuracion local fuerza firma GPG sin una clave secreta valida.
- El proyecto usa nombres de productos normalizados en `data/procesados/precios.csv` y `catalogo.csv`; conviene respetarlos antes de agregar nuevos datos.

## Git y versionado

- Si `git commit` falla con un error de firma, revisar `user.signingkey` y si el comando esta usando `-S`.
- Para un proyecto de aprendizaje, conviene priorizar commits simples y reproducibles antes que firmas obligatorias.

## Comportamiento esperado del agente

Preguntas tipicas:

- consolidacion de una lista de productos por proveedor
- busqueda de un proveedor sugerido para un producto similar
- listado de claves de productos cargados

## Buen punto de partida para cambios

- Si falla la salida conversacional, revisar `src/agente.py` primero.
- Si la seleccion de proveedor es incorrecta, revisar `src/optimizador.py`.
- Si no encuentra productos parecidos, revisar `src/catalogo_semantico.py` y `data/procesados/catalogo.csv`.
