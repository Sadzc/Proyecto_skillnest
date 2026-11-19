"""Confirma que lo básico está en orden antes de gastar cuota:
- que la carpeta del índice (vectorstore/) existe: si no, ¿corriste la indexación?
- que esa carpeta está en el .gitignore: es contenido regenerable, no código fuente.

La ruta del índice se importa de indexar_corpus.py: así se comprueba la MISMA ruta
que usan la indexación y la consulta.
"""

from pathlib import Path

from indexar_corpus import PERSIST_DIR

RAIZ = Path(__file__).resolve().parent.parent


def preflight_check(persist_directory=PERSIST_DIR, gitignore_path=RAIZ / ".gitignore"):
    """Confirma, sin llamar a ninguna API, que lo básico del flujo está en orden.

    Devuelve la lista de problemas encontrados; vacía si todo está bien.
    """
    problemas = []
    persist_directory = Path(persist_directory)
    gitignore_path = Path(gitignore_path)

    if not persist_directory.is_dir():
        problemas.append(f"{persist_directory.name}/ no existe: ¿corriste la indexación?")

    if gitignore_path.exists():
        lineas = [linea.strip().rstrip("/") for linea in
                  gitignore_path.read_text(encoding="utf-8").splitlines()]
        if persist_directory.name not in lineas:
            problemas.append(f"{persist_directory.name}/ no está en {gitignore_path.name}")
    else:
        problemas.append(f"no existe {gitignore_path.name} en este proyecto")

    return problemas


if __name__ == "__main__":
    problemas = preflight_check()
    if problemas:
        print("Preflight con problemas:")
        for problema in problemas:
            print(" -", problema)
    else:
        print("Preflight OK: la carpeta del índice existe y está en .gitignore")