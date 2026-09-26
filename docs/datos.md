# Entendimiento de los datos

Dataset: `data/telemetria_publica.csv` — 14.400 filas, 48 episodios de 300 segundos, 12 episodios por clase (balanceado).

## Columnas

| Columna | Qué es | Rango / valores observados |
|---|---|---|
| `episodio_id` | Tramo continuo de una GPU | 48 valores distintos (0-47). Identificador |
| `segundo` | Segundo dentro del episodio | 0-299. Identificador temporal |
| `temp_c` | Temperatura (°C) | 22.1 - 99.2 |
| `power_w` | Consumo (W) | -18.1 - 335.2. Hay valores negativos imposibles |
| `util_pct` | Utilización (%) | 0.0 - 100.0 |
| `clock_mhz` | Frecuencia del reloj (MHz) | 1022 - 2546 |
| `ecc_errors` | Errores ECC por segundo | 0 - 14 |
| `estado` | Etiqueta | 4 clases: normal, sobrecalentamiento, degradacion_memoria, falla_alimentacion. Es la `y` |

## Datos con problemas

3 filas con `power_w` negativa (físicamente imposible), todas en episodios de `falla_alimentacion`:

| episodio_id | segundo | power_w |
|---|---|---|
| 36 | 107 | -13.5 |
| 38 | 262 | -3.9 |
| 44 | 158 | -18.1 |

El resto del dataset está limpio: sin nulos, rangos físicos válidos, episodios completos.
