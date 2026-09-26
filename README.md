# Detector de fallas de GPU

Clasifica el estado de una GPU NVIDIA L40 a partir de una ventana de telemetría (temperatura, potencia, utilización, reloj, errores ECC). Cuatro estados: `normal`, `sobrecalentamiento`, `degradacion_memoria`, `falla_alimentacion`.

El servicio es una API FastAPI empaquetada en Docker. El modelo (RandomForest sobre features de ventanas de 30 s) viaja entrenado dentro de la imagen.

## Ejecutar con Docker

```bash
docker build -t detector-gpu .
docker run -p 8000:8000 detector-gpu
```

Documentación en http://localhost:8000/docs

## Uso de la API

`POST /predecir` recibe una ventana de telemetría (mínimo 10 lecturas, una por segundo).

Respuesta:

```json
{"estado_predicho": "sobrecalentamiento", "confianza": 0.98}
```

Petición inválida (campos faltantes, tipos o rangos físicos incorrectos, menos de 10 lecturas): 422 sin tocar el modelo.

## Estructura

```
src/
  config.py     # rutas de datos y modelo
  schema.py     # contrato de datos (pandera) para el entrenamiento
  features.py   # ventaneo y cálculo de features (usado por train.py y api.py)
  train.py      # entrena y serializa el pipeline
  api.py        # API FastAPI (validación con BaseModel + /predecir)
data/           # telemetría cruda (no va en la imagen)
models/         # modelo.joblib serializado (sí va en la imagen)
docs/           # entendimiento de datos y decisiones de features
```

## Ejemplos

Ventana válida de operación normal (respuesta esperada: `normal`):

```json
{
  "lecturas": [
    {"temp_c": 56.2, "power_w": 234.5, "util_pct": 76.2, "clock_mhz": 2412, "ecc_errors": 0},
    {"temp_c": 50.8, "power_w": 169.3, "util_pct": 63.1, "clock_mhz": 2403, "ecc_errors": 0},
    {"temp_c": 58.0, "power_w": 217.3, "util_pct": 85.3, "clock_mhz": 2396, "ecc_errors": 0},
    {"temp_c": 58.8, "power_w": 193.4, "util_pct": 62.5, "clock_mhz": 2448, "ecc_errors": 0},
    {"temp_c": 47.2, "power_w": 198.8, "util_pct": 62.4, "clock_mhz": 2381, "ecc_errors": 0},
    {"temp_c": 49.8, "power_w": 178.9, "util_pct": 76.5, "clock_mhz": 2462, "ecc_errors": 0},
    {"temp_c": 55.5, "power_w": 193.3, "util_pct": 79.2, "clock_mhz": 2393, "ecc_errors": 0},
    {"temp_c": 53.7, "power_w": 226.0, "util_pct": 75.4, "clock_mhz": 2362, "ecc_errors": 0},
    {"temp_c": 54.9, "power_w": 211.7, "util_pct": 49.8, "clock_mhz": 2402, "ecc_errors": 0},
    {"temp_c": 51.6, "power_w": 234.6, "util_pct": 76.5, "clock_mhz": 2368, "ecc_errors": 0}
  ]
}
```

Ventana válida de degradación de memoria (respuesta esperada: `degradacion_memoria`):

```json
{
  "lecturas": [
    {"temp_c": 62.5, "power_w": 234.3, "util_pct": 92.9, "clock_mhz": 2381, "ecc_errors": 2},
    {"temp_c": 63.4, "power_w": 238.6, "util_pct": 73.7, "clock_mhz": 2338, "ecc_errors": 3},
    {"temp_c": 59.3, "power_w": 182.8, "util_pct": 55.6, "clock_mhz": 2393, "ecc_errors": 2},
    {"temp_c": 54.4, "power_w": 215.1, "util_pct": 61.2, "clock_mhz": 2390, "ecc_errors": 10},
    {"temp_c": 56.9, "power_w": 190.7, "util_pct": 51.3, "clock_mhz": 2327, "ecc_errors": 9},
    {"temp_c": 58.1, "power_w": 182.2, "util_pct": 61.7, "clock_mhz": 2368, "ecc_errors": 6},
    {"temp_c": 60.1, "power_w": 214.1, "util_pct": 90.5, "clock_mhz": 2395, "ecc_errors": 5},
    {"temp_c": 68.0, "power_w": 199.7, "util_pct": 65.7, "clock_mhz": 2377, "ecc_errors": 5},
    {"temp_c": 64.5, "power_w": 205.8, "util_pct": 49.3, "clock_mhz": 2302, "ecc_errors": 7},
    {"temp_c": 55.9, "power_w": 197.5, "util_pct": 74.0, "clock_mhz": 2354, "ecc_errors": 6}
  ]
}
```

Ventana válida de falla de alimentación (respuesta esperada: `falla_alimentacion`):

