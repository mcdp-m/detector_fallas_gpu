"""Entrena el clasificador de estados de GPU y serializa el pipeline.

Flujo: cargar -> validar contrato -> ventanear -> split por episodio -> entrenar -> joblib.
El split es por episodio (no por ventana) para que ventanas del mismo episodio
no queden repartidas entre train y test (fuga).
"""

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from config import RUTA_DATOS, RUTA_MODELO
from features import ventanear
from schema import validar_y_limpiar


def main():
    df = validar_y_limpiar(pd.read_csv(RUTA_DATOS))
    tabla = ventanear(df)

    episodios = tabla[["episodio_id", "estado"]].drop_duplicates()
    ep_train, ep_test = train_test_split(
        episodios, test_size=0.25, stratify=episodios["estado"], random_state=42
    )

    train = tabla[tabla["episodio_id"].isin(ep_train["episodio_id"])]
    test = tabla[tabla["episodio_id"].isin(ep_test["episodio_id"])]

    X_train = train.drop(columns=["estado", "episodio_id"])
    y_train = train["estado"]
    X_test = test.drop(columns=["estado", "episodio_id"])
    y_test = test["estado"]

    pipeline = Pipeline(
        [("modelo", RandomForestClassifier(n_estimators=100, random_state=42))]
    )
    pipeline.fit(X_train, y_train)

    print(f"ventanas train: {len(train)}, test: {len(test)}")
    print(f"accuracy test: {pipeline.score(X_test, y_test):.3f}")

    RUTA_MODELO.parent.mkdir(exist_ok=True)
    joblib.dump(pipeline, RUTA_MODELO)
    print(f"modelo serializado en {RUTA_MODELO}")


if __name__ == "__main__":
    main()
