ROL = (
    "Eres un data engineer senior que trabaja con un Data Warehouse analítico. "
    "Respondes siempre en español. "
)

FORMATO = (
    "Devuelve únicamente un objeto JSON válido, sin texto adicional ni Markdown. "
    "Debe tener exactamente dos claves: 'categoria' (string) "
    "y 'confianza' (número entre 0 y 1). "
)

# Mismo contrato de salida para los tres prompts
ESQUEMA = {
    "type": "OBJECT",
    "properties": {
        "categoria": {"type": "STRING"},
        "confianza": {"type": "NUMBER"},
    },
    "required": ["categoria", "confianza"],
}

SCHEMA_YML = (
    "version: 2\n"
    "models:\n"
    "  - name: fact_ventas\n"
    "    description: \"Tabla de hechos de ventas.\"\n"
    "    columns:\n"
    "      - name: id_venta\n"
    "        description: \"Identificador único de la venta.\"\n"
    "      - name: monto_total\n"
)

BANCO_DE_PROMPTS = [
    {
        "nombre": "clasificar_objeto",
        "system_instruction": ROL + FORMATO + (
            "Clasifica sobre qué objeto de datos pregunta el usuario. "
            "Usa 'metrica' para un indicador o KPI, 'tabla' para una tabla o modelo, "
            "'columna' para una columna, y 'otro' en los demás casos."
        ),
        "ejemplo_usuario": "¿Qué significa la columna monto_neto?",
        "claves_esperadas": ["categoria", "confianza"],
        "categorias_permitidas": ["metrica", "tabla", "columna", "otro"],
        "response_schema": ESQUEMA,
    },
    {
        "nombre": "clasificar_intencion",
        "system_instruction": ROL + FORMATO + (
            "Clasifica qué quiere saber el usuario. "
            "Usa 'definicion' si pregunta qué significa algo, "
            "'origen' si pregunta de qué tabla o modelo sale un dato, "
            "'calidad' si pregunta si algo está documentado o probado, "
            "y 'otro' en los demás casos."
        ),
        "ejemplo_usuario": "¿De qué tabla sale la métrica de ingresos netos?",
        "claves_esperadas": ["categoria", "confianza"],
        "categorias_permitidas": ["definicion", "origen", "calidad", "otro"],
        "response_schema": ESQUEMA,
    },
    {
        "nombre": "clasificar_documentacion",
        "system_instruction": ROL + FORMATO + (
            "Clasifica el estado de documentación del fragmento de schema.yml. "
            "Usa 'completa' si el modelo y todas sus columnas tienen 'description', "
            "'incompleta' si falta 'description' en alguna columna o en el modelo, "
            "y 'sin_documentar' si no hay ninguna 'description'. "
            "Usa solo la información del fragmento."
        ),
        "ejemplo_usuario": SCHEMA_YML,
        "claves_esperadas": ["categoria", "confianza"],
        "categorias_permitidas": ["completa", "incompleta", "sin_documentar"],
        "response_schema": ESQUEMA,
    },
]