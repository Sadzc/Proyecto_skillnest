# Decisión de arquitectura: elección de modelo

## Modelo elegido

**Gemini 3.6 Flash**, para la funcionalidad principal de la miniaplicación RAG.

## Diagrama de arquitectura

![Diagrama de arquitectura de la miniaplicación](./diagrama_arquitectura.png)

El flujo completo va desde la pregunta del usuario hasta la respuesta final, pasando por `armar_peticion`, `enviar_peticion` (con la credencial `GEMINI_API_KEY` leída desde `.env` y el manejo de errores en `try/except`) y `extraer_texto`, con el costo calculado a partir de `usageMetadata`. El diagrama está en `docs/diagrama_arquitectura.png`.

## Comparación de candidatos

| Criterio | Gemini 3.6 Flash | Gemini 3.5 Flash |
| :--- | :--- | :--- |
| Costo por 1M tokens de entrada | $0.0375 USD | $0.075 USD |
| Costo por 1M tokens de salida | $0.15 USD | $0.30 USD |
| Latencia promedio observada (preguntas 1 y 2) | 6.22 segundos | 6.48 segundos |
| Costo promedio por pregunta (preguntas 1 y 2) | $0.000116 USD | $0.000239 USD |
| Calidad de respuesta para el caso | Buena: una sola frase clara en la pregunta 1; en la 2, YAML correcto con las dos columnas, más tests `unique` y `not_null` y la nota sobre `data_tests` vs `tests`. | Buena: una sola frase clara en la pregunta 1; en la 2, YAML correcto con las dos columnas, más simple y sin tests. |
| Fecha de medición | 2026-10-21 | 2026-10-21 |

Nota: la comparación usa solo las preguntas 1 y 2 de dos corridas (4 mediciones por modelo), porque son las únicas respondidas por ambos modelos en las dos corridas.

## Justificación

La miniaplicación responde dudas puntuales de analistas de negocio sobre tablas y métricas, aplicando RAG sobre la documentación de dbt. El criterio que más pesó fue el costo: 3.6 Flash cuesta la mitad por token y salió unas 2 veces más barato por consulta, con una latencia equivalente. La calidad es suficiente para el caso: las respuestas son claras, correctas y cumplen el formato pedido, y el mayor detalle que pudiera ofrecer otro modelo no es un requisito de esta aplicación.

## Alternativa descartada y por qué

Se descartó **Gemini 3.5 Flash**. Sus respuestas son comparables en calidad, pero cuesta el doble por consulta sin una ventaja de latencia ni de calidad que lo justifique para un asistente de preguntas puntuales.

También se intentó evaluar **Gemini 3.8 Flash**, pero no se pudo medir: la API respondió con error 503 ("alta demanda") y timeouts en las 4 preguntas. Queda fuera por falta de datos, no por una decisión de calidad.

## Limitaciones de la prueba

- Las preguntas 3 y 4 no se usaron en la comparación: 3.6 Flash falló en ellas por errores 503 y por el límite de cuota diaria del plan gratuito (error 429).
- Las mediciones se hicieron en momentos distintos y la latencia varía con la carga del servicio.
- Son pocas mediciones (4 por modelo), así que los promedios son orientativos.