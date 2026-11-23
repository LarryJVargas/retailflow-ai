# Guía Operativa y Runbook Full Stack - RetailFlow AI

> [!NOTE]
> **Aviso de Proyecto Personal:**
> Este documento detalla los procedimientos de operación y contingencia de **RetailFlow AI**, un proyecto de portafolio personal desarrollado de forma independiente por un estudiante de Ingeniería en Sistemas para una postulación a **Pasante de Desarrollo Backend e IA**. No constituye un documento operativo de Carrefour Argentina ni de ninguna otra entidad comercial.

---

## 1. Requisitos del Sistema

- **Sistema Operativo:** Windows 10/11 (ejecución mediante PowerShell).
- **Backend:** Python **3.12.x** añadido al `PATH`.
- **Frontend:** Node.js **20+ o 24+** (con `npm`).
- **Navegador Web:** Chrome, Edge, Firefox o cualquier navegador moderno.

---

## 2. Procedimiento de Arranque Full Stack

Se requieren dos terminales independientes de **PowerShell**:

### Terminal 1: Servidor Backend (FastAPI)
```powershell
# 1. Posicionarse en la raíz del proyecto
cd c:\Users\user\Desktop\Apps\retailflow-ai

# 2. Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# 3. Iniciar Uvicorn en el puerto 8000
uvicorn app.main:app --reload --port 8000
```
- Endpoint Base: `http://127.0.0.1:8000`
- Documentación Swagger: `http://127.0.0.1:8000/docs`

### Terminal 2: Servidor Frontend (React + Vite)
```powershell
# 1. Posicionarse en la carpeta frontend
cd c:\Users\user\Desktop\Apps\retailflow-ai\frontend

# 2. Iniciar Vite en modo desarrollo
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

La suite del backend cuenta con **24 pruebas** que se ejecutan sobre una base de datos SQLite en memoria aislada:

```powershell
# Desde la raíz del proyecto con el entorno virtual activo:
.\.venv\Scripts\Activate.ps1
pytest -v
```

Para compilar y verificar el frontend:
```powershell
# Desde la carpeta frontend/:
cd frontend
npm run build
```

---

## 5. Matriz de Diagnóstico y Resolución de Errores (Troubleshooting)

### A. Errores de Comunicación Frontend ↔ Backend

| Síntoma / Error | Causa Probable | Procedimiento de Mitigación |
| :--- | :--- | :--- |
| **`TypeError: Failed to fetch` en la consola del navegador** | El backend no está encendido en el puerto 8000 o la URL en `VITE_API_BASE_URL` es incorrecta. | 1. Verificar que Uvicorn esté corriendo en `http://localhost:8000`.<br>2. Revisar que `frontend/.env` contenga `VITE_API_BASE_URL=http://localhost:8000`. |
| **Error de CORS en la consola (`Access-Control-Allow-Origin`)** | La solicitud proviene de un origen no registrado en `origins` dentro de `app/main.py`. | Comprobar que el frontend esté corriendo en `http://localhost:5173` o `http://127.0.0.1:5173`. Si se utiliza otro puerto (ej. 3000), verificar que esté incluido en la lista `origins` de FastAPI. |
| **Error 409 Conflict al guardar producto** | El código SKU ingresado ya existe en la base de datos para otro artículo. | La interfaz muestra un aviso contextual en el modal. Ingresar un SKU único para el producto. |
| **Error 422 Unprocessable Entity** | Valores numéricos negativos (precio < 0, stock < 0) o campos de texto vacíos. | El cliente HTTP extrae los errores de validación de Pydantic y los presenta en el formulario. Corregir los campos señalados. |

### B. Errores del Proveedor de IA (Google Gemini)

| Error / Código | Causa Probable | Comportamiento del Sistema y Mitigación |
| :--- | :--- | :--- |
| **401 Unauthorized** | `GEMINI_API_KEY` vacía, inválida o expirada en `.env`. | **Comportamiento:** Se activa el fallback determinista (`source="fallback"`).<br>**Mitigación:** Obtener una clave válida en Google AI Studio y actualizar `.env`. |
| **403 Forbidden** | Clave sin permisos de inferencia o bloqueada por región. | El sistema conmuta automáticamente a fallback determinista en milisegundos sin arrojar error 500 al operador. |
| **404 Not Found (Modelo)** | Identificador de modelo inexistente en la API (ej. `gemini-2.5-flash`). | Configurar en `.env`: `GEMINI_MODEL="gemini-3.5-flash"`. Se puede ejecutar `python check_models.py` para listar los modelos habilitados. |
| **429 Too Many Requests** | Límite de cuota gratuita por minuto o día alcanzado en Google AI Studio. | El backend intercepta el 429 y responde de forma transparente con el análisis determinista. La operación de tienda no se interrumpe. |
| **Timeout de Conexión** | Latencia de red o cuelgue temporal de los servidores externos. | El bloque `except Exception` captura el timeout y responde con fallback en menos de 20 ms. |

---

## 6. Verificación Segura de Variables de Entorno

Para verificar que las variables están cargadas sin exponer contraseñas ni claves privadas en pantalla:

### Backend (PowerShell):
```powershell
python -c "import os; from dotenv import load_dotenv; load_dotenv(); key = os.getenv('GEMINI_API_KEY', ''); print(f'GEMINI_API_KEY presente: {bool(key)} | Longitud: {len(key)} chars | Modelo: {os.getenv(\"GEMINI_MODEL\")}')"
```

### Frontend (PowerShell):
```powershell
Get-Content frontend/.env | Select-String "VITE_API_BASE_URL"
```
