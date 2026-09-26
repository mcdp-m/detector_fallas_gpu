"""Contrato de datos de la telemetría (pandera).

Valida rangos físicos y estados válidos antes de entrenar.
Las filas que violan el contrato se descartan, no el episodio completo.
"""

import pandas as pd
import pandera.pandas as pa
from pandera.pandas import Check, Column, DataFrameSchema

ESTADOS_VALIDOS = [
    "normal",
    "sobrecalentamiento",
    "degradacion_memoria",
    "falla_alimentacion",
]

schema_telemetria = DataFrameSchema(
    {
        "episodio_id": Column(int, Check.greater_than_or_equal_to(0)),
        "segundo": Column(int, Check.greater_than_or_equal_to(0)),
        "temp_c": Column(float, Check.in_range(0, 110)),
        "power_w": Column(float, Check.in_range(0, 400)),
        "util_pct": Column(float, Check.in_range(0, 100)),
        "clock_mhz": Column(float, Check.greater_than(0)),
        "ecc_errors": Column(int, Check.greater_than_or_equal_to(0)),
        "estado": Column(str, Check.isin(ESTADOS_VALIDOS)),
    }
)


def validar_y_limpiar(df: pd.DataFrame) -> pd.DataFrame:
    """Devuelve el DataFrame sin las filas que violan el contrato."""
    try:
        return schema_telemetria.validate(df, lazy=True)
    except pa.errors.SchemaErrors as e:
        malas = e.failure_cases["index"].dropna().unique()
        return df.drop(index=malas).reset_index(drop=True)
