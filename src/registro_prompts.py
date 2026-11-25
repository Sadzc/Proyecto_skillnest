"""Bloque 32 · Paso 1: versionado del prompt real del flujo RAG del DWH.

Las dos versiones se importan desde el código que las usa de verdad, no se copian:
si alguien edita el prompt en recuperacion.py o logging_rag.py, la huella cambia sola.

- v1: PROMPT_TEMPLATE (Bloque 26), un único string de texto plano.
- v2: PROMPT_SISTEMA + PLANTILLA_USUARIO (Bloque 31), roles separados, contexto
  delimitado con <contexto> y la instrucción anti-inyección.
"""

import difflib
from datetime import date

from logging_rag import PLANTILLA_USUARIO, PROMPT_SISTEMA, huella
from recuperacion import MODELO_LLM, PROMPT_TEMPLATE

NOMBRE_PROMPT = "prompt_rag_dwh"
AUTOR = "Sebastian"


class RegistroDePrompts:
    """Historial de versiones de un prompt: huella (Bloque 31), texto, autor, fecha y nota."""

    def __init__(self):
        self.versiones = []

    def registrar(self, nombre, texto, autor, nota):
        version = {
            "nombre": nombre,
            "huella": huella(texto),
            "texto": texto,
            "autor": autor,
            "fecha": str(date.today()),
            "nota": nota,
        }
        self.versiones.append(version)
        return version

    def ultima(self, nombre):
        candidatas = [v for v in self.versiones if v["nombre"] == nombre]
        return candidatas[-1] if candidatas else None


def diff_prompts(anterior, nueva):
    """Palabras agregadas (+) y quitadas (-) entre dos versiones."""
    return list(difflib.unified_diff(
        anterior.split(), nueva.split(),
        fromfile="version_anterior", tofile="version_nueva", lineterm="",
    ))


def construir_registro():
    """Registro con las dos versiones reales del prompt, en orden cronológico."""
    registro = RegistroDePrompts()
    registro.registrar(
        NOMBRE_PROMPT,
        PROMPT_TEMPLATE,
        AUTOR,
        f"version inicial: prompt unico con citas (Bloque 26, {MODELO_LLM})",
    )
    registro.registrar(
        NOMBRE_PROMPT,
        PROMPT_SISTEMA + "\n\n" + PLANTILLA_USUARIO,
        AUTOR,
        f"roles separados + contexto delimitado + anti-inyeccion (Bloque 31, {MODELO_LLM})",
    )
    return registro


if __name__ == "__main__":
    registro = construir_registro()
    print("=" * 62)
    print("PASO 1: versionado de mi prompt")
    print("=" * 62)
    for v in registro.versiones:
        print(v["huella"], "-", v["nota"])

    v1, v2 = registro.versiones
    print("huellas distintas?", v1["huella"] != v2["huella"])
    print("ultima version activa:", registro.ultima(NOMBRE_PROMPT)["huella"])
    for linea in diff_prompts(v1["texto"], v2["texto"]):
        print(linea)