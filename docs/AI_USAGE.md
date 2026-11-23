# Registro de Uso y Validación de Inteligencia Artificial - RetailFlow AI

> [!NOTE]
> **Aviso de Proyecto Personal:**
> Este documento detalla la trazabilidad técnica de las herramientas de Inteligencia Artificial empleadas en el desarrollo de **RetailFlow AI**, un proyecto de portafolio personal desarrollado de forma independiente por un estudiante de Ingeniería en Sistemas para una postulación a **Pasante de Desarrollo Backend e IA**.

---

## 1. Asistencia de IA vs. Validación e Ingeniería Humana

En el ciclo de desarrollo de RetailFlow AI se adoptó una metodología de **co-diseño asistido con validación técnica humana rigurosa**:

- **Herramienta de Asistencia:** Se utilizó **Antigravity** (Google DeepMind) como agente de desarrollo para la generación de estructuras iniciales de código (FastAPI, SQLAlchemy 2.0, esquemas Pydantic v2, componentes React con Tailwind y pruebas Pytest).
- **Rol y Validación Humana:**
  - **Definición de Arquitectura y Negocio:** Establecimiento del principio de que **la IA nunca decide cantidades numéricas finales de inventario** ni escribe en la base de datos relacional.
  - **Verificación en Vivo:** Pruebas interactivas manuales del frontend React (`http://localhost:5173`) y del backend a través de Swagger UI (`/docs`).
  - **Ejecución y Control de Pruebas:** Ejecución independiente de la suite completa de **24 pruebas Pytest** desde la terminal de Windows PowerShell (`pytest -v`), confirmando 24/24 aprobadas.
  - **Compilación de Frontend:** Verificación de la compilación de TypeScript y el empaquetado de producción de Vite (`npm run build`, transformando 1601 módulos en ~2.62 s).

---

## 2. Registro Cronológico de Incidentes Reales y Depuración

Durante la implementación del proyecto se diagnosticaron y resolvieron incidencias técnicas reales:

### Incidente 1: `ModuleNotFoundError` en el entorno virtual de Python
- **Síntoma:** Al ejecutar pruebas iniciales de IA, Python arrojó:
  ```text
  ModuleNotFoundError: No module named 'google'
  ```
- **Causa:** La librería oficial `google-genai` había sido declarada en `requirements.txt`, pero el entorno virtual `.venv` no había completado la instalación de dependencias tras una desconexión de sesión.
- **Resolución Humana:** Se ejecutó explícitamente desde PowerShell:
  ```powershell
  pip install -r requirements.txt
  ```
  Verificando la presencia de `google-genai>=1.0.0` y sus dependencias asociadas.

### Incidente 2: Error 404 con el modelo `gemini-2.5-flash`
- **Síntoma:** La primera llamada real a Gemini API falló con una excepción HTTP 404 de Google AI Studio, indicando que el identificador `gemini-2.5-flash` no estaba habilitado en la región/cuenta.
- **Diagnóstico:** Se ejecutó el script de inspección `check_models.py` para consultar qué modelos tenían habilitada la acción `generateContent`.
- **Resolución:** Se configuró en `.env` el modelo soportado: `GEMINI_MODEL="gemini-3.5-flash"`.
- **Verificación Real:** Se ejecutó la llamada desde Swagger UI y luego desde el Frontend React, obteniendo una respuesta **HTTP 200** con:
  ```json
  {
    "source": "gemini",
    "model_used": "gemini-3.5-flash",
    "total_critical_products": 2
  }
  ```

### Incidente 3: Errores de compilación TypeScript en el Frontend
- **Síntomas:** Al ejecutar `npm run build` en `frontend/`, TypeScript emitió:
  ```text
  src/main.tsx: error TS5097: An import path can only end with a '.tsx' extension when 'allowImportingTsExtensions' is enabled.
  src/services/api.ts: error TS2339: Property 'env' does not exist on type 'ImportMeta'.
  ```
- **Causa:**
  1. Importación con extensión explícita (`import App from './App.tsx'`).
  2. Falta de referencia a los tipos de cliente de Vite para `import.meta.env`.
- **Resolución:**
  1. Se ajustó el import a `import App from './App'`.
  2. Se creó el archivo `src/vite-env.d.ts` con `/// <reference types="vite/client" />` y la interfaz tipada `ImportMetaEnv`.
- **Verificación:** El comando `npm run build` compiló sin advertencias ni errores en 20.97 s (y subsecuentes en 2.62 s).

---

## 3. Pruebas Automatizadas de Mitigación de Alucinaciones

Para asegurar la confiabilidad del sistema ante comportamientos estocásticos de los LLMs, se diseñaron pruebas unitarias especializadas en `tests/test_ai.py` utilizando mocks controlados:

1. **Rechazo de SKUs Inventados (Alucinación):**
   - El mock inyecta un SKU inexistente (`SKU-INVENTADO-999`).
   - El backend detecta que el artículo no pertenece al catálogo de productos críticos enviados y activa inmediatamente el **fallback determinista** (`source="fallback"`).
2. **Rechazo de Cantidades Inconsistentes:**
   - Para un producto con stock crítico que requiere 9 unidades según el cálculo del backend, el mock de Gemini devuelve `suggested_quantity: 50`.
   - El validador detecta la alteración cuantitativa y conmuta a fallback, garantizando que **la IA no pueda inflar ni recortar pedidos de compra**.
3. **Manejo de Respuestas no Parseables:**
   - El mock devuelve texto que no es JSON válido.
   - El backend captura la excepción de deserialización y emite el análisis determinista en milisegundos con HTTP 200, evitando errores 500 en tienda.
4. **Resiliencia ante Caídas de Red y Límites de Cuota (429 / Timeout):**
   - El mock simula una excepción `TimeoutError`.
   - El sistema responde con el fallback determinista, manteniendo la continuidad operativa sin bloquear el frontend ni exponer detalles internos de la API.
