import re
from collections import Counter


def limpiar_texto(texto: str) -> str:
    """Normaliza el texto: minúsculas y sin puntuación."""
    if not isinstance(texto, str):
        tipo = type(texto).__name__
        raise TypeError(f"limpiar_texto espera str, no {tipo}")

    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def tokenizar(texto_limpio: str) -> list[str]:
    """Convierte texto limpio en una lista de tokens."""
    return texto_limpio.split()


def vectorizar(tokens: list[str]) -> Counter:
    """Cuenta cuántas veces aparece cada token."""
    return Counter(tokens)


def procesar_texto(texto: str) -> list[str]:
    """Limpia y tokeniza: el paso previo a cualquier métrica."""
    return tokenizar(limpiar_texto(texto))


def proporcion_coincidencia(tokens_referencia: list[str], tokens_respuesta: list[str]) -> float:
    """Proporción de palabras distintas de la referencia que aparecen en la respuesta."""
    palabras_referencia = set(tokens_referencia)
    if not palabras_referencia:
        return 0.0
    return len(palabras_referencia & set(tokens_respuesta)) / len(palabras_referencia)