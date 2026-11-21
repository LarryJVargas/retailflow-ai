# Estrategia y Ejecución de Pruebas - RetailFlow AI

Este documento detalla la suite completa de pruebas automatizadas que respaldan la estabilidad, integridad y resiliencia de **RetailFlow AI**.

---

## 1. Arquitectura del Entorno de Pruebas

Para garantizar pruebas deterministas, ultrarrápidas y sin efectos secundarios sobre los datos de desarrollo:

- **Base de Datos Aislada en Memoria:**
  En `tests/conftest.py` se utiliza `sqlite:///:memory:` con la estrategia `StaticPool` de SQLAlchemy.
- **Ciclo de Vida por Prueba (`scope="function"`):**
  Antes de cada prueba unitaria se ejecutan las sentencias `Base.metadata.create_all()` y al finalizar se invoca `Base.metadata.drop_all()`. De este modo, ninguna prueba contamina el estado de otra, ni modifica el archivo `retailflow.db` de desarrollo.
- **Inyección de Dependencias Sobre-escrita:**
  Se utiliza el mecanismo nativo `app.dependency_overrides[get_db]` para que FastAPI despache la sesión efímera en memoria a través de `TestClient`.
- **Aislamiento de la IA (Mocks):**
  Para la suite automatizada se utiliza `unittest.mock.patch("google.genai.Client")`, evitando llamadas de red, costos de cuota y dependencia de credenciales externas durante el proceso de testing.

---

## 2. Inventario de las 24 Pruebas Automatizadas

La suite cuenta exactamente con **24 pruebas** distribuidas en 4 módulos especializados:

### Módulo 1: Salud y Disponibilidad (`tests/test_health.py` - 1 Test)
| Función de Test | Objetivo y Comprobaciones |
| :--- | :--- |
| `test_health_check_returns_200_and_ok` | Valida que `GET /health` retorne HTTP 200, status "ok", nombre de la aplicación y entorno. |

### Módulo 2: Catálogo y CRUD de Productos (`tests/test_products.py` - 12 Tests)
| Función de Test | Objetivo y Comprobaciones |
| :--- | :--- |
| `test_create_product_success` | Creación exitosa de producto vía `POST /products` (HTTP 201), validando campos y timestamp. |
| `test_create_product_with_duplicate_sku_returns_409` | Intento de registrar un producto con un SKU existente. Debe rechazar con HTTP 409 Conflict. |
| `test_create_product_negative_price_fails_with_422` | Validación Pydantic que impide precios negativos (HTTP 422 Unprocessable Entity). |
| `test_create_product_negative_stock_fails_with_422` | Validación Pydantic que impide stock inicial negativo (HTTP 422). |
| `test_list_products` | Comportamiento de `GET /products` con catálogo vacío y con registros insertados. |
| `test_get_product_by_id_success` | Consulta de detalle exitosa por ID numérico (`GET /products/{id}`). |
| `test_get_product_by_id_not_found` | Retorno adecuado de HTTP 404 cuando el ID solicitado no existe. |
| `test_patch_product_success` | Actualización parcial de campos (`PATCH /products/{id}`) preservando los atributos omitidos. |
| `test_patch_product_duplicate_sku_returns_409` | Bloqueo de colisión de SKU durante una actualización parcial contra otro registro existente. |
| `test_patch_product_not_found` | Retorno de HTTP 404 al intentar actualizar un ID inexistente. |
| `test_delete_product_success` | Eliminación exitosa (`DELETE /products/{id}`) con HTTP 204 y posterior verificación de no existencia. |
| `test_delete_product_not_found` | Retorno de HTTP 404 al intentar eliminar un ID inexistente. |

### Módulo 3: Métricas de Inventario y Reportes CSV (`tests/test_inventory.py` - 4 Tests)
| Función de Test | Objetivo y Comprobaciones |
| :--- | :--- |
| `test_inventory_empty_database` | Verifica que con base vacía los endpoints `/summary`, `/low-stock`, `/out-of-stock` y `/report` respondan limpiamente sin errores ni nulos. |
| `test_inventory_classification_and_metrics` | Verifica la partición matemática de clasificación de inventario: productos agotados, con bajo stock y saludables (incluyendo casos de borde donde `minimum_stock == 0`), garantizando que `total = low + out + healthy`. |
| `test_inventory_csv_report_endpoint` | Descarga de reporte vía `GET /inventory/report`, validando cabecera `Content-Disposition`, formato CSV y exclusión de productos saludables. |
| `test_save_inventory_report_to_disk_service` | Ejecución del servicio de exportación a disco (`report_service`), comprobando escritura en UTF-8 y presencia de cabeceras en el sistema de archivos temporal. |

### Módulo 4: Análisis con IA y Resiliencia con Fallback (`tests/test_ai.py` - 7 Tests)
| Función de Test | Objetivo y Comprobaciones |
| :--- | :--- |
| `test_ai_analyze_inventory_empty_db` | Cuando no hay productos críticos, responde inmediatamente con estado saludable y 0 recomendaciones sin invocar a Gemini. |
| `test_ai_analyze_inventory_valid_gemini_response` | Mock de Gemini retornando JSON válido, SKUs exactos y cantidades coincidentes. Valida respuesta con `source="gemini"`. |
| `test_ai_analyze_inventory_invalid_json_triggers_fallback` | Mock retornando texto no parseable. Verifica que el sistema conmuta a `source="fallback"` con HTTP 200. |
| `test_ai_analyze_inventory_hallucinated_sku_triggers_fallback` | Mock inyectando un SKU no existente en el catálogo. Valida que el filtro anti-alucinaciones active el fallback. |
| `test_ai_analyze_inventory_inconsistent_quantity_triggers_fallback` | Mock modificando la cantidad de reposición calculada por el backend. Valida el rechazo y activación del fallback. |
| `test_ai_analyze_inventory_api_exception_triggers_fallback` | Mock simulando una excepción de timeout / caída de API. Valida que la API no emita HTTP 500 y responda en fallback. |
| `test_ai_analyze_inventory_missing_api_key_triggers_fallback` | Con `GEMINI_API_KEY` vacía o no configurada, valida que el servicio utilice directamente las reglas deterministas locales. |

---

## 3. Diferenciación: Pruebas Automatizadas vs. Verificación Real con Gemini

- **Pruebas Automatizadas (`pytest`):**
  Utilizan simulaciones aisladas (mocks) para garantizar que la suite completa pueda ejecutarse sin conexión a internet, en cualquier pipeline de CI/CD, sin costo de tokens y en menos de 2 segundos.
- **Verificación Real en Vivo:**
  La conexión real con la API de Google Gemini fue contrastada independientemente mediante la interfaz interactiva de **Swagger UI** (`/docs`) y scripts auxiliares (`test_gemini_connection.py`), confirmando la recepción de respuestas generadas por el modelo `gemini-3.5-flash` con credenciales activas.

---

## 4. Comandos de Ejecución en PowerShell

```powershell
# 1. Asegurar entorno virtual activo
.\.venv\Scripts\Activate.ps1

# 2. Ejecutar toda la suite de pruebas (24 tests)
pytest -v

# 3. Ejecución por archivo
pytest -v tests/test_health.py
pytest -v tests/test_products.py
pytest -v tests/test_inventory.py
pytest -v tests/test_ai.py
```
