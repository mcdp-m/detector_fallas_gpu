"""API del detector de fallas de GPU.

POST /predecir recibe una ventana de telemetría (una lectura por segundo),
calcula las MISMAS features que en el entrenamiento (features.py) y responde
el estado predicho con su confianza.

La puerta es el BaseModel de pydantic: campos completos, tipos correctos,
rangos físicos y tamaño mínimo de ventana. Si no cumple, FastAPI responde
422 sin tocar el modelo.
"""

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

from config import RUTA_MODELO
from features import calcular_features

MIN_LECTURAS = 10


class Lectura(BaseModel):
    temp_c: float = Field(ge=0, le=110)
    power_w: float = Field(ge=0, le=400)
    util_pct: float = Field(ge=0, le=100)
    clock_mhz: float = Field(gt=0)
    ecc_errors: int = Field(ge=0)


class Ventana(BaseModel):
    lecturas: list[Lectura] = Field(min_length=MIN_LECTURAS)


app = FastAPI(title="Detector de fallas de GPU")
pipeline = joblib.load(RUTA_MODELO)


@app.post("/predecir")
def predecir(ventana: Ventana):
    df = pd.DataFrame([lectura.model_dump() for lectura in ventana.lecturas])
    X = pd.DataFrame([calcular_features(df)])
    estado = pipeline.predict(X)[0]
    confianza = float(pipeline.predict_proba(X).max())
    return {"estado_predicho": estado, "confianza": round(confianza, 4)}
