import json
from collections import Counter

from google.genai import types

# Paso 1: dataset propio (12 ejemplos, 4 categorías, 3 por categoría).
# Cada categoría usa siempre la misma accion_sugerida, para no enseñar inconsistencia.
ejemplos_raw = [
    # ausente: la descripción no existe o está vacía
    ("modelo: dim_routes | columna: activa | description: ''",
     {"estado_documentacion": "ausente", "accion_sugerida": "solicitar redocumentacion al owner del modelo"}),
    ("modelo: fct_revenue | columna: fecha | description: (sin campo description en schema.yml)",
     {"estado_documentacion": "ausente", "accion_sugerida": "solicitar redocumentacion al owner del modelo"}),
    ("modelo: dim_routes | columna: destino | description: null",
     {"estado_documentacion": "ausente", "accion_sugerida": "solicitar redocumentacion al owner del modelo"}),

    # incompleta: describe algo, pero falta unidad, granularidad u origen
    ("modelo: fct_revenue | columna: ingresos | description: 'Ingresos.'",
     {"estado_documentacion": "incompleta", "accion_sugerida": "completar descripcion con unidad, granularidad y origen"}),
    ("modelo: fct_revenue | columna: pasajeros | description: 'Cantidad de pasajeros.'",
     {"estado_documentacion": "incompleta", "accion_sugerida": "completar descripcion con unidad, granularidad y origen"}),
    ("modelo: fct_revenue | description: 'Tabla de ingresos.'",
     {"estado_documentacion": "incompleta", "accion_sugerida": "completar descripcion con unidad, granularidad y origen"}),

    # ambigua: la descripción admite más de una interpretación
    ("modelo: fct_revenue | columna: monto | description: 'Monto de la operacion, puede incluir o no impuestos.'",
     {"estado_documentacion": "ambigua", "accion_sugerida": "aclarar el significado y el criterio de calculo"}),
    ("modelo: dim_routes | columna: estado | description: 'Estado de la ruta (ver sistema origen).'",
     {"estado_documentacion": "ambigua", "accion_sugerida": "aclarar el significado y el criterio de calculo"}),
    ("modelo: fct_revenue | columna: ocupacion | description: 'Porcentaje de ocupacion, segun el caso.'",
     {"estado_documentacion": "ambigua", "accion_sugerida": "aclarar el significado y el criterio de calculo"}),

    # completa: explica significado, unidad/granularidad y relación u origen
    ("modelo: fct_revenue | columna: route_id | description: 'Identificador unico de la ruta. Se usa para relacionar con dim_routes.'",
     {"estado_documentacion": "completa", "accion_sugerida": "ninguna, documentacion suficiente"}),
    ("modelo: dim_routes | columna: origen | description: 'Ciudad de origen de la ruta, en texto, tomada del catalogo de rutas activas.'",
     {"estado_documentacion": "completa", "accion_sugerida": "ninguna, documentacion suficiente"}),
    ("modelo: fct_revenue | description: 'Tabla de hechos con los ingresos diarios por ruta, en pesos chilenos, un registro por ruta y dia.'",
     {"estado_documentacion": "completa", "accion_sugerida": "ninguna, documentacion suficiente"}),
]

examples = [
    types.TuningExample(text_input=texto, output=json.dumps(salida, ensure_ascii=False))
    for texto, salida in ejemplos_raw
]


# Paso 2: balance entre categorías
def chequear_balance(ejemplos_raw: list[tuple[str, dict]], clave: str) -> Counter:
    categorias = Counter(salida[clave] for _, salida in ejemplos_raw)
    return categorias


# Paso 3: validación antes de enviar nada
def validar_dataset(
    examples: list[types.TuningExample], claves_esperadas: tuple[str, ...]
) -> list[str]:
    problemas = []
    vistos = set()
    for i, ej in enumerate(examples):
        if not ej.text_input or not ej.text_input.strip():
            problemas.append(f"ejemplo {i}: text_input vacio")
        if not ej.output or not ej.output.strip():
            problemas.append(f"ejemplo {i}: output vacio")
            continue
        if ej.text_input in vistos:
            problemas.append(f"ejemplo {i}: text_input duplicado")
        vistos.add(ej.text_input)
        try:
            salida = json.loads(ej.output)
        except json.JSONDecodeError:
            problemas.append(f"ejemplo {i}: output no es JSON valido")
            continue
        for clave in claves_esperadas:
            if clave not in salida:
                problemas.append(f'ejemplo {i}: output no tiene la clave "{clave}"')
    return problemas


CLAVES = ("estado_documentacion", "accion_sugerida")

if __name__ == "__main__":
    print(len(examples), "ejemplos construidos")
    print(examples[0])

    print()
    balance = chequear_balance(ejemplos_raw, "estado_documentacion")
    for categoria, cuenta in balance.most_common():
        print(f"{categoria}: {cuenta}")

    print()
    problemas = validar_dataset(examples, claves_esperadas=CLAVES)
    print(f"{len(examples)} ejemplos, {len(problemas)} problemas encontrados")
    for p in problemas:
        print(" -", p)

    # Comprobar que el validador detecta errores: un output sin una clave y un text_input duplicado
    print()
    examples_rotos = examples + [
        types.TuningExample(text_input="modelo: dim_routes | columna: codigo | description: ''",
                            output='{"estado_documentacion": "ausente"}'),
        types.TuningExample(text_input=ejemplos_raw[0][0],
                            output="{'estado_documentacion': 'ausente', 'accion_sugerida': 'x'}"),
    ]
    problemas_rotos = validar_dataset(examples_rotos, claves_esperadas=CLAVES)
    print(f"{len(examples_rotos)} ejemplos, {len(problemas_rotos)} problemas encontrados")
    for p in problemas_rotos:
        print(" -", p)