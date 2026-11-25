"""Bloque 32 · Paso 2: punto de supervisión humana antes de activar una versión nueva del prompt.

La huella propuesta no se escribe a mano: sale de registro_prompts.py, así el grafo
siempre pide aprobar la versión que de verdad está registrada como la última.
Cada solicitud usa un thread_id único y resolver() verifica que haya algo pendiente
antes de reanudar, para no aprobar dos veces ni aprobar algo que nadie revisó.
"""

import uuid
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from registro_prompts import NOMBRE_PROMPT, construir_registro


class EstadoDespliegue(TypedDict):
    huella_nueva: str
    aprobado: bool


def proponer(estado: EstadoDespliegue):
    print("nodo proponer: huella", estado["huella_nueva"])
    return {}


def supervisar(estado: EstadoDespliegue):
    decision = interrupt({
        "motivo": "aprobar nueva version de prompt en produccion",
        "huella_propuesta": estado["huella_nueva"],
    })
    return {"aprobado": decision}


def aplicar(estado: EstadoDespliegue):
    if estado["aprobado"]:
        print("version", estado["huella_nueva"], "activada")
    else:
        print("version", estado["huella_nueva"], "rechazada, se mantiene la anterior")
    return {}


def nuevo_thread_id(prefijo="despliegue"):
    return f"{prefijo}-{uuid.uuid4().hex[:8]}"


def resolver(app, config, aprobar: bool, huella_revisada: str):
    """Reanuda el grafo con la decisión humana. En un sistema real la invoca el botón
    Aprobar/Rechazar de una interfaz (POST al backend), no una línea de código.

    Antes de reanudar comprueba que el thread tenga algo pendiente y que la huella
    pendiente sea la misma que revisó la persona."""
    snapshot = app.get_state(config)
    if not snapshot.next:
        raise ValueError("este thread_id no tiene ninguna aprobacion pendiente")
    if snapshot.values["huella_nueva"] != huella_revisada:
        raise ValueError("la huella pendiente no es la que reviso la persona")
    return app.invoke(Command(resume=aprobar), config=config)


def construir_grafo():
    grafo = StateGraph(EstadoDespliegue)
    grafo.add_node("proponer", proponer)
    grafo.add_node("supervisar", supervisar)
    grafo.add_node("aplicar", aplicar)
    grafo.add_edge(START, "proponer")
    grafo.add_edge("proponer", "supervisar")
    grafo.add_edge("supervisar", "aplicar")
    grafo.add_edge("aplicar", END)
    return grafo.compile(checkpointer=InMemorySaver())


def solicitar_despliegue(app, huella):
    """Corre el grafo hasta el interrupt y devuelve el config de esa solicitud."""
    config = {"configurable": {"thread_id": nuevo_thread_id()}}
    resultado = app.invoke({"huella_nueva": huella, "aprobado": False}, config=config)
    assert "__interrupt__" in resultado, "el grafo no se detuvo en el punto de supervision"
    print("estado tras primera corrida (interrumpido):", resultado)
    return config


if __name__ == "__main__":
    huella = construir_registro().ultima(NOMBRE_PROMPT)["huella"]
    app = construir_grafo()

    print("=" * 62)
    print("PASO 2: punto de supervision antes de activar la version nueva")
    print("=" * 62)

    # Camino de aprobación
    config = solicitar_despliegue(app, huella)
    snapshot = app.get_state(config)
    print("siguiente nodo pendiente:", snapshot.next)
    print("detalle de la interrupcion:", snapshot.interrupts[0].value)
    print("aprobado:", resolver(app, config, True, huella_revisada=huella))

    # Camino de rechazo, con su propio thread_id
    config2 = solicitar_despliegue(app, huella)
    print("rechazado:", resolver(app, config2, False, huella_revisada=huella))

    # Protecciones de resolver(): ninguna llega a reanudar el grafo
    try:
        resolver(app, config, True, huella_revisada=huella)
    except ValueError as e:
        print("aprobar dos veces la misma solicitud:", e)

    config3 = solicitar_despliegue(app, huella)
    try:
        resolver(app, config3, True, huella_revisada="otra-huella")
    except ValueError as e:
        print("aprobar una huella distinta a la revisada:", e)