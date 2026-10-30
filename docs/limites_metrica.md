# Límites de la métrica de evaluación

## Qué mide

Coincidencia de palabras (precisión, cobertura y F1, contando repeticiones)
entre la respuesta del modelo y una referencia escrita por mí, después de
pasar ambos textos por `procesar_texto` (minúsculas, sin puntuación).
No mide significado, ni orden, ni si un dato es verdadero.

## Modos de falla conocidos

Observados en mi revisión (falsos negativos: respuesta correcta, F1 bajo):

- **Relleno y verbosidad.** El modelo agrega frases como "Según el fragmento
  proporcionado" o cita la descripción completa; baja la precisión.
  Ejemplo: "¿Qué columnas sí tienen descripción?", F1 0.417, respuesta correcta.
- **Paráfrasis.** Mismo significado con otras palabras.
  Ejemplo: "¿Para qué sirve id_venta?", F1 0.316 ("identifica de forma única"
  vs "identificador único"). Otro: "¿Qué tests tiene fact_ventas?", F1 0.421
  ("no define tests" vs "no tiene ningún test definido").
- **Números escritos distinto.** "dos" y "2" cuentan como palabras distintas.
  Ejemplo: "¿Cuántas columnas tiene fact_ventas?", F1 0.526, respuesta correcta.
- **Respuestas del tipo "el fragmento no dice X".** Es la conducta deseada
  (no inventar), pero puntúa bajo o medio (0.49 a 0.74), porque el modelo
  explica por qué.
  Ejemplo: "¿De qué tabla sale la métrica de ingresos netos?", F1 0.486.

No observados en esta muestra, pero posibles por construcción (falsos
positivos): dato equivocado con el resto de la oración igual, y negación
omitida. Quedan documentados con pruebas en `test_pipeline_texto.py`
(`test_metricas_limite_dato_equivocado_puntua_alto`,
`test_metricas_limite_negacion_casi_no_se_nota`).

## Muestra revisada

12 de 20 respuestas, revisadas a mano con la rúbrica de tres preguntas
(corrección factual, completitud, contradicción): los 5 con menor F1, los 5
con mayor F1 y 2 del medio elegidos por riesgo (una negación y un número).
Fecha: 2026-10-30. Limitación: las 20 consultas usan un único fragmento
pequeño de schema.yml y referencias cortas escritas por mí.
Resultado: 12 de 12 respuestas correctas; el F1 no refleja errores reales.

## Recomendación de uso

Usar el F1 para comparar versiones del cliente o del prompt en volumen, no
para decidir si una respuesta es correcta: en esta muestra un F1 bajo
significó verbosidad o paráfrasis, no error. Revisar siempre a mano las
respuestas con cifras, fechas, nombres o negaciones, y las de tipo "no está
en el fragmento". Antes de cambiar el prompt para subir el F1, leer los casos.