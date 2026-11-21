# Guía Operativa y Runbook - RetailFlow AI

Este documento detalla los procedimientos de instalación, operación diaria, diagnóstico y contingencia para **RetailFlow AI** en entornos de desarrollo y evaluación técnica.

---

## 1. Requisitos Previos

- **Sistema Operativo:** Windows 10/11 (ejecución mediante PowerShell).
- **Python:** Versión **3.12.x** instalada y añadida al `PATH`.
- **Git:** Para clonación y control de versiones.
- **Acceso a Internet (opcional para IA):** Requerido únicamente para llamadas reales a Gemini API y descarga inicial de paquetes pip.

---

## 2. Instalación y Puesta en Marcha en Windows

Ejecutar secuencialmente desde **PowerShell**:

### Paso 1: Clonar o posicionarse en el directorio
```powershell
cd c:\Users\user\Desktop\Apps\retailflow-ai
```

### Paso 2: Crear y activar el entorno virtual
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
*(Si PowerShell restringe la ejecución de scripts, habilitar temporalmente con: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`)*.

### Paso 3: Instalar dependencias fijadas
```powershell
pip install -r requirements.txt
```

### Paso 4: Configurar variables de entorno
Copiar la plantilla de ejemplo:
```powershell
Copy-Item .env.example .env
```
Abrir el archivo `.env` y configurar las credenciales requeridas:
```env
APP_NAME="RetailFlow AI"
APP_ENV="development"
DEBUG=True
DATABASE_URL="sqlite:///./retailflow.db"

# Gemini AI Configuration
GEMINI_API_KEY="tu_clave_de_google_ai_studio"
GEMINI_MODEL="gemini-3.5-flash"
```

---

## 3. Inicio y Detención del Servidor

### Iniciar el servicio con recarga en caliente
```powershell
uvicorn app.main:app --reload --port 8000
```

- **API REST base:** `http://127.0.0.1:8000`
- **Swagger UI interactivo:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

### Detener el servidor
Presionar `Ctrl + C` en la ventana de PowerShell donde está corriendo Uvicorn.

---

## 4. Ejecución de Pruebas Automatizadas

La suite completa consta de **24 pruebas** que se ejecutan sobre una base de datos SQLite en memoria aislada:

```powershell
# Ejecutar todas las pruebas con detalle
pytest -v

# Ejecutar una suite específica
pytest -v tests/test_health.py
pytest -v tests/test_products.py
pytest -v tests/test_inventory.py
pytest -v tests/test_ai.py
```

---

## 5. Generación y Exportación de Reportes de Inventario

Existen dos vías para generar reportes en formato CSV con codificación UTF-8:

### Vía 1: Descarga directa HTTP
Realizar una petición GET al endpoint:
```http
GET http://127.0.0.1:8000/inventory/report
```
El navegador o cliente descargará un archivo con nombre dinámico: `inventory_report_YYYYMMDD_HHMMSS.csv`.

### Vía 2: Script CLI de automatización
Ejecutar desde PowerShell sin necesidad de tener el servidor HTTP encendido:
```powershell
python scripts/generate_report.py
```
El script generará el reporte en la carpeta `reports/` (excluida del control de versiones):
```text
[RetailFlow AI] Reporte de inventario generado exitosamente:
 -> c:\Users\user\Desktop\Apps\retailflow-ai\reports\inventory_report_20261121_143000.csv
```

---

## 6. Diagnóstico y Troubleshooting (Guía de Errores)

A continuación se describen los posibles escenarios de falla relacionados con el proveedor de IA (Google Gemini) y la forma en que el sistema los mitiga:

| Código / Error | Causa Probable | Comportamiento del Sistema | Acción de Mitigación |
| :--- | :--- | :--- | :--- |
| **401 Unauthorized** | `GEMINI_API_KEY` ausente, mal escrita o expirada en `.env`. | El servicio registra una advertencia en log y activa el **fallback determinista** (`source: "fallback"`). No rompe la API. | Verificar la clave en Google AI Studio y actualizar `.env`. |
| **403 Forbidden** | Clave sin permisos de inferencia para la API o restricciones de facturación/región. | Se activa el fallback determinista con HTTP 200. | Verificar las restricciones de la API Key en la consola de Google Cloud / AI Studio. |
| **404 Not Found** (Modelo) | El identificador de modelo configurado no existe o no está soportado en la versión de la API (ej. `gemini-2.5-flash` inexistente). | Se activa el fallback determinista. | Cambiar en `.env` a un modelo soportado verificado, como `GEMINI_MODEL=gemini-3.5-flash` o `gemini-1.5-flash`. Ejecutar `python check_models.py` para listar modelos disponibles. |
| **429 Too Many Requests** | Límite de cuota gratuita (RPM/TPD) alcanzado en la API de Gemini. | El sistema no propaga el 429 al cliente retail; activa inmediatamente el fallback determinista. | Esperar el refresco de ventana de cuota o utilizar plan pago. La operación de tienda no se detiene. |
| **Timeout de Conexión** | Latencia de red o indisponibilidad temporal de los servidores de Google. | La llamada es atrapada por el bloque `except Exception`; se emite fallback determinista en milisegundos. | Verificar la conexión a internet. El sistema sigue operativo sin intervención humana. |

---

## 7. Procedimiento de Verificación Segura de Variables de Entorno

Para validar que las variables están cargadas sin imprimir claves privadas ni secretos en la terminal de PowerShell:

```powershell
# Verificar si GEMINI_API_KEY está definida y su longitud (sin exponer su contenido)
python -c "import os; from dotenv import load_dotenv; load_dotenv(); key = os.getenv('GEMINI_API_KEY', ''); print(f'API Key presente: {bool(key)} | Longitud: {len(key)} chars')"

# Verificar modelo configurado
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Modelo:', os.getenv('GEMINI_MODEL', 'no definido'))"
```
