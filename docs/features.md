# Features

## Filas corruptas

Se descartan **solo las filas** que violan el contrato (3 de 14.400), no el episodio ni la ventana. Tirar un episodio borraría 900 filas de `falla_alimentacion`, la clase donde la inestabilidad es la señal.

## Ventaneo

- Ventanas de **30 segundos, sin solape**, siempre dentro de un mismo `episodio_id`.
- Cada episodio de 300 s produce 10 ventanas → 48x10 muestras disponibles.
- La etiqueta de la ventana es el `estado` de su episodio.

## Features por ventana

20 features por ventana:

| Señal | mean | std | min | max | sum |
|---|---|---|---|---|---|
| temp_c | X | X | X | X | |
| power_w | X | X | X | X | |
| util_pct | X | X | X | X | |
| clock_mhz | X | X | X | X | |
| ecc_errors | X | | X | X | X |

`estado`, `segundo` y `episodio_id` nunca entran como features: el primero es la etiqueta y los otros dos son identificadores.

## Rangos de las features por clase

Rango (min-max) de cada feature por clase, sobre ventanas de 30 s:

| Feature | normal | sobrecalentamiento | degradacion_memoria | falla_alimentacion |
|---|---|---|---|---|
| temp_c_mean | 53.2-56.3 | **86.7-89.7** | 57.7-62.2 | 45.2-53.8 |
| temp_c_std | 2.7-5.2 | 2.2-4.2 | 3.7-7.1 | 4.3-10.8 |
| temp_c_min | 39.4-51.3 | **77.8-85.1** | 42.5-54.4 | 22.1-42.6 |
| temp_c_max | 58.4-68.7 | **91.1-99.2** | 63.6-80.9 | 57.2-77.8 |
| power_w_mean | 190.7-208.5 | **285.9-295.4** | 200.1-223.5 | 119.8-159.2 |
| power_w_std | 14.1-26.0 | 7.3-13.7 | 16.0-34.7 | 32.1-62.7 |
| power_w_min | 131.1-186.9 | 257.4-279.9 | 120.5-187.5 | **3.2-95.5** |
| power_w_max | 218.1-280.5 | 301.7-330.9 | 231.1-335.2 | 186.4-305.3 |
| util_pct_mean | 64.8-74.4 | **93.3-97.0** | 61.4-74.1 | 46.4-63.9 |
| util_pct_std | 8.5-15.9 | 2.8-4.8 | 9.1-18.8 | 16.3-31.5 |
| util_pct_min | 31.3-57.6 | **81.3-90.8** | 13.3-56.4 | 0.0-29.9 |
| util_pct_max | 82.0-100 | 98.8-100 | 81.6-100 | 75.8-100 |
| clock_mhz_mean | 2383.9-2414.3 | 2068.2-2134.8 | 2359.8-2396.5 | **1708.1-1875.2** |
| clock_mhz_std | 21.1-44.9 | 57.3-106.4 | 24.7-59.4 | **149.1-283.7** |
| clock_mhz_min | 2268-2374 | 1804-2026 | 2236-2338 | **1022-1564** |
| clock_mhz_max | 2436-2525 | 2185-2365 | 2410-2543 | 2015-2546 |
| ecc_errors_mean | 0.0-0.1 | 0.0-0.3 | **3.9-6.1** | 0.0-0.5 |
| ecc_errors_min | 0 | 0 | 0-3 | 0 |
| ecc_errors_max | 0-2 | 0-2 | **7-14** | 1-3 |
| ecc_errors_sum | 0-3 | 0-8 | **118-184** | 1-14 |
