"""Configuración centralizada del rate limiter (SlowAPI) para RetailFlow AI.

El limiter se instancia una sola vez como módulo y se importa tanto en
app/main.py (para registrar el handler de 429) como en los routers que
necesitan aplicar límites.

Extracción de IP:
  En desarrollo, se usa request.client.host directamente.
  En producción detrás de un proxy reverso (Render, Nginx, AWS ALB), el IP real
  del cliente llega en el header X-Forwarded-For. Esta función extrae el primer
  valor de la cadena (el IP más cercano al cliente original).

Almacenamiento:
  Se usa almacenamiento en memoria (MemoryStorage). Es suficiente para un
  despliegue de instancia única en Render (plan gratuito). No persiste entre
  reinicios del servidor, lo cual es aceptable para rate limiting de demo pública.
  Para producción con múltiples instancias o alta disponibilidad, sustituir por
  RedisStorage (requiere instancia Redis separada).
"""

from fastapi import Request
from slowapi import Limiter


def get_real_ip(request: Request) -> str:
    """Extrae el IP real del cliente respetando el header X-Forwarded-For.

    Render y la mayoría de proxies reversos insertan el IP original del cliente
    en X-Forwarded-For. Se toma el primer valor de la lista (cliente original)
    para evitar que un cliente malicioso inyecte una IP arbitraria al final.
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Formato: "client, proxy1, proxy2" — tomar el primer valor
        return forwarded_for.split(",")[0].strip()
    # Desarrollo local sin proxy: usar la conexión directa
    return request.client.host if request.client else "127.0.0.1"


# Instancia global del limiter — importar desde aquí en todos los routers
limiter = Limiter(key_func=get_real_ip)
