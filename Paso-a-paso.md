1. Crear el repo y abrir el proyecto desde WSL
   Abrí WSL y corré:

```bash
git clone git@github.com:MiyoBran/hotel-supply-optimizer-ai.git
cd hotel-supply-optimizer-ai
code .
```

Si ya tenés la carpeta descargada en Windows y preferís copiarla en vez de clonar, creá primero la carpeta destino en WSL y copiá todo el contenido ahí. La idea es trabajar desde el repo nuevo y no desde la copia de Windows.

2. Crear el entorno y preparar dependencias
   En la terminal de WSL, dentro del repo, creá y activá un entorno virtual si querés aislar dependencias:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Después instalá dependencias:

```bash
pip install -r requirements.txt
```

No hace falta desinstalar nada de Windows; ese entorno queda separado del de WSL.

3. Crear el .env y conseguir la API key de Cohere
   Copiá el archivo de ejemplo y completalo:

```bash
cp .env.example .env
```

Entrá a dashboard.cohere.com, creá una cuenta gratis si hace falta y andá a API Keys. Copiá la Trial key y pegala en `.env` como:

```bash
COHERE_API_KEY=tu_key_aca
```

Este archivo no se sube a GitHub porque ya está en `.gitignore`.

4. Probar el agente en local sin interfaz
   Corré:

```bash
python prototipo_local.py
```

Esto ejecuta 3 preguntas de prueba y te muestra las respuestas en la terminal. Si ves errores de import, revisá si el entorno virtual está activo y si `requirements.txt` se instaló bien. Si Cohere tira error de rate limit, esperá un minuto entre pruebas porque la cuenta gratis tiene límite bajo.

5. Probar la app completa con Streamlit
   Cuando el prototipo local funcione, corré:

```bash
streamlit run app.py
```

Se abre automáticamente en el navegador en `localhost:8501`. Probá los ejemplos del desplegable "Ejemplos de preguntas". Si algo falla acá, suele ser más fácil de debuggear antes del deploy.

6. Verificar Git y subir los cambios
   Antes de pushear, revisá el estado del repo:

```bash
git status
```

Confirmá que `.env` no aparezca en la lista de archivos a subir. Luego, si hace falta, configurá el remoto con este repo:

```bash
git remote add origin git@github.com:MiyoBran/hotel-supply-optimizer-ai.git
git branch -M main
git push -u origin main
```

Si el remoto ya existe, solo hacé el push.

7. Configurar el deploy en Streamlit Community Cloud
   Entrá a share.streamlit.io con tu cuenta de GitHub. Click en "New app", elegí tu repositorio y como "Main file path" poné `app.py`. No pongas la API key en el formulario principal; cargala en "Advanced settings" o después en Settings → Secrets con este formato TOML:

```toml
COHERE_API_KEY = "tu_key_aca"
```

Eso queda guardado de forma segura, separado del código.

8. Verificar el deploy y cerrar el README
   Una vez desplegado, probá la misma pregunta de ejemplo en la URL pública. Sacá una captura de pantalla o copiá el link, que es la evidencia del challenge. Agregalo al README en la sección correspondiente y hacé el último commit y push.
