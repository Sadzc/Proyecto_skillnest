# Decision de personalizacion

## 1. El problema
El clasificador de estado_documentacion del asistente debe devolver, para cada descripcion del schema.yml, un JSON con estado_documentacion y accion_sugerida de forma consistente. En el banco de prompts, 0 de 5 respuestas validas fallaron el formato.

## 2. Resultado del metodo de decision
- RAG: 2 puntos
- PEFT: 1 puntos
- Fine-tuning completo: 0 puntos

## 3. Tecnica elegida y por que
Elijo RAG. El metodo dio un ganador claro (RAG 2, PEFT 1, fine-tuning completo 0), sin empate.
Tiene sentido porque al clasificador no le falta formato: en el banco de prompts
(prompts/registro_resultados.json) 0 de 5 respuestas validas de gemini-3.6-flash fallaron el
contrato JSON, y los 4 errores registrados fueron 503 por alta demanda, no de formato.
Descarto PEFT y fine-tuning por costo: tengo 12 ejemplos etiquetados y llegar a 200 serian
188 ejemplos mas, unas 15,7 horas de etiquetado (src/costos_personalizacion.py), ademas de
habilitar Vertex AI con facturacion, cuando hoy trabajo con el free tier. Con RAG, agregar o
corregir un documento del schema.yml se refleja en segundos, sin reentrenar.

## 4. Que necesitarias para ejecutarla
El corpus indexado hoy (src/indexar_corpus.py) tiene 7 documentos de 2 modelos
(fct_revenue y dim_routes). Me faltan por indexar 4 columnas que ya aparecen en mi dataset
de casos (src/dataset_tuning.py) pero no en el corpus: fct_revenue.fecha, fct_revenue.monto,
fct_revenue.ocupacion y dim_routes.estado, con lo que el corpus pasaria a 11 documentos.
Tampoco hay indexada ninguna definicion de KPI (0 hoy). No necesito ejemplos etiquetados
adicionales, porque no uso PEFT ni fine-tuning.