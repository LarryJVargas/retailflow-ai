# Registro de Uso y Validación de Inteligencia Artificial - RetailFlow AI

Este documento describe con transparencia técnica el rol de las herramientas de Inteligencia Artificial en el desarrollo de **RetailFlow AI**, diferenciando con precisión la asistencia computacional de la supervisión, validación y depuración humana.

---

## 1. Asistencia de IA vs. Validación e Ingeniería Humana

En el desarrollo de este backend se adoptó un enfoque de **co-diseño asistido por IA** complementado con **auditoría manual rigurosa**:

- **Herramienta de Asistencia:** Se utilizó **Antigravity** (Google DeepMind) como agente de desarrollo para la generación inicial de estructuras de código (FastAPI, SQLAlchemy 2.0, esquemas Pydantic), automatización de pruebas y redacción de borradores de documentación.
- **Rol y Validación Humana:**
  - Definición de los requisitos del dominio de negocio retail (prevención de stockout, partición mutuamente excluyente de inventario, contratos estrictos).
  - Verificación manual e interactiva de los endpoints REST mediante la interfaz Swagger UI (`/docs`).
  - Ejecución independiente y controlada de la suite de pruebas unitarias desde la terminal de **PowerShell**.
  - Auditoría del código para garantizar que la IA nunca decida cantidades contables ni escriba directamente en la base de datos relacional.

---

## 2. Registro de Incidentes Reales y Depuración

Durante la integración con el SDK oficial de Gemini (`google-genai`), se presentaron desafíos técnicos concretos que fueron diagnosticados y resueltos:

### Incidente 1: `ModuleNotFoundError` en el entorno de ejecución
- **Síntoma:** Al ejecutar pruebas iniciales o scripts de verificación, se produjo el error:
  ```text
  ModuleNotFoundError: No module named 'google'
  ```
- **Causa:** La librería moderna `google-genai` había sido agregada a `requirements.txt`, pero el entorno virtual `.venv` no había completado la instalación del paquete tras una reconexión de terminal.
- **Solución y Validación Humana:** Se ejecutó explícitamente desde PowerShell:
  ```powershell
  pip install -r requirements.txt
  ```
  Verificando con `pip show google-genai` que el paquete quedó correctamente instalado en `.venv\Lib\site-packages`.

### Incidente 2: Error 404 en el identificador de modelo `gemini-2.5-flash`
- **Síntoma:** Al probar la llamada real a la API, la librería arrojó una excepción de tipo `NotFound (404)` indicando que el modelo `gemini-2.5-flash` no estaba habilitado o no existía bajo ese identificador en la API v1beta/v1 de Google AI Studio.
- **Diagnóstico:** Se ejecutó el script `check_models.py` para listar los modelos con capacidad `generateContent` habilitados en la cuenta.
- **Solución:** Se ajustó la configuración a `GEMINI_MODEL="gemini-3.5-flash"` en el archivo `.env`.
- **Verificación Real:** Se invocó el endpoint `POST /ai/analyze-inventory` desde Swagger UI con la API Key configurada, obteniendo exitosamente una respuesta **HTTP 200** con:
  ```json
  {
    "source": "gemini",
    "model_used": "gemini-3.5-flash",
    "total_critical_products": 2
  }
  ```

---

## 3. Pruebas de Mitigación de Alucinaciones y Fallos del Modelo

Para garantizar que RetailFlow AI sea seguro para un entorno retail comercial, se implementaron pruebas con mocks en `tests/test_ai.py` que simulan comportamientos adversos típicos de LLMs:

1. **Simulación de SKU Inventado (Alucinación):**
   - El mock inyecta en la respuesta de Gemini un SKU inexistente (`SKU-INVENTADO-999`).
   - El backend detecta la discrepancia con el catálogo real, descarta el payload y activa el **fallback determinista**, preservando la integridad del catálogo.
2. **Simulación de Cantidad Inconsistente:**
   - El backend calcula que se requieren 9 unidades de reposición para el producto `CAP-002`, pero el mock de Gemini devuelve `suggested_quantity: 50`.
   - El sistema detecta que la IA intentó alterar la cantidad determinista y conmuta inmediatamente a **fallback**, asegurando que la IA no tome decisiones cuantitativas arbitrarias.
3. **Simulación de JSON Malformado:**
   - El mock devuelve texto plano o sintaxis rota.
   - Pydantic y el parser de Python capturan el fallo de deserialización y activan el fallback sin emitir un error 500 al cliente.
4. **Simulación de Errores de API (429 / Timeout):**
   - El mock genera una excepción `TimeoutError`.
   - El servicio responde con HTTP 200 en fallback, manteniendo la continuidad operativa de la sucursal.
