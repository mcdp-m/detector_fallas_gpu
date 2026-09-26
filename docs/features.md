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
