"""Métricas en memoria de la API: tráfico, errores y latencia (p50/p95).

Se resetean al reiniciar el servicio. El Lock es necesario porque uvicorn
atiende peticiones concurrentes.
"""

from threading import Lock


class RegistroMetricas:
    def __init__(self):
        self._lock = Lock()
        self.requests_total = 0
        self.errores_total = 0
        self.latencias_ms = []

    def registrar(self, latencia_ms, ok=True):
        with self._lock:
            self.requests_total += 1
            if not ok:
                self.errores_total += 1
            self.latencias_ms.append(latencia_ms)

    def _percentil(self, datos, p):
        if not datos:
            return 0.0
        datos = sorted(datos)
        k = max(0, min(len(datos) - 1, int(round(p / 100 * len(datos))) - 1))
        return round(datos[k], 1)

    def resumen(self):
        with self._lock:
            total = self.requests_total
            errores = self.errores_total
            lat = list(self.latencias_ms)
        return {
            "requests_total": total,
            "errores_total": errores,
            "tasa_error_pct": round(errores / total * 100, 1) if total else 0.0,
            "latencia_p50_ms": self._percentil(lat, 50),
            "latencia_p95_ms": self._percentil(lat, 95),
            "latencia_media_ms": round(sum(lat) / len(lat), 1) if lat else 0.0,
        }


metricas = RegistroMetricas()
