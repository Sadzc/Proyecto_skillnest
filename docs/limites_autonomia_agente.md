# Límites de autonomía: Agente de documentación del data warehouse

## Herramientas y nivel de riesgo

- `buscar_modelo`: bajo (solo lee el schema en memoria, no modifica nada)
- `calcular_cobertura`: bajo (solo calcula un porcentaje, no ejecuta ninguna acción externa)
- `buscar_columna_en_modelo`: bajo (solo consulta la descripción de una columna, no modifica nada)
- `solicitar_redocumentacion`: alto (abre un ticket en el sistema de seguimiento de forma
  irreversible; un ticket mal generado compromete tiempo del equipo de Data Engineering
  y no se puede deshacer)

## Herramientas que requieren aprobación humana

- `solicitar_redocumentacion`: porque genera una acción externa irreversible. Si el agente
  identifica mal el modelo o redacta un motivo equivocado, el ticket queda abierto de todas
  formas y compromete recursos reales del equipo. La aprobación humana es el único punto
  donde se puede detener esa acción antes de que ocurra.

## Revisión de trazas

- **Frecuencia:** semanal para una muestra representativa; revisión completa de cada traza
  donde haya aparecido `solicitar_redocumentacion`, sin excepción.
- **Qué se busca:**
  - `buscar_modelo` o `buscar_columna_en_modelo` invocadas dos veces seguidas con el mismo
    argumento: puede indicar que la observación fue ambigua y el agente reintentó sin avanzar.
  - `solicitar_redocumentacion` en la traza sin un registro de aprobación correspondiente
    en `registro_aprobaciones`: señal de que el flujo de supervisión no funcionó.
  - Respuesta final que afirma algo que ninguna herramienta devolvió: el agente probablemente
    inventó información en vez de consultar el schema real.

## Qué hacer ante un comportamiento inesperado

1. Buscar la sesión afectada en `trazas_agente.jsonl` y revisar la secuencia completa de
   acciones y observaciones.
2. Si la herramienta comprometida es `solicitar_redocumentacion`, verificar en
   `registro_aprobaciones` si la acción fue aprobada antes de continuar cualquier otra cosa.
3. Remover temporalmente la herramienta del listado `herramientas` en
   `src/agente_con_herramientas.py` mientras se investiga, para que el agente no pueda
   volver a invocarla.
4. Revisar la descripción del `@tool` afectado: si el agente la invocó en un caso que no
   corresponde, ajustar la descripción para acotar cuándo debe usarse.
5. Revisar el prompt del sistema (`instrucciones`) si el problema es de interpretación
   general y no de una herramienta puntual.
6. Volver a ejecutar las cuatro pruebas del `__main__` para confirmar que el comportamiento
   corregido es el esperado antes de reactivar la herramienta.