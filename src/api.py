"""API del detector de fallas de GPU.

POST /predecir recibe una ventana de telemetría (una lectura por segundo),
calcula las MISMAS features que en el entrenamiento (features.py) y responde
el estado predicho con su confianza.

La puerta es el BaseModel de pydantic: campos completos, tipos correctos,
rangos físicos y tamaño mínimo de ventana. Si no cumple, FastAPI responde
422 sin tocar el modelo.
"""

import os
import time

import joblib
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field

from config import RUTA_MODELO, VERSION
from features import calcular_features
from logger import log_evento, obtener_logger
from metrics import metricas

MIN_LECTURAS = 10
UMBRAL_LATENCIA_MS = float(os.environ.get("UMBRAL_LATENCIA_MS", 500))

log = obtener_logger()


class Lectura(BaseModel):
    temp_c: float = Field(ge=0, le=110)
    power_w: float = Field(ge=0, le=400)
    util_pct: float = Field(ge=0, le=100)
    clock_mhz: float = Field(gt=0)
    ecc_errors: int = Field(ge=0)


class Ventana(BaseModel):
    lecturas: list[Lectura] = Field(min_length=MIN_LECTURAS)


app = FastAPI(title="Detector de fallas de GPU", version=VERSION)
pipeline = joblib.load(RUTA_MODELO)
log_evento(log, "info", "servicio_iniciado", modelo_version=VERSION)


@app.middleware("http")
async def medir(request: Request, call_next):
    inicio = time.perf_counter()
    respuesta = await call_next(request)
    latencia_ms = round((time.perf_counter() - inicio) * 1000, 1)
    ok = respuesta.status_code < 400

    if request.url.path == "/predecir":
        metricas.registrar(latencia_ms, ok=ok)
        if latencia_ms > UMBRAL_LATENCIA_MS:
            log_evento(log, "warning", "latencia_alta",
                       ruta=request.url.path, latencia_ms=latencia_ms)

    respuesta.headers["X-Latencia-ms"] = str(latencia_ms)
    return respuesta


@app.exception_handler(RequestValidationError)
async def input_invalido(request: Request, exc: RequestValidationError):
    errores = exc.errors()
    primero = errores[0] if errores else {}
    # El error ya lo cuenta el middleware al ver el 422.
    log_evento(log, "error", "input_invalido",
               ruta=request.url.path, n_errores=len(errores),
               tipo=primero.get("type"),
               campo=".".join(str(p) for p in primero.get("loc", ())),
               mensaje=primero.get("msg"))
    return await request_validation_exception_handler(request, exc)


@app.post("/predecir")
def predecir(ventana: Ventana):
    inicio = time.perf_counter()
    df = pd.DataFrame([lectura.model_dump() for lectura in ventana.lecturas])
    X = pd.DataFrame([calcular_features(df)])
    estado = pipeline.predict(X)[0]
    confianza = round(float(pipeline.predict_proba(X).max()), 4)
    latencia_ms = round((time.perf_counter() - inicio) * 1000, 1)
    log_evento(log, "info", "prediccion",
               n_lecturas=len(ventana.lecturas), estado=estado,
               confianza=confianza, latencia_ms=latencia_ms,
               modelo_version=VERSION)
    return {"estado_predicho": estado, "confianza": confianza}


@app.get("/health")
def health():
    return {"status": "ok", "modelo_version": VERSION}


@app.get("/metrics")
def metrics():
    return metricas.resumen()
