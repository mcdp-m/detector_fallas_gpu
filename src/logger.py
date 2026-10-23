"""Logs estructurados en JSON por stdout.

La app solo emite; el entorno (terminal, Docker, Render) decide dónde caen.
"""

import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record):
        base = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname,
            "evento": record.getMessage(),
        }
        datos = getattr(record, "datos", None)
        if datos:
            base.update(datos)
        return json.dumps(base, ensure_ascii=False)


def obtener_logger(nombre="detector_gpu", nivel=logging.INFO):
    log = logging.getLogger(nombre)
    log.setLevel(nivel)
    if not log.handlers:  # uvicorn --reload reimporta el módulo
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(JsonFormatter())
        log.addHandler(h)
        log.propagate = False
    return log


def log_evento(log, nivel, evento, **campos):
    getattr(log, nivel)(evento, extra={"datos": campos})
