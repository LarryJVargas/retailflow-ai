# Guía Operativa y Runbook Full Stack - RetailFlow AI

Este documento detalla los procedimientos de instalación, puesta en marcha, operación diaria, monitoreo, contingencias y resolución de errores para **RetailFlow AI** en entornos de desarrollo y evaluación técnica.

---

## 1. Requisitos del Sistema

- **Sistemas Operativos Soportados:** Windows 10/11 (PowerShell), Linux (Ubuntu/Debian/Fedora) o macOS.
- **Backend:** Python **3.12.x** añadido al `PATH`, con soporte para SQLite (local) y PostgreSQL mediante `psycopg2-binary` (producción).
- **Frontend:** Node.js **20+ o 24+** (con `npm`).
- **Navegador Web:** Chrome, Edge, Firefox o cualquier navegador moderno.
- **Git** para clonación del código fuente.

---

## 2. Procedimiento de Clonación e Inicio Full Stack

### Paso Previo: Clonar el Repositorio
```bash
git clone https://github.com/<tu-usuario>/retailflow-ai.git
cd retailflow-ai
```

Se requieren dos terminales independientes (una para el Backend y otra para el Frontend):

### Terminal 1: Servidor Backend (FastAPI)

1. Crear y activar el entorno virtual:

   **En Windows (PowerShell):**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **En Linux / macOS:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Instalar dependencias e iniciar Uvicorn en el puerto 8000:
   ```bash
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```
   - Endpoint Base: `http://localhost:8000`
   - Documentación Swagger: `http://localhost:8000/docs`

### Terminal 2: Servidor Frontend (React + Vite)

1. Posicionarse en la carpeta relativa `frontend/`:
   ```bash
   cd frontend
   ```

2. Instalar dependencias e iniciar Vite:
   ```bash
   npm install
   npm run dev
   ```
   - Aplicación Web: `http://localhost:5173`

---

## 3. Procedimiento de Detención y Reinicio

- **Detener servicios:** Presionar `Ctrl + C` en cada una de las terminales activas.
- **Reinicio rápido de backend:** Si Uvicorn se inició con `--reload`, los cambios en archivos `.py` se recargan automáticamente sin reiniciar el proceso.
- **Reinicio rápido de frontend:** Vite aplica *Hot Module Replacement* (HMR) instantáneo al modificar archivos en `frontend/src/`.

---

## 4. Ejecución de Pruebas Automatizadas

La suite del backend cuenta con **36 pruebas** que se ejecutan sobre una base de datos SQLite en memoria aislada:

**En Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
pytest -v
```

**En Linux / macOS:**
```bash
source .venv/bin/activate
pytest -v
```

Para compilar y verificar el frontend en modo de producción:
```bash
cd frontend
npm run build
```

---

## 5. Preparación y Despliegue en Producción (Supabase + Render + Vercel)

> **Estado:** La aplicación está técnicamente preparada para desplegarse en estos entornos (aún pendiente de provisión en plataformas externas).

### A. Base de Datos PostgreSQL (Supabase)
1. Crear un proyecto en Supabase y copiar el *Connection String* (`URI`).
2. `app/config.py` normaliza automáticamente `postgres://` a `postgresql://` para compatibilidad con SQLAlchemy 2.0.
3. En `app/database.py`, el engine desactiva `check_same_thread` cuando no es SQLite y habilita `pool_pre_ping=True` y `pool_recycle=300`.

### B. Backend FastAPI (Render)
1. Crear un **Web Service** conectado al repositorio.
2. **Build Command:** `pip install -r requirements.txt`
3. **Start Command:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
4. **Variables de Entorno requeridas en Render:**
   - `APP_ENV=production`
   - `DEBUG=False`
   - `DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:[PORT]/postgres`
   - `GEMINI_API_KEY=<tu_clave_de_google_ai_studio>`
   - `GEMINI_MODEL=gemini-3.5-flash`
   - `CORS_ORIGINS=https://<tu-frontend>.vercel.app`
   - `RATE_LIMIT_WRITE=10/minute`
   - `RATE_LIMIT_DELETE=5/minute`
   - `RATE_LIMIT_AI=3/minute`

### C. Frontend React + Vite (Vercel)
1. Importar el repositorio en Vercel estableciendo **Root Directory** en `frontend`.
2. `frontend/vercel.json` ya incluye las reglas de *rewrite* hacia `/index.html` para soporte de SPA.
3. Configurar la variable de entorno:
   - `VITE_API_BASE_URL=https://<tu-backend>.onrender.com`

### D. Inicialización de Datos Demo (Seed Idempotente)
Para poblar una base de datos nueva (local o PostgreSQL apuntando `DATABASE_URL` al entorno destino) con 14 productos de ejemplo sin duplicar ni sobrescribir registros existentes:
```bash
python scripts/seed_data.py
```
*(En Linux/macOS: `python3 scripts/seed_data.py`)*.

