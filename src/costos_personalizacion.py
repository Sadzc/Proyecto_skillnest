def estimar_costo_de_etiquetar(num_ejemplos, minutos_por_ejemplo, costo_por_hora):
    horas = (num_ejemplos * minutos_por_ejemplo) / 60
    costo = horas * costo_por_hora
    return horas, costo


if __name__ == "__main__":
    # 1. Ejemplo de la lección: dataset de 8 ejemplos (Bloque 29) vs 200 de producción
    horas, costo = estimar_costo_de_etiquetar(8, 5, 25)
    print(f"{horas:.2f} horas, aprox ${costo:.2f}")

    horas2, costo2 = estimar_costo_de_etiquetar(200, 5, 25)
    print(f"{horas2:.2f} horas, aprox ${costo2:.2f}")
    print(f"factor de crecimiento en horas: {horas2 / horas:.1f}x, para 25x mas ejemplos")

    # 2. Mini-ejercicio: 500 ejemplos, 4 min c/u, 20 USD/hora, 20 % con segunda revisión de 2 min
    print()
    horas_base, costo_base = estimar_costo_de_etiquetar(500, 4, 20)
    horas_rev, costo_rev = estimar_costo_de_etiquetar(500 * 0.20, 2, 20)

    total_horas = horas_base + horas_rev
    total_costo = costo_base + costo_rev
    jornadas = total_horas / 8

    print(f"etiquetado base: {horas_base:.2f} horas, aprox ${costo_base:.2f}")
    print(f"segunda revision: {horas_rev:.2f} horas, aprox ${costo_rev:.2f}")
    print(f"total: {total_horas:.2f} horas, aprox ${total_costo:.2f}")
    print(f"jornadas de 8 horas: {jornadas:.1f}")

    # 3. Mi proyecto: clasificador de estado_documentacion (src/dataset_tuning.py)

    EJEMPLOS_ACTUALES = 12
    EJEMPLOS_OBJETIVO = 200
    MINUTOS_POR_EJEMPLO = 5
    COSTO_POR_HORA = 25

    faltantes = EJEMPLOS_OBJETIVO - EJEMPLOS_ACTUALES
    horas_mi, costo_mi = estimar_costo_de_etiquetar(faltantes, MINUTOS_POR_EJEMPLO, COSTO_POR_HORA)
    print()
    print(f"mi proyecto: faltan {faltantes} ejemplos para llegar a {EJEMPLOS_OBJETIVO}")
    print(f"etiquetarlos: {horas_mi:.2f} horas, aprox ${costo_mi:.2f} ({horas_mi / 8:.1f} jornadas)")