```json
{
  "lecturas": [
    {"temp_c": 55.0, "power_w": 171.9, "util_pct": 66.4, "clock_mhz": 2125, "ecc_errors": 0},
    {"temp_c": 49.9, "power_w": 173.1, "util_pct": 82.7, "clock_mhz": 2048, "ecc_errors": 1},
    {"temp_c": 50.4, "power_w": 190.5, "util_pct": 53.7, "clock_mhz": 1826, "ecc_errors": 0},
    {"temp_c": 59.1, "power_w": 118.4, "util_pct": 62.6, "clock_mhz": 1124, "ecc_errors": 1},
    {"temp_c": 50.8, "power_w": 186.3, "util_pct": 38.0, "clock_mhz": 1752, "ecc_errors": 0},
    {"temp_c": 62.6, "power_w": 237.5, "util_pct": 100.0, "clock_mhz": 1599, "ecc_errors": 0},
    {"temp_c": 49.8, "power_w": 141.3, "util_pct": 43.7, "clock_mhz": 1759, "ecc_errors": 0},
    {"temp_c": 38.0, "power_w": 145.3, "util_pct": 49.7, "clock_mhz": 1730, "ecc_errors": 0},
    {"temp_c": 42.9, "power_w": 170.5, "util_pct": 60.2, "clock_mhz": 1737, "ecc_errors": 0},
    {"temp_c": 44.2, "power_w": 42.5, "util_pct": 71.7, "clock_mhz": 2015, "ecc_errors": 0}
  ]
}
```

Ventana válida de sobrecalentamiento (10 lecturas reales, respuesta esperada: `sobrecalentamiento`):

```json
{
  "lecturas": [
    {"temp_c": 88.3, "power_w": 296.5, "util_pct": 95.8, "clock_mhz": 2038, "ecc_errors": 0},
    {"temp_c": 89.8, "power_w": 298.9, "util_pct": 95.4, "clock_mhz": 2091, "ecc_errors": 0},
    {"temp_c": 84.6, "power_w": 284.7, "util_pct": 91.8, "clock_mhz": 2043, "ecc_errors": 0},
    {"temp_c": 89.2, "power_w": 297.3, "util_pct": 92.3, "clock_mhz": 2053, "ecc_errors": 0},
    {"temp_c": 85.8, "power_w": 288.9, "util_pct": 92.2, "clock_mhz": 2305, "ecc_errors": 0},
    {"temp_c": 87.6, "power_w": 301.5, "util_pct": 88.6, "clock_mhz": 2080, "ecc_errors": 0},
    {"temp_c": 93.1, "power_w": 310.3, "util_pct": 95.6, "clock_mhz": 2122, "ecc_errors": 0},
    {"temp_c": 83.8, "power_w": 279.1, "util_pct": 94.8, "clock_mhz": 2119, "ecc_errors": 0},
    {"temp_c": 87.2, "power_w": 297.7, "util_pct": 98.0, "clock_mhz": 2147, "ecc_errors": 0},
    {"temp_c": 84.2, "power_w": 303.0, "util_pct": 100.0, "clock_mhz": 2062, "ecc_errors": 0}
  ]
}
```

Ventana de solo 3 lecturas (respuesta esperada: 422, `too_short`):

```json
{
  "lecturas": [
    {"temp_c": 56.2, "power_w": 234.5, "util_pct": 76.2, "clock_mhz": 2412, "ecc_errors": 0},
    {"temp_c": 50.8, "power_w": 169.3, "util_pct": 63.1, "clock_mhz": 2403, "ecc_errors": 0},
    {"temp_c": 58.0, "power_w": 217.3, "util_pct": 85.3, "clock_mhz": 2396, "ecc_errors": 0}
  ]
}
```

Temperatura Fahrenheit (respuesta esperada: 422, `temp_c` debe ser ≤ 110):

```json
{
  "lecturas": [
    {"temp_c": 133.2, "power_w": 234.5, "util_pct": 76.2, "clock_mhz": 2412, "ecc_errors": 0},
    {"temp_c": 123.4, "power_w": 169.3, "util_pct": 63.1, "clock_mhz": 2403, "ecc_errors": 0},
    {"temp_c": 136.4, "power_w": 217.3, "util_pct": 85.3, "clock_mhz": 2396, "ecc_errors": 0},
    {"temp_c": 137.8, "power_w": 193.4, "util_pct": 62.5, "clock_mhz": 2448, "ecc_errors": 0},
    {"temp_c": 117.0, "power_w": 198.8, "util_pct": 62.4, "clock_mhz": 2381, "ecc_errors": 0},
    {"temp_c": 121.6, "power_w": 178.9, "util_pct": 76.5, "clock_mhz": 2462, "ecc_errors": 0},
    {"temp_c": 131.9, "power_w": 193.3, "util_pct": 79.2, "clock_mhz": 2393, "ecc_errors": 0},
    {"temp_c": 128.7, "power_w": 226.0, "util_pct": 75.4, "clock_mhz": 2362, "ecc_errors": 0},
    {"temp_c": 130.8, "power_w": 211.7, "util_pct": 49.8, "clock_mhz": 2402, "ecc_errors": 0},
    {"temp_c": 124.9, "power_w": 234.6, "util_pct": 76.5, "clock_mhz": 2368, "ecc_errors": 0}
  ]
}
```
