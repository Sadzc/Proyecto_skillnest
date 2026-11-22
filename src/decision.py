import os


# Paso 1: método de decisión sobre mi caso
def recomendar_estrategia(respuestas):
    puntos = {"RAG": 0, "Fine-tuning completo": 0, "PEFT": 0}

    if respuestas["informacion_cambia_seguido"]:
        puntos["RAG"] += 3
    if respuestas["problema_de_formato_o_tono"]:
        puntos["PEFT"] += 2
        puntos["Fine-tuning completo"] += 1
    if respuestas["dataset_grande_y_de_calidad"]:
        puntos["Fine-tuning completo"] += 2
        puntos["PEFT"] += 1
    if respuestas["presupuesto_limitado_o_iterar_rapido"]:
        puntos["RAG"] += 2
        puntos["PEFT"] += 1
    if respuestas["necesita_multiples_variantes"]:
        puntos["PEFT"] += 2

    maximo = max(puntos.values())
    ganadoras = [tecnica for tecnica, p in puntos.items() if p == maximo]
    return puntos, ganadoras


# Mi caso: clasificador de estado_documentacion (src/dataset_tuning.py),
# que recibe la descripción de un modelo o columna del schema.yml y devuelve
# {"estado_documentacion": ..., "accion_sugerida": ...}
respuestas_mi_caso = {
    # las 4 categorías (ausente, incompleta, ambigua, completa) son fijas;
    # el schema.yml llega como entrada, el modelo no necesita "saberlo"
    "informacion_cambia_seguido": False,
    # PENDIENTE: revisar 20 respuestas reales del modelo base y contar cuántas
    # no traen el JSON con las dos claves esperadas (3 o más -> True)
    "problema_de_formato_o_tono": False,  # prompts/registro_resultados.json: 0 fallos de formato en 5 respuestas validas (0 %); los 4 errores fueron 503, no de formato
    # 12 ejemplos etiquetados (4 categorías x 3): menos de 200 -> False
    "dataset_grande_y_de_calidad": False,
    # free tier de la API y sin facturación en GCP: 0 entrenamientos pagables
    "presupuesto_limitado_o_iterar_rapido": True,
    # un solo clasificador para todo el asistente
    "necesita_multiples_variantes": False,
}

if any(valor is None for valor in respuestas_mi_caso.values()):
    raise SystemExit("Completa las cinco respuestas con True o False antes de continuar.")

puntos, ganadoras = recomendar_estrategia(respuestas_mi_caso)
print(puntos)
print("candidatas:", ganadoras)


# Paso 2: esqueleto del documento
def generar_esqueleto_decision(problema, puntos, ganadoras):
    empate = len(ganadoras) > 1
    lineas = []
    lineas.append("# Decision de personalizacion")
    lineas.append("")
    lineas.append("## 1. El problema")
    lineas.append(problema)
    lineas.append("")
    lineas.append("## 2. Resultado del metodo de decision")
    for tecnica, p in sorted(puntos.items(), key=lambda x: -x[1]):
        lineas.append(f"- {tecnica}: {p} puntos")
    if empate:
        lineas.append("")
        lineas.append(f"**Empate entre: {', '.join(ganadoras)}**")
    lineas.append("")
    lineas.append("## 3. Tecnica elegida y por que")
    if empate:
        lineas.append(
            "[COMPLETAR: el puntaje no resolvio el empate solo -- "
            "justifica aqui con criterio propio]"
        )
    else:
        lineas.append(f"[COMPLETAR: por que {ganadoras[0]} responde mejor a este caso]")
    lineas.append("")
    lineas.append("## 4. Que necesitarias para ejecutarla")
    lineas.append(
        "[COMPLETAR: corpus faltante, o cantidad de ejemplos etiquetados que faltan]"
    )
    return "\n".join(lineas)


esqueleto = generar_esqueleto_decision(
    "El clasificador de estado_documentacion del asistente debe devolver, para cada "
    "descripcion del schema.yml, un JSON con estado_documentacion y accion_sugerida "
    "de forma consistente. En el banco de prompts, 0 de 5 respuestas validas fallaron el formato.",
    puntos,
    ganadoras,
)
print()
print(esqueleto)

ruta = os.path.join("docs", "decision_personalizacion.md")
with open(ruta, "w", encoding="utf-8") as f:
    f.write(esqueleto)
print(f"\nDocumento generado en {ruta}")