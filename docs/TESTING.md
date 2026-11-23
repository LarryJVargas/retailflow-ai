# Estrategia y Ejecución de Pruebas Full Stack - RetailFlow AI

> [!NOTE]
> **Aviso de Proyecto Personal:**
> Este documento detalla la estrategia de aseguramiento de calidad de **RetailFlow AI**, un proyecto de portafolio personal desarrollado de forma independiente por un estudiante de Ingeniería en Sistemas para una postulación a **Pasante de Desarrollo Backend e IA**.

---

## 1. Visión General de la Estrategia de Pruebas

La calidad y confiabilidad de **RetailFlow AI** descansan sobre tres pilares complementarios:
1. **Suite Automatizada de Backend:** 24 pruebas unitarias e integradoras con **Pytest**, ejecutadas sobre una base de datos SQLite en memoria aislada.
2. **Validación de Compilación y Tipado de Frontend:** Verificación estricta de TypeScript (`tsc`) y empaquetado de producción con **Vite** (1601 módulos transformados sin errores).
3. **Verificación Manual Integral en Vivo:** Pruebas funcionales de extremo a extremo desde el navegador web (`http://localhost:5173`) contra el backend real con credenciales de **Google Gemini API** (`gemini-3.5-flash`).

---

## 2. Aislamiento del Entorno de Pruebas de Backend

Para asegurar que las pruebas sean deterministas, veloces y no contaminen los datos operativos:
- **Base de Datos en Memoria:** En `tests/conftest.py` se utiliza `sqlite:///:memory:` con la estrategia `StaticPool` de SQLAlchemy.
- **Ciclo de Vida Limpio por Prueba (`scope="function"`):** Cada test crea las tablas (`Base.metadata.create_all()`) y las destruye al finalizar (`Base.metadata.drop_all()`), asegurando aislamiento total entre ejecuciones y sin alterar `retailflow.db`.
- **Inyección de Dependencias Sobre-escrita:** FastAPI utiliza `app.dependency_overrides[get_db]` para entregar la sesión de pruebas en memoria mediante `TestClient`.
- **Mocks Controlados para IA:** En `tests/test_ai.py` se utiliza `unittest.mock.patch("google.genai.Client")` para simular respuestas de Gemini, permitiendo ejecutar la suite sin conexión a internet y sin costo de tokens.

---

## 3. Catálogo de las 24 Pruebas Pytest del Backend

### Módulo 1: Salud y Configuración (`tests/test_health.py` - 1 Test)
| Función de Test | Alcance y Comprobaciones |
| :--- | :--- |
| `test_health_check_returns_200_and_ok` | Valida que `GET /health` retorne HTTP 200, status "ok", nombre de la aplicación y entorno actual. |

### Módulo 2: Catálogo y Operaciones CRUD (`tests/test_products.py` - 12 Tests)
| Función de Test | Alcance y Comprobaciones |
| :--- | :--- |
| `test_create_product_success` | Creación exitosa de producto vía `POST /products` (HTTP 201), validando persistencia y campos. |
| `test_create_product_with_duplicate_sku_returns_409` | Intento de registrar un SKU existente. Debe rechazar con HTTP 409 Conflict. |
| `test_create_product_negative_price_fails_with_422` | Validación Pydantic que bloquea precios negativos (HTTP 422 Unprocessable Entity). |
| `test_create_product_negative_stock_fails_with_422` | Validación Pydantic que bloquea stock inicial negativo (HTTP 422). |
| `test_list_products` | Comportamiento de `GET /products` con catálogo vacío y con registros insertados. |
| `test_get_product_by_id_success` | Consulta de detalle exitosa por ID numérico (`GET /products/{id}`). |
| `test_get_product_by_id_not_found` | Retorno adecuado de HTTP 404 cuando el ID solicitado no existe. |
| `test_patch_product_success` | Actualización parcial de campos (`PATCH /products/{id}`) preservando los atributos omitidos. |
| `test_patch_product_duplicate_sku_returns_409` | Bloqueo de colisión de SKU durante una actualización parcial contra otro registro existente. |
| `test_patch_product_not_found` | Retorno de HTTP 404 al intentar actualizar un ID inexistente. |
| `test_delete_product_success` | Eliminación física (`DELETE /products/{id}`) con HTTP 204 y posterior verificación de no existencia. |
| `test_delete_product_not_found` | Retorno de HTTP 404 al intentar eliminar un ID inexistente. |

