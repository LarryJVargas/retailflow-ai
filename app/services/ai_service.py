import json
import logging
from sqlalchemy.orm import Session

from app.config import get_settings
from app.schemas.ai import (
    GeminiRawResponse,
    InventoryAnalysisResponse,
    PriorityLevel,
    ProductRecommendation,
)
from app.schemas.inventory import InventoryItemResponse
from app.services.inventory_service import get_low_stock_products, get_out_of_stock_products

logger = logging.getLogger(__name__)


def _build_fallback_analysis(critical_items: list[InventoryItemResponse]) -> InventoryAnalysisResponse:
    """Genera un análisis de inventario alternativo y 100% determinista basado en reglas de negocio fijas.

    Se utiliza de forma transparente si la API de Gemini falla, no está configurada,
    devuelve JSON malformado o propone SKUs/cantidades inconsistentes con el backend.
    """
    recommendations: list[ProductRecommendation] = []

    for item in critical_items:
        if item.stock == 0:
            priority = PriorityLevel.CRITICAL
            explanation = (
                f"Producto '{item.name}' totalmente agotado. "
                "Reposición urgente requerida para reanudar disponibilidad comercial."
            )
        else:
            ratio = item.stock / item.minimum_stock if item.minimum_stock > 0 else 1.0
            if ratio <= 0.5:
                priority = PriorityLevel.HIGH
                explanation = (
                    f"Stock de '{item.name}' ({item.stock} u.) inferior al 50% del mínimo requerido "
                    f"({item.minimum_stock} u.). Alto riesgo de quiebre de inventario."
                )
            else:
                priority = PriorityLevel.MEDIUM
                explanation = (
                    f"Stock de '{item.name}' ({item.stock} u.) por debajo del umbral mínimo "
                    f"({item.minimum_stock} u.). Reposición preventiva recomendada."
                )

        recommendations.append(
            ProductRecommendation(
                sku=item.sku,
                explanation=explanation,
                priority=priority,
                suggested_quantity=item.suggested_restock,
            )
        )

    # Ordenar por criticidad: CRITICAL -> HIGH -> MEDIUM -> LOW
    priority_order = {
        PriorityLevel.CRITICAL: 0,
        PriorityLevel.HIGH: 1,
        PriorityLevel.MEDIUM: 2,
        PriorityLevel.LOW: 3,
    }
    recommendations.sort(key=lambda rec: priority_order.get(rec.priority, 99))

    return InventoryAnalysisResponse(
        source="fallback",
        model_used=None,
        summary=(
            f"Análisis determinista generado por motor de reglas del sistema para "
            f"{len(critical_items)} productos en estado crítico."
        ),
        total_critical_products=len(critical_items),
        recommendations=recommendations,
    )


