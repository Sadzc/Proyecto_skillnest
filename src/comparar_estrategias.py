import sys

print("Python", sys.version.split()[0])
if sys.version_info < (3, 10):
    raise SystemExit("Necesitas Python 3.10 o superior.")
print("Entorno listo")


# Primera versión: tiene un bug real con los empates
def recomendar_estrategia_v1(respuestas):
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

    # max() con key=puntos.get compara las tecnicas por su puntaje.
    # Si hay empate, devuelve solo la primera que encuentra en el diccionario.
    ganador = max(puntos, key=puntos.get)
    return puntos, ganador


# Versión corregida: reporta empates, no los esconde
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

    # puntos.values() son solo los puntajes (por ejemplo [0, 3, 3]); max() toma el mayor.
    maximo = max(puntos.values())
    # para cada par (tecnica, puntaje), guarda la tecnica si su puntaje es igual al maximo:
    # asi se conservan TODAS las empatadas, no solo la primera que encuentra max().
    ganadoras = [tecnica for tecnica, p in puntos.items() if p == maximo]
    return puntos, ganadoras


if __name__ == "__main__":
    # caso 2: clasificador de errores del cliente (Bloque 29)
    respuestas_caso2 = {
        "informacion_cambia_seguido": False,
        "problema_de_formato_o_tono": True,
        "dataset_grande_y_de_calidad": True,
        "presupuesto_limitado_o_iterar_rapido": False,
        "necesita_multiples_variantes": False,
    }

    print()
    puntos_v1, ganador_v1 = recomendar_estrategia_v1(respuestas_caso2)
    print("v1 caso 2:", puntos_v1, "-> recomendacion:", ganador_v1)

    print()
    puntos2, ganadoras2 = recomendar_estrategia(respuestas_caso2)
    print("caso 2:", puntos2)
    print("candidatas empatadas:", ganadoras2)

    # las piezas de la version corregida, por separado
    print()
    print(list(puntos2.items()))
    maximo2 = max(puntos2.values())
    print("maximo:", maximo2)
    print([tecnica for tecnica, p in puntos2.items() if p == maximo2])

    # analisis de sensibilidad: cambiar una respuesta a la vez
    print()
    for clave in respuestas_caso2:
        variante = dict(respuestas_caso2)
        variante[clave] = not variante[clave]
        puntos_v, ganadoras_v = recomendar_estrategia(variante)
        cambio = "CAMBIA" if set(ganadoras_v) != set(ganadoras2) else "igual"
        print(f"{clave} -> {not respuestas_caso2[clave]}: {ganadoras_v}  [{cambio}]")

    # caso 1: bot de atencion al cliente (Bloque 29), con ganador claro
    respuestas_caso1 = {
        "informacion_cambia_seguido": True,
        "problema_de_formato_o_tono": True,
        "dataset_grande_y_de_calidad": False,
        "presupuesto_limitado_o_iterar_rapido": True,
        "necesita_multiples_variantes": False,
    }
    print()
    puntos1, ganadoras1 = recomendar_estrategia(respuestas_caso1)
    print("caso 1:", puntos1)
    print("candidatas empatadas:", ganadoras1)