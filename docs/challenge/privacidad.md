## Política de privacidad y manejo de datos

### Alcance

Esta aplicación es una demo educativa para el desafío AlurAgente. No está
pensada como una plataforma de producción ni como un sistema de gestión de
datos sensibles.

### Qué datos procesa

- Las consultas que escribe el usuario en la interfaz.
- Los datos de productos, precios y proveedores guardados en CSV.
- La API key de Cohere, solo para autenticación con el proveedor de modelo.

### Qué no persiste

- No hay base de datos de usuarios.
- No se guarda historial de conversación de forma permanente.
- No se versiona el archivo `.env`.
- No se versiona el entorno virtual `.venv/`.

La conversación vive en la sesión de Streamlit mientras la app está abierta. Si
se reinicia el proceso o se recarga la app, ese estado se pierde.

### Recomendaciones de uso

- No ingreses datos personales, contraseñas ni información sensible.
- Usá claves de prueba o limitadas cuando sea posible.
- Guardá la API key en `.env` local o en `Secrets`, nunca en el código.

### Embeddings y búsqueda semántica

La búsqueda semántica usa Cohere para generar embeddings y Chroma como vector
store en memoria.

### Datos del challenge

Los CSV procesados contienen información de proveedores y precios preparada para
la demo. Si el proyecto se reutiliza con datos reales nuevos, conviene revisar
otra vez qué información se carga y quién puede acceder a ella.