def analyze_inventory(db: Session) -> InventoryAnalysisResponse:
    """Analiza los productos críticos de inventario utilizando Gemini API con fallback determinista.

    Garantías de seguridad y consistencia:
    1. Las cantidades finales son calculadas exclusivamente por el backend; Gemini solo sugiere priorización y contexto.
    2. Si Gemini inventa SKUs, modifica cantidades, devuelve JSON corrupto o arroja excepción de red/cuota,
       se retorna automáticamente una respuesta determinista (source='fallback').
    3. Nunca se muta la base de datos SQLite durante este proceso.
    """
    settings = get_settings()

    # 1. Obtener productos críticos del inventario (agotados y bajo stock)
    out_of_stock = get_out_of_stock_products(db)
    low_stock = get_low_stock_products(db)
    critical_items = out_of_stock + low_stock

    # Si no hay productos críticos, devolver respuesta saludable inmediata
    if not critical_items:
        return InventoryAnalysisResponse(
            source="fallback",
            model_used=None,
            summary="El inventario se encuentra en niveles saludables. No hay productos con stock bajo ni agotados.",
            total_critical_products=0,
            recommendations=[],
        )

    # Mapa de referencia para validación estricta post-IA
    backend_expected = {item.sku: item for item in critical_items}

    # 2. Si no hay API key configurada, recurrir inmediatamente al fallback determinista
    if not settings.gemini_api_key or not settings.gemini_api_key.strip():
        logger.info("GEMINI_API_KEY no configurada. Utilizando motor determinista de fallback.")
        return _build_fallback_analysis(critical_items)

    # 3. Invocar Gemini mediante google-genai
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.gemini_api_key)

        # Preparar payload mínimo necesario (sin datos personales ni sensibles)
        minimal_items = [
            {
                "sku": item.sku,
                "name": item.name,
                "category": item.category,
                "stock": item.stock,
                "minimum_stock": item.minimum_stock,
                "suggested_restock": item.suggested_restock,
            }
            for item in critical_items
        ]

        prompt = (
            "Eres un analista de inventario para RetailFlow AI. A continuación se presentan los productos que "
            "requieren reposición de inventario.\n\n"
            "DATOS DEL INVENTARIO CRÍTICO:\n"
            f"{json.dumps(minimal_items, ensure_ascii=False, indent=2)}\n\n"
            "INSTRUCCIONES ESTRICTAS:\n"
            "1. Debes respetar exactamente la cantidad en 'suggested_restock' para cada producto como 'suggested_quantity'. "
            "NO alteres ni recalcules las cantidades bajo ningún concepto.\n"
            "2. Solo genera recomendaciones para los SKUs presentes en la lista anterior. No inventes productos ni SKUs.\n"
            "3. Asigna a cada uno una prioridad ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW') y una breve justificación comercial en 'explanation'.\n"
            "4. Devuelve ÚNICAMENTE un objeto JSON válido con las claves:\n"
            "   - 'summary': Resumen ejecutivo en una o dos oraciones.\n"
            "   - 'recommendations': Lista de objetos con 'sku', 'explanation', 'priority' y 'suggested_quantity'."
        )

        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )

        raw_text = response.text or ""
        parsed_data = json.loads(raw_text)
        validated_gemini = GeminiRawResponse.model_validate(parsed_data)

        # 4. Validación de negocio estricta sobre la respuesta de Gemini
        verified_recommendations: list[ProductRecommendation] = []
        seen_skus: set[str] = set()

        for rec in validated_gemini.recommendations:
            # Validación anti-alucinación: El SKU debe existir en el lote enviado
            if rec.sku not in backend_expected:
                logger.warning("Gemini devolvió un SKU inexistente ('%s'). Activando fallback.", rec.sku)
                return _build_fallback_analysis(critical_items)

            # Validación de duplicados
            if rec.sku in seen_skus:
                logger.warning("Gemini devolvió un SKU duplicado ('%s'). Activando fallback.", rec.sku)
                return _build_fallback_analysis(critical_items)
            seen_skus.add(rec.sku)

            # Validación de cantidades: la IA no debe decidir ni alterar cantidades finales
            expected_item = backend_expected[rec.sku]
            if rec.suggested_quantity != expected_item.suggested_restock:
                logger.warning(
                    "Cantidad inconsistente para SKU '%s' (IA: %s vs Backend: %s). Activando fallback.",
                    rec.sku,
                    rec.suggested_quantity,
                    expected_item.suggested_restock,
                )
                return _build_fallback_analysis(critical_items)

            verified_recommendations.append(
                ProductRecommendation(
                    sku=rec.sku,
                    explanation=rec.explanation,
                    priority=rec.priority,
                    suggested_quantity=expected_item.suggested_restock,
                )
            )

        # Verificar que se hayan cubierto todos los SKUs críticos
        if len(verified_recommendations) != len(critical_items):
            logger.warning(
                "Gemini cubrió %s de %s productos críticos. Activando fallback.",
                len(verified_recommendations),
                len(critical_items),
            )
            return _build_fallback_analysis(critical_items)

        return InventoryAnalysisResponse(
            source="gemini",
            model_used=settings.gemini_model,
            summary=validated_gemini.summary,
            total_critical_products=len(verified_recommendations),
            recommendations=verified_recommendations,
        )

    except Exception as exc:
        # Registrar advertencia sin exponer secretos ni información sensible
        logger.warning(
            "Excepción durante el análisis de Gemini (%s). Activando fallback determinista de forma segura.",
            type(exc).__name__,
        )
        return _build_fallback_analysis(critical_items)
