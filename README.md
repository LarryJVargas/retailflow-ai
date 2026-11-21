# RetailFlow AI - Sistema Inteligente de Gestión de Inventario para Retail

[![Python 3.12](https://img.shields.io/badge/Python-3.12.2-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.165.0-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.1.9-red.svg?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-2.14.4-e92063.svg?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![Google Gemini API](https://img.shields.io/badge/Google%20GenAI-gemini--3.5--flash-8E24AA.svg?logo=google&logoColor=white)](https://ai.google.dev/)
[![Tests Passing](https://img.shields.io/badge/Tests-24%20Passed-brightgreen.svg?logo=pytest&logoColor=white)](docs/TESTING.md)

**RetailFlow AI** es un backend de alto rendimiento diseñado para resolver desafíos críticos de disponibilidad de productos en góndola (*On-Shelf Availability*) y control de inventario en el sector retail (supermercados e hipermercados). Combina la solidez contable y la velocidad de reglas de negocio deterministas en Python con la capacidad analítica y contextual de **Google Gemini API** (`gemini-3.5-flash`), garantizando un diseño resiliente con **fallback automático**.

> Proyecto de portafolio técnico desarrollado para la postulación a **Pasante de Desarrollo Backend e IA en Carrefour Argentina**.

---

## 🏬 El Problema de Negocio en Retail

En la operación diaria de cadenas de retail a gran escala, la gestión deficiente de stock genera dos pérdidas directas:
1. **Quiebre de Stock (*Stockout*):** Falta de producto en góndola que provoca pérdidas inmediatas de facturación, insatisfacción del cliente y migración hacia competidores.
2. **Sobrestock:** Exceso de inventario que inmoviliza capital de trabajo, satura depósitos de sucursal e incrementa el riesgo de mermas y vencimientos.

**RetailFlow AI** resuelve este dilema mediante:
- Clasificación automatizada en categorías mutuamente excluyentes (Agotado, Stock Bajo, Saludable).
- Cálculo matemático exacto de la reposición sugerida para alcanzar el stock de seguridad.
- Priorización inteligente asistida por IA para orientar las órdenes de reposición del equipo de logística de tienda.
- Exportación automatizada de reportes CSV para abastecimiento y auditoría.

---

## 🚀 Funcionalidades Principales

- **Catálogo de Productos Completo (CRUD REST):** Administración con validación estricta de SKU único, precios no negativos y existencias.
- **Motor de Clasificación de Inventario:** Detección en tiempo real de artículos agotados y con bajo stock.
- **Análisis Inteligente con Google Gemini:** Generación de resúmenes ejecutivos, justificaciones contextuales y priorización de reposición (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
- **Arquitectura Híbrida Defensiva:** Las cantidades sugeridas son fijadas por el backend; la IA nunca altera los cálculos ni escribe en la base de datos.
- **Fallback Determinista Transparente:** Ante fallas de red, cuota excedida (429), timeouts o alucinaciones de la IA, el sistema conmuta automáticamente a reglas de negocio fijas sin interrumpir el servicio.
- **Exportación de Reportes CSV:** Vía endpoint REST o mediante script CLI automatizado en segundo plano.
- **Documentación Interactiva:** Swagger UI y ReDoc autogenerados.

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Justificación Técnica |
| :--- | :--- | :--- |
| **Lenguaje** | **Python 3.12.2** | Tipado estático moderno, mejoras de rendimiento y gestión asíncrona nativa. |
| **Framework Web** | **FastAPI** | Alta velocidad de respuesta, inyección de dependencias (`Depends`) y OpenAPI nativo. |
| **ORM / Persistencia** | **SQLAlchemy 2.0** | Declaración tipada moderna con `Mapped` y `mapped_column`, eliminando sintaxis legacy. |
| **Motor de BD** | **SQLite** | Portabilidad y facilidad de reproducción local inmediata sin requerir infraestructura cloud externa. |
| **Validación & DTOs** | **Pydantic v2** | Serialización ultrarrápida (núcleo en Rust), validación de restricciones (`ge=0`) y tipado estricto. |
| **SDK de IA** | **google-genai** | SDK oficial de Google para inferencia de modelos Gemini (`gemini-3.5-flash`). |
| **Testing** | **Pytest 9.2 + HTTPX** | 24 pruebas automatizadas sobre base de datos aislada en memoria con `StaticPool` y mocks controlados. |

---

## 📐 Arquitectura del Sistema

El sistema implementa una arquitectura desacoplada por capas:
- **Routers (`app/routers/`):** Controladores HTTP limpios, validación de peticiones y respuestas.
- **Services (`app/services/`):** Lógica pura de inventario (`inventory_service.py`), reportes (`report_service.py`) y orquestación con Gemini / Fallback (`ai_service.py`).
- **Schemas (`app/schemas/`):** Contratos de datos inmutables y validados.
- **Models (`app/models/`):** Modelado relacional mapeado a tablas SQLite.

```
[Cliente HTTP / Swagger UI]
          │
          ▼
   [Routers FastAPI] ──► [Inyección Depends(get_db)]
          │
          ▼
   [Services Layer]
     ├─► [inventory_service]: Reglas matemáticas de stock
     ├─► [report_service]: Generación CSV UTF-8
     └─► [ai_service]: Orquestador Gemini + Fallback Determinista
          │         │
          │         ├─► [Google Gemini API (gemini-3.5-flash)]
          ▼         ▼
     [SQLAlchemy 2.0 ORM] ──► [SQLite DB: retailflow.db]
```

Para más detalles, consulta la documentación completa en [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## 💻 Instalación y Puesta en Marcha (Windows PowerShell)

### 1. Clonar o posicionarse en el repositorio
```powershell
cd c:\Users\user\Desktop\Apps\retailflow-ai
```

### 2. Crear y activar el entorno virtual
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias fijadas
```powershell
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Copiar la plantilla de ejemplo:
```powershell
Copy-Item .env.example .env
```
Editar `.env` para ingresar tu API Key de Google Gemini:
```env
APP_NAME="RetailFlow AI"
APP_ENV="development"
DEBUG=True
DATABASE_URL="sqlite:///./retailflow.db"

# Gemini AI Configuration
GEMINI_API_KEY="tu_clave_de_google_ai_studio"
GEMINI_MODEL="gemini-3.5-flash"
```
*(Nota: Si no se provee `GEMINI_API_KEY`, el sistema operará normalmente utilizando el motor de fallback determinista local sin emitir errores).*

### 5. Iniciar el servidor
```powershell
uvicorn app.main:app --reload --port 8000
```
- **API Base:** `http://127.0.0.1:8000`
- **Documentación Swagger UI:** `http://127.0.0.1:8000/docs`
- **Documentación ReDoc:** `http://127.0.0.1:8000/redoc`

---

## 📌 Tabla de Endpoints de la API

### Catálogo y CRUD de Productos (`/products`)
| Método | Endpoint | Descripción | Códigos HTTP |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Chequeo de estado y ambiente de la aplicación | `200` |
| `GET` | `/products` | Listado paginado de productos | `200` |
| `GET` | `/products/{id}` | Obtención de detalle de un producto por ID | `200`, `404` |
| `POST` | `/products` | Creación de producto (valida SKU único y valores no negativos) | `201`, `409`, `422` |
| `PATCH` | `/products/{id}` | Actualización parcial de atributos de producto | `200`, `404`, `409`, `422` |
| `DELETE` | `/products/{id}` | Eliminación permanente de un producto | `204`, `404` |

### Control de Inventario (`/inventory`)
| Método | Endpoint | Descripción | Códigos HTTP |
| :--- | :--- | :--- | :--- |
| `GET` | `/inventory/summary` | Resumen cuantitativo del inventario (categorías mutuamente excluyentes) | `200` |
| `GET` | `/inventory/low-stock` | Productos con existencia positiva pero inferior al mínimo requerido | `200` |
| `GET` | `/inventory/out-of-stock` | Productos con stock agotado (`stock == 0`) | `200` |
| `GET` | `/inventory/report` | Descarga directa de archivo CSV con productos críticos | `200` |

### Análisis Inteligente con IA (`/ai`)
| Método | Endpoint | Descripción | Códigos HTTP |
| :--- | :--- | :--- | :--- |
| `POST` | `/ai/analyze-inventory` | Análisis de inventario crítico mediante Gemini o Fallback Determinista | `200` |

---

## 🤖 Ejemplo de Análisis Inteligente de Inventario

### Petición
```http
POST /ai/analyze-inventory
```

### Respuesta Exitosa con Gemini (`gemini-3.5-flash`)
```json
{
  "source": "gemini",
  "model_used": "gemini-3.5-flash",
  "summary": "Se detectaron 2 productos críticos con riesgo inminente de quiebre en góndola. Se sugiere reaprovisionamiento inmediato de productos básicos de alta rotación.",
  "total_critical_products": 2,
  "recommendations": [
    {
      "sku": "LECHE-ENT-001",
      "explanation": "Producto de primera necesidad totalmente agotado. Pérdida inmediata de ventas y daño a la fidelidad del cliente.",
      "priority": "CRITICAL",
      "suggested_quantity": 20
    },
    {
      "sku": "ARROZ-LAR-002",
      "explanation": "Stock por debajo del 30% del nivel mínimo de seguridad. Reposición preventiva recomendada antes del próximo turno pico.",
      "priority": "HIGH",
      "suggested_quantity": 8
    }
  ]
}
```

### Respuesta con Fallback Determinista (Ante fallas de red, cuota o sin API Key)
```json
{
  "source": "fallback",
  "model_used": null,
  "summary": "Análisis determinista generado por motor de reglas del sistema para 2 productos en estado crítico.",
  "total_critical_products": 2,
  "recommendations": [
    {
      "sku": "LECHE-ENT-001",
      "explanation": "Producto 'Leche Entera 1L' totalmente agotado. Reposición urgente requerida para reanudar disponibilidad comercial.",
      "priority": "CRITICAL",
      "suggested_quantity": 20
    },
    {
      "sku": "ARROZ-LAR-002",
      "explanation": "Stock de 'Arroz Largo Fino 1kg' (2 u.) inferior al 50% del mínimo requerido (10 u.). Alto riesgo de quiebre de inventario.",
      "priority": "HIGH",
      "suggested_quantity": 8
    }
  ]
}
```

---

## 🧪 Ejecución de Pruebas Automatizadas

La suite cuenta con **24 pruebas** que validan la salud del servicio, el CRUD, las reglas matemáticas de stock y la resiliencia de la IA mediante mocks:

```powershell
# Ejecutar toda la suite con detalle en PowerShell
pytest -v
```

Consulta el desglose completo de pruebas en [docs/TESTING.md](docs/TESTING.md).

---

## 📊 Automatización de Reportes (CLI Script)

Para ejecutar la generación de reportes CSV de inventario crítico sin levantar el servidor web:

```powershell
python scripts/generate_report.py
```
El reporte se depositará en `reports/inventory_report_YYYYMMDD_HHMMSS.csv` con codificación UTF-8.

---

## 📚 Documentación Técnica Adicional

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): Diagramas de secuencia, diseño de capas y trade-offs técnicos.
- [docs/RUNBOOK.md](docs/RUNBOOK.md): Guía operativa, procedimientos de emergencia y resolución de errores.
- [docs/AI_USAGE.md](docs/AI_USAGE.md): Transparencia del uso de IA, validación humana e incidentes reales resueltos.
- [docs/TESTING.md](docs/TESTING.md): Detalle exhaustivo de las 24 pruebas Pytest.

---

## 🔮 Limitaciones Actuales y Mejoras Futuras

1. **Autenticación y Autorización (RBAC):** Incorporar JWT para diferenciar roles de sucursal (cajero/repositor: solo lectura y actualización de stock; gerente de tienda: creación de catálogo y reportes).
2. **Escalabilidad Multi-sucursal:** Modelar la entidad `Store` / `Sucursal` y stock distribuido con soporte para traslados inter-depósito.
3. **Migración a PostgreSQL:** Sustituir SQLite en entornos de producción mediante PostgreSQL administrado en la nube (AWS RDS / GCP Cloud SQL).
4. **Pronóstico de Demanda Predictivo:** Integrar modelos de series temporales (ej. Prophet o XGBoost) para anticipar demanda estacional y feriados de retail.
5. **Notificaciones Push y Webhooks:** Alertas automáticas a canales de Slack / Teams para el equipo de logística al detectar artículos en `CRITICAL`.
