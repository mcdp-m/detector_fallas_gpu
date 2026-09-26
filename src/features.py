"""Cálculo de features por ventana de telemetría.

Usado tanto por el entrenamiento (train.py) como por la API (api.py):
misma función, mismas features.
"""

import pandas as pd

SENIALES = ["temp_c", "power_w", "util_pct", "clock_mhz", "ecc_errors"]

TAM_VENTANA = 30


def calcular_features(ventana: pd.DataFrame) -> dict:
    """Una ventana de telemetría -> diccionario de 20 features."""
    features = {}
    for senial in SENIALES:
        s = ventana[senial]
        features[f"{senial}_mean"] = s.mean()
        if senial != "ecc_errors":
            features[f"{senial}_std"] = s.std()
        features[f"{senial}_min"] = s.min()
        features[f"{senial}_max"] = s.max()
    features["ecc_errors_sum"] = ventana["ecc_errors"].sum()
    return features


def ventanear(df: pd.DataFrame, tam: int = TAM_VENTANA) -> pd.DataFrame:
    """Episodios de telemetría -> tabla de features por ventana con etiqueta.

    Una ventana nunca mezcla episodios distintos. Las ventanas no se solapan.
    Incluye episodio_id solo para poder hacer el split train/test por episodio;
    se descarta antes de entrenar, nunca es feature.
    """
    filas = []
    for episodio_id, episodio in df.groupby("episodio_id"):
        episodio = episodio.sort_values("segundo")
        for inicio in range(0, len(episodio) - tam + 1, tam):
            ventana = episodio.iloc[inicio : inicio + tam]
            features = calcular_features(ventana)
            features["episodio_id"] = episodio_id
            features["estado"] = episodio["estado"].iloc[0]
            filas.append(features)
    return pd.DataFrame(filas)
