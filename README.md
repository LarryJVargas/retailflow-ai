# RetailFlow AI - Sistema Full Stack de Gestión Inteligente de Inventario

[![Python 3.12](https://img.shields.io/badge/Python-3.12.2-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.165.0-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.3.1-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7.3-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-6.1.0-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4.17-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.1.9-red.svg?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Google Gemini API](https://img.shields.io/badge/Google%20GenAI-gemini--3.5--flash-8E24AA.svg?logo=google&logoColor=white)](https://ai.google.dev/)
[![Tests Passing](https://img.shields.io/badge/Pytest-24%2F24%20Passed-brightgreen.svg?logo=pytest&logoColor=white)](docs/TESTING.md)

**RetailFlow AI** es una plataforma Full Stack de gestión inteligente de inventario y optimización de abastecimiento para el sector retail. Diseñada con un enfoque de arquitectura híbrida y defensiva, combina el cálculo determinista de reglas de inventario en Python con la capacidad analítica y contextual de **Google Gemini API** (`gemini-3.5-flash`), incorporando mitigación de alucinaciones mediante validaciones en el backend y un mecanismo de fallback determinista.

---

## 🏬 Propósito y Problema de Negocio en Retail

En la gestión de inventarios para supermercados, hipermercados y cadenas de consumo masivo, el descalce entre la demanda y el stock disponible genera dos contingencias de alto impacto operativo:
1. **Quiebre de Stock en Góndola (*Stockout*):** Falta física de producto que causa pérdida directa de ingresos, insatisfacción del consumidor y daño a la fidelidad del cliente.
2. **Sobrestock y Capital Inmovilizado:** Exceso de mercadería en depósitos de sucursal que satura el espacio físico, eleva el riesgo de mermas/vencimientos e inmoviliza capital operativo.

**RetailFlow AI** aborda este desafío a través de una **arquitectura Full Stack híbrida y defensiva**:
- **Cálculo Determinista Backend:** Las cantidades sugeridas de reposición se calculan exclusivamente mediante reglas deterministas en el backend:
  $$\text{suggested\_restock} = \max(\text{minimum\_stock} - \text{stock}, 0)$$
  La IA no define ni modifica las cantidades finales.
- **Análisis Contextual con IA:** **Google Gemini API** (`gemini-3.5-flash`) aporta contextualización operativa y prioriza la urgencia de reposición (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
- **Resiliencia Operativa:** Ante contingencias de red, límites de cuota o respuestas no válidas de la IA, el sistema activa automáticamente un **fallback determinista** local con `source="fallback"`.
- **Frontend SaaS Reactivo:** Dashboard y panel de control de inventario construido con React, Vite, TypeScript y Tailwind CSS.

---

## 📸 Capturas de Pantalla de la Aplicación

> Las capturas reales de la interfaz se almacenan en el directorio [`docs/screenshots/`](docs/screenshots/). A continuación se presenta el mapeo de vistas implementadas:

| Vista | Descripción de la Interfaz | Ubicación de Captura |
| :--- | :--- | :--- |
| **Dashboard Principal** | Tarjetas de indicadores cuantitativos (Total, Saludables, Bajo Stock, Agotados) y alerta operativa de reaprovisionamiento. | `docs/screenshots/01_dashboard.png` |
| **Catálogo de Productos** | Tabla de productos con badges de estado, búsqueda en tiempo real, filtros por categoría/estado y acciones CRUD. | `docs/screenshots/02_catalogo_productos.png` |
| **Inventario Crítico** | Vista dividida de artículos agotados y con bajo stock con columna de reposición calculada por el backend. | `docs/screenshots/03_inventario_critico.png` |
| **Análisis Gemini AI** | Panel de diagnóstico con badge de procedencia (`Gemini AI` vs `Fallback`), resumen ejecutivo y tarjetas de recomendación priorizadas. | `docs/screenshots/04_analisis_gemini.png` |

---

## 🛠️ Stack Tecnológico Completo

### Frontend
- **React 18.3.1 + TypeScript 5.7.3:** Tipado estricto para componentes, DTOs y llamadas API.
- **Vite 6.1.0:** Entorno de desarrollo y empaquetador con soporte HMR y compilación de producción optimizada.
- **Tailwind CSS 3.4.17:** Diseño de interfaz SaaS responsivo (desktop, tablet y móvil).
- **Lucide React 0.475.0:** Iconografía profesional para retail y métricas.
- **Fetch API nativo:** Cliente HTTP centralizado sin dependencias pesadas innecesarias.

### Backend
- **Python 3.12.2:** Entorno de ejecución de última generación con tipado fuerte.
- **FastAPI 0.165.0:** API REST asíncrona, validación automática mediante Pydantic v2 y documentación OpenAPI interactiva.
- **SQLAlchemy 2.1.9:** ORM declarativo moderno (`Mapped`, `mapped_column`, consultas tipadas `select()`).
- **SQLite:** Base de datos relacional ligera (`retailflow.db`) para portabilidad total.
- **Google GenAI SDK (`google-genai`):** Cliente oficial de Google para inferencia con el modelo `gemini-3.5-flash`.
- **Pydantic v2 & Pydantic-Settings:** Validación exhaustiva de contratos y configuración segura de variables de entorno.
- **Pytest 9.2.0 + HTTPX:** 24 pruebas automatizadas sobre base de datos en memoria (`sqlite:///:memory:`) con `StaticPool` y mocks de IA.

---

## 📐 Arquitectura Full Stack y Comunicación

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)                  │
│                     http://localhost:5173                   │
│                                                             │
│   Dashboard  •  Catálogo  •  Inventario Crítico  •  Gemini  │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / JSON (Fetch API)
                               │ CORS Permitido: [5173, 3000]
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI + Uvicorn)               │
│                     http://localhost:8000                   │
│                                                             │
│  [Routers] ──► [Services Layer] ──► [Pydantic v2 Schemas]   │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               │ SQLAlchemy 2.0 ORM           │ google-genai SDK
               ▼                              ▼
┌──────────────────────────────┐  ┌───────────────────────────┐
│     SQLite (retailflow.db)   │  │   Google Gemini API       │
│      Catálogo e Inventario   │  │    (gemini-3.5-flash)     │
└──────────────────────────────┘  └───────────────────────────┘
```

El flujo de comunicación respeta las siguientes premisas:
1. **Frontend Desacoplado:** El cliente web consume la URL del backend a través de `VITE_API_BASE_URL`.
2. **CORS Controlado:** FastAPI autoriza únicamente las solicitudes provenientes de orígenes locales de desarrollo.
3. **Cero Exposición de Secretos:** `GEMINI_API_KEY` reside exclusivamente en el archivo `.env` del backend y **nunca** se envía al frontend ni a logs.
4. **Mitigación de Alucinaciones mediante Validaciones:** El backend intercepta la respuesta de Gemini, verifica la existencia de SKUs, rechaza duplicados y audita que las cantidades sugeridas coincidan exactamente con el cálculo del backend antes de entregarlas al frontend.

Para un análisis técnico profundo de las capas, consulta [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## 💻 Instalación y Puesta en Marcha

### Requisitos Previos
- **Python 3.12.x** y **Node.js 20+ / 24+** instalados en el sistema.
- **Git** para clonar el repositorio.

---

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/<tu-usuario>/retailflow-ai.git
cd retailflow-ai
```

---

### Paso 2: Configurar e Iniciar el Backend

1. Crear y activar el entorno virtual de Python:

   **En Windows (PowerShell):**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   *(Si PowerShell restringe la ejecución de scripts en tu equipo, habilítala para la sesión actual con: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`)*.

   **En Linux / macOS (Bash/Zsh):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Instalar dependencias del backend:
   ```bash
   pip install -r requirements.txt
   ```

3. Configurar variables de entorno del backend:
   - En Windows (PowerShell): `Copy-Item .env.example .env`
   - En Linux / macOS: `cp .env.example .env`

   Editar el archivo `.env` resultante para configurar tu clave de Gemini:
   ```env
   APP_NAME="RetailFlow AI"
   APP_ENV="development"
   DEBUG=True
   DATABASE_URL="sqlite:///./retailflow.db"

   # Gemini AI Configuration
   GEMINI_API_KEY=""
   GEMINI_MODEL="gemini-3.5-flash"
   ```
   *(Nota: Si `GEMINI_API_KEY` se deja vacía o sin configurar, el sistema operará automáticamente utilizando el motor de fallback determinista local sin arrojar errores).*

4. Iniciar el servidor FastAPI (Uvicorn):
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   - API Base: `http://localhost:8000`
   - Documentación Interactiva Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

---

### Paso 3: Configurar e Iniciar el Frontend

1. Abrir **otra terminal** y posicionarse en la carpeta `frontend/`:
   ```bash
   cd frontend
   ```

2. Instalar dependencias de Node.js:
   ```bash
   npm install
   ```

3. Configurar variables de entorno del frontend:
   - En Windows (PowerShell): `Copy-Item .env.example .env`
   - En Linux / macOS: `cp .env.example .env`

   *(Contenido por defecto en `.env`: `VITE_API_BASE_URL=http://localhost:8000`)*.

4. Iniciar el servidor de desarrollo de Vite:
   ```bash
   npm run dev
   ```
   - Abrir en el navegador: **`http://localhost:5173`**

5. (Opcional) Compilar para producción:
   ```bash
   npm run build
   ```

---

## 📌 Tabla de Endpoints de la API

### Catálogo y CRUD (`/products`)
| Método | Endpoint | Descripción | Códigos HTTP |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Chequeo de estado y ambiente de la aplicación | `200` |
| `GET` | `/products` | Listado paginado de productos (`skip`, `limit`) | `200` |
| `GET` | `/products/{id}` | Obtención de detalle de un producto por ID | `200`, `404` |
| `POST` | `/products` | Creación de producto (valida SKU único y valores no negativos) | `201`, `409`, `422` |
| `PATCH` | `/products/{id}` | Actualización parcial de atributos de producto | `200`, `404`, `409`, `422` |
| `DELETE` | `/products/{id}` | Eliminación física de un producto | `204`, `404` |

### Control de Inventario (`/inventory`)
| Método | Endpoint | Descripción | Códigos HTTP |
| :--- | :--- | :--- | :--- |
| `GET` | `/inventory/summary` | Resumen cuantitativo del inventario (categorías mutuamente excluyentes) | `200` |
| `GET` | `/inventory/low-stock` | Productos con existencia positiva pero inferior al mínimo | `200` |
| `GET` | `/inventory/out-of-stock` | Productos con stock agotado (`stock == 0`) | `200` |
| `GET` | `/inventory/report` | Descarga de archivo CSV con productos críticos | `200` |

### Análisis Inteligente con IA (`/ai`)
| Método | Endpoint | Descripción | Códigos HTTP |
| :--- | :--- | :--- | :--- |
| `POST` | `/ai/analyze-inventory` | Análisis de inventario crítico mediante Gemini o Fallback Determinista | `200` |

---

## 🤖 Ejemplo de Análisis de Inventario

### Respuesta Exitosa vía Gemini (`gemini-3.5-flash`)
```json
{
  "source": "gemini",
  "model_used": "gemini-3.5-flash",
  "summary": "Se detectaron 2 artículos críticos con riesgo inminente de quiebre en góndola. Se sugiere reposición inmediata de productos básicos de alta rotación.",
  "total_critical_products": 2,
  "recommendations": [
    {
      "sku": "LECHE-ENT-001",
      "explanation": "Artículo de primera necesidad totalmente agotado. Pérdida inmediata de ventas y daño a la experiencia del cliente.",
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

### Respuesta con Fallback Determinista (Sin API Key o contingencia)
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

La suite cuenta con **24 pruebas unitarias e integradoras** ejecutables con Pytest desde la raíz del proyecto (con el entorno virtual activo):

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

- **1 prueba en `test_health.py`:** Verificación de salud y configuración.
- **12 pruebas en `test_products.py`:** CRUD completo, unicidad de SKU, códigos 404, 409 y validaciones Pydantic 422.
- **4 pruebas en `test_inventory.py`:** Métricas mutuamente excluyentes, bordes con `minimum_stock = 0`, reporte CSV y guardado en disco.
- **7 pruebas en `test_ai.py`:** Simulación de respuestas exitosas con mocks, detección de JSON inválido, rechazo de SKUs inventados, detección de cantidades alteradas por IA y fallbacks por error de API.

Consulta el desglose completo en [docs/TESTING.md](docs/TESTING.md).

---

## 📑 Automatización de Reportes (CLI Script)

Para exportar el reporte CSV de inventario crítico sin necesidad de iniciar el servidor web ni el navegador, ejecuta desde la raíz:

```bash
python scripts/generate_report.py
```
*(En Linux/macOS: `python3 scripts/generate_report.py`)*

El archivo generado se deposita en la carpeta `reports/` relativa a la raíz: `reports/inventory_report_YYYYMMDD_HHMMSS.csv` (directorio ignorado por Git).

---

## 📚 Documentación Técnica Detallada

- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md):** Diagramas de secuencia Mermaid, capas del sistema, separación de responsabilidades y trade-offs técnicos.
- **[docs/RUNBOOK.md](docs/RUNBOOK.md):** Guía operativa integral, comandos de inicio/parada, resolución de errores (401, 403, 404, 429, CORS) y verificación segura de credenciales.
- **[docs/AI_USAGE.md](docs/AI_USAGE.md):** Transparencia del uso de IA asistida vs. validación humana, registro de incidentes reales resueltos y mitigación de alucinaciones.
- **[docs/TESTING.md](docs/TESTING.md):** Inventario detallado de las 24 pruebas Pytest, estrategia de mocks y verificación de build de Vite.

---

## 🔮 Limitaciones Actuales y Mejoras Futuras

1. **Autenticación y Control de Acceso (RBAC):** Implementación de JWT para distinguir roles de sucursal (repositor/cajero con permisos de lectura y ajuste de stock vs. gerente de tienda con administración de catálogo y reportes).
2. **Escalabilidad Multi-Sucursal:** Modelar la entidad `Store` y soporte para stock distribuido y transferencias entre depósitos.
3. **Migración a Base de Datos de Producción:** Transición transparente de SQLite a PostgreSQL alojado en la nube (AWS RDS / GCP Cloud SQL) modificando únicamente la variable `DATABASE_URL`.
4. **Pronóstico de Demanda Predictivo:** Integración de modelos de series temporales (ej. Prophet o XGBoost) para anticipar picos de demanda estacional y fines de semana.
5. **Alertas Push Automatizadas:** Integración de webhooks para alertar a canales de Slack / Microsoft Teams cuando se detecten artículos en estado `CRITICAL`.
