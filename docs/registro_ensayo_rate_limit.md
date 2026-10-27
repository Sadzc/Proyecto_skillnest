# Registro del ensayo de rate limit (Bloque 13)

- **Fecha:** 2026-10-27
- **Archivo ejecutado:** `python cliente.py`
- **Modelo utilizado:** `gemini-3.6-flash`
- **Configuración del backoff (`con_reintento`):** `intentos=4`, `espera_base=5` s, `espera_maxima=30` s, jitter aleatorio de hasta 10%.
- **Peticiones enviadas en el bloque principal:** 6 (1 consulta inicial + bucle de 5 preguntas de prueba sin pausa entre llamadas).
- **Comportamiento observado ante saturación / rate limit (429 / 503):**
  - Cuando la API responde con `429` o `503`, `enviar_peticion` lo traduce a `TimeoutError`.
  - `con_reintento` captura el `TimeoutError` y muestra esperas crecientes con jitter (aprox. `5.3s`, `10.6s`, `21.2s`).
  - Si se agotan los 4 intentos (por ejemplo, al topar la cuota diaria de 20 peticiones de la capa gratuita), `consultar_modelo` captura el `TimeoutError` final y lanza un `RuntimeError` claro: `"El servicio no respondió tras varios intentos. Intenta más tarde."`
- **Registro de costo (`registrar_costo`):**
  - Solo se ejecuta en las peticiones que responden `200 OK`.
  - Costo por petición corta de prueba: ~$0.000045 - $0.000120 USD (acumulado automáticamente en `costo_total_sesion`).
  - Las peticiones que fallan tras agotar los reintentos no suman costo a la sesión.