### Módulo 3: Métricas de Inventario y Reportes CSV (`tests/test_inventory.py` - 4 Tests)
| Función de Test | Alcance y Comprobaciones |
| :--- | :--- |
| `test_inventory_empty_database` | Verifica que con base vacía los endpoints `/summary`, `/low-stock`, `/out-of-stock` y `/report` respondan limpiamente. |
| `test_inventory_classification_and_metrics` | Verifica la partición matemática mutuamente excluyente (agotados, stock bajo y saludables, incluyendo casos de borde con `minimum_stock = 0`), garantizando que `total = low + out + healthy`. |
| `test_inventory_csv_report_endpoint` | Descarga de reporte vía `GET /inventory/report`, validando cabecera `Content-Disposition`, formato CSV y exclusión de artículos saludables. |
| `test_save_inventory_report_to_disk_service` | Ejecución del servicio de exportación a disco (`report_service`), comprobando codificación UTF-8 y escritura en directorio temporal. |

### Módulo 4: Análisis Inteligente y Resiliencia con Fallback (`tests/test_ai.py` - 7 Tests)
| Función de Test | Alcance y Comprobaciones |
| :--- | :--- |
| `test_ai_analyze_inventory_empty_db` | Con inventario saludable, responde inmediatamente con `total_critical_products = 0` sin invocar a Gemini. |
| `test_ai_analyze_inventory_valid_gemini_response` | Mock de Gemini retornando JSON válido, SKUs exactos y cantidades coincidentes. Valida respuesta con `source="gemini"`. |
| `test_ai_analyze_inventory_invalid_json_triggers_fallback` | Mock retornando texto roto no parseable. Verifica conmutación automática a `source="fallback"` con HTTP 200. |
| `test_ai_analyze_inventory_hallucinated_sku_triggers_fallback` | Mock inyectando un SKU inexistente en el catálogo. Valida que el filtro anti-alucinaciones active el fallback. |
| `test_ai_analyze_inventory_inconsistent_quantity_triggers_fallback` | Mock modificando la cantidad de reposición calculada por el backend. Valida el rechazo y activación del fallback. |
| `test_ai_analyze_inventory_api_exception_triggers_fallback` | Mock simulando una excepción de timeout / caída de API. Valida que el sistema responda con fallback sin emitir error 500. |
| `test_ai_analyze_inventory_missing_api_key_triggers_fallback` | Con `GEMINI_API_KEY` vacía o no configurada, valida que el servicio utilice directamente las reglas deterministas locales. |

---

## 4. Validación del Frontend (TypeScript & Vite)

El frontend fue sometido a validación estricta de compilación y empaquetado para producción:

```powershell
# En la carpeta frontend/:
cd frontend
npm run build
```

- **Resultado verificado:**
  ```text
  > retailflow-ai-frontend@0.1.0 build
  > tsc && vite build

  vite v6.4.6 building for production...
  transforming...
  ✓ 1601 modules transformed.
  rendering chunks...
  computing gzip size...
  dist/index.html                   0.55 kB │ gzip:  0.37 kB
  dist/assets/index-D9yChYps.css   24.41 kB │ gzip:  5.05 kB
  dist/assets/index-CJDUQWw7.js   191.71 kB │ gzip: 58.34 kB
  ✓ built in 2.62s
  ```
- **0 errores de TypeScript:** Configuración estricta en `tsconfig.json` con `noUnusedLocals`, `noUnusedParameters` y verificación de tipos en `src/services/api.ts`.

---

## 5. Pruebas Funcionales Manuales Ejecutadas en Vivo

Se comprobó manualmente en el navegador web el comportamiento de la solución Full Stack:
1. **Flujo CRUD:** Registro de productos con validación de SKU, edición en tiempo real, reflejo inmediato en la tabla y eliminación mediante modal de confirmación.
2. **Descarga de Reportes:** Clic en "Descargar CSV", validando la generación y descarga en disco del archivo con formato `inventory_report_YYYYMMDD_HHMMSS.csv`.
3. **Inferencia Real con Gemini:** Ejecución de `POST /ai/analyze-inventory`, verificando en pantalla la insignia púrpura `Gemini AI (gemini-3.5-flash)` y las tarjetas de recomendación con prioridad y justificación contextual.
4. **Resiliencia de Fallback:** Prueba sin API Key o con red desconectada, confirmando la conmutación a la insignia gris `Motor Determinista (Fallback)` sin interrupción del servicio.

---

## 6. Comandos de Verificación en PowerShell

```powershell
# 1. Asegurar entorno virtual activo y ejecutar Pytest (24 tests)
.\.venv\Scripts\Activate.ps1
pytest -v

# 2. Compilar el frontend en producción
cd frontend
npm run build
```