**Estrategia para Demo Pública:** El backend aplica *rate limiting* por IP mediante `SlowAPI` (respetando `X-Forwarded-For` detrás del proxy de Render) sobre `POST`, `PATCH`, `DELETE` y `/ai/analyze-inventory`, devolviendo `HTTP 429`. Como el límite por IP no protege la cuota global de Gemini frente a tráfico distribuido, se recomienda configurar topes de cuota en Google AI Studio y re-ejecutar `scripts/seed_data.py` si se necesita restaurar el catálogo de demostración.

---

## 5. Matriz de Diagnóstico y Resolución de Errores (Troubleshooting)

### A. Errores de Comunicación Frontend ↔ Backend

| Síntoma / Error | Causa Probable | Procedimiento de Mitigación |
| :--- | :--- | :--- |
| **`TypeError: Failed to fetch` en la consola del navegador** | El backend no está encendido en el puerto 8000 o la URL en `VITE_API_BASE_URL` es incorrecta. | 1. Verificar que Uvicorn esté corriendo en `http://localhost:8000`.<br>2. Revisar que `frontend/.env` contenga `VITE_API_BASE_URL=http://localhost:8000`. |
| **Error de CORS en la consola (`Access-Control-Allow-Origin`)** | La solicitud proviene de un origen no registrado en la variable de entorno `CORS_ORIGINS`. | Comprobar que `CORS_ORIGINS` (en `.env` local o en el panel de Render) incluya el dominio exacto del frontend (ej. `http://localhost:5173` o `https://tu-app.vercel.app`), separados por comas y sin barra final. |
| **Error 429 Too Many Requests en `/products` o `/ai`** | Se superó el límite de peticiones por IP configurado en `SlowAPI`. | Esperar un minuto o ajustar `RATE_LIMIT_WRITE`, `RATE_LIMIT_DELETE` o `RATE_LIMIT_AI` en las variables de entorno. |
| **Error 409 Conflict al guardar producto** | El código SKU ingresado ya existe en la base de datos para otro artículo. | La interfaz muestra un aviso contextual en el modal. Ingresar un SKU único para el producto. |
| **Error 422 Unprocessable Entity** | Valores numéricos negativos (precio < 0, stock < 0) o campos de texto vacíos. | El cliente HTTP extrae los errores de validación de Pydantic y los presenta en el formulario. Corregir los campos señalados. |

### B. Errores del Proveedor de IA (Google Gemini)

| Error / Código | Causa Probable | Comportamiento del Sistema y Mitigación |
| :--- | :--- | :--- |
| **401 Unauthorized** | `GEMINI_API_KEY` vacía, inválida o expirada en `.env`. | **Comportamiento:** Se activa el fallback determinista (`source="fallback"`).<br>**Mitigación:** Obtener una clave válida en Google AI Studio y actualizar `.env`. |
| **403 Forbidden** | Clave sin permisos de inferencia o bloqueada por región. | El sistema conmuta automáticamente al análisis determinista de fallback sin emitir un error no controlado al cliente. |
| **404 Not Found (Modelo)** | Identificador de modelo inexistente en la API (ej. `gemini-2.5-flash`). | Configurar en `.env`: `GEMINI_MODEL="gemini-3.5-flash"`. Se puede ejecutar `python check_models.py` para listar los modelos habilitados. |
| **429 Too Many Requests** | Límite de cuota gratuita por minuto o día alcanzado en Google AI Studio. | El backend intercepta el 429 y responde de forma transparente con el análisis determinista. La operación de tienda no se interrumpe. |
| **Timeout de Conexión** | Latencia de red o cuelgue temporal de los servidores externos. | El bloque `except Exception` captura la excepción de timeout y genera la respuesta mediante el fallback determinista local. |

---

## 6. Verificación Segura de Variables de Entorno

Para verificar que las variables están cargadas sin exponer contraseñas ni claves privadas en la terminal:

### Backend:
**En Windows (PowerShell) o Linux/macOS (Bash):**
```bash
python -c "from app.config import get_settings; s = get_settings(); print(f'ENV: {s.app_env} | DB_IS_SQLITE: {s.resolved_database_url.startswith(\"sqlite\")} | CORS_ORIGINS: {len(s.parsed_cors_origins)} | GEMINI_KEY_SET: {bool(s.gemini_api_key)} | MODEL: {s.gemini_model}')"
```

### Frontend:
**En Windows (PowerShell):**
```powershell
Get-Content frontend/.env | Select-String "VITE_API_BASE_URL"
```

**En Linux / macOS (Bash):**
```bash
grep "VITE_API_BASE_URL" frontend/.env
```
