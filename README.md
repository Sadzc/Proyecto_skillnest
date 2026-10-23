# Asistente de Documentación de Data Warehouse

## 1. Descripción del proyecto

Este repositorio contiene un asistente para trabajar con documentación de un Data Warehouse mediante modelos de lenguaje y técnicas de RAG (*Retrieval-Augmented Generation*). El proyecto forma parte de la Especialización en Desarrollo con IA Generativa de Skillnest y Accenture.

La propuesta consiste en responder preguntas sobre columnas, modelos y métricas de negocio a partir de documentación como archivos `schema.yml`, descripciones de modelos dbt y definiciones de KPI, citando fuentes e identificando posibles brechas de documentación.

Esta guía explica cómo preparar y ejecutar el proyecto en Windows, macOS, Ubuntu, otras distribuciones Linux y WSL. Puedes trabajar con VS Code o solo con una terminal; VS Code es opcional.

## 2. Requisitos previos

Necesitas:

- **Python 3**, en una versión compatible con las dependencias del proyecto. El repositorio no especifica aquí una versión mínima única; revisa los requisitos de las bibliotecas si aparece un error de compatibilidad.
- **Git**, para clonar el repositorio y gestionar cambios.
- **Acceso a Internet**, para clonar el proyecto, instalar dependencias y consultar servicios externos.
- **Una clave de API de Gemini**, para los scripts que realizan solicitudes al modelo.
- **Visual Studio Code (opcional)**, si prefieres una interfaz gráfica y una terminal integrada.

### 2.1. Comprobar Python

**Windows — PowerShell o CMD:**

```powershell
python --version
```

Si `python` no se reconoce en Windows, prueba el comando `py`:

```powershell
py --version
```

**macOS, Ubuntu, Linux y WSL:**

```bash
python3 --version
```

El comando debe mostrar una versión instalada. Si falla, instala Python desde [python.org](https://www.python.org/downloads/) y revisa la configuración de `PATH` cuando corresponda.

En Ubuntu/WSL, si faltan Python, `pip` o los componentes para crear entornos virtuales:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

Estos comandos con `apt` son para distribuciones basadas en Debian/Ubuntu; no se usan en Windows nativo ni en macOS. En WSL, Python debe estar instalado dentro de la distribución Linux que vayas a utilizar: la instalación de Windows es independiente.

### 2.2. Comprobar Git

**Windows, macOS, Ubuntu, Linux y WSL:**

```bash
git --version
```

Debe aparecer la versión instalada. Si Git no está disponible:

- **Windows:** instala Git desde [git-scm.com/downloads](https://git-scm.com/downloads). Si `winget` está disponible, puedes usar PowerShell:

  ```powershell
  winget install --id Git.Git -e
  ```

- **macOS:** puedes instalar las herramientas de línea de comandos con:

  ```bash
  xcode-select --install
  ```

  También puedes instalar Git mediante otro método compatible con macOS.

- **Ubuntu/WSL:**

  ```bash
  sudo apt update
  sudo apt install git
  ```

Después de instalarlo, cierra y vuelve a abrir la terminal y ejecuta `git --version` otra vez.

### 2.3. Instalar VS Code (opcional)

Si quieres utilizar el editor, descárgalo desde [code.visualstudio.com](https://code.visualstudio.com/). No es obligatorio: el proyecto también puede prepararse y ejecutarse desde una terminal.

## 3. Obtener el proyecto

Repositorio: [https://github.com/Sadzc/Proyecto_skillnest.git](https://github.com/Sadzc/Proyecto_skillnest.git)

Elige **una** de estas alternativas. No necesitas clonar el repositorio de las dos maneras.

### 3.1. Alternativa A: clonar con VS Code

1. Instala y abre Visual Studio Code.
2. Abre la paleta de comandos:
   - Windows y Linux: `Ctrl + Shift + P`.
   - macOS: `Cmd + Shift + P`.
3. Busca y selecciona `Git: Clone`.
4. Introduce la URL:

   ```text
   https://github.com/Sadzc/Proyecto_skillnest.git
   ```

5. Elige la carpeta **padre** donde guardarás el proyecto, por ejemplo, una carpeta de proyectos o Documentos.
6. Espera a que termine la clonación.
7. Cuando VS Code lo solicite, abre la carpeta clonada **`Proyecto_skillnest`**, no solamente la carpeta padre.
8. Abre una terminal integrada desde el menú **Terminal → New Terminal / Nueva terminal**.
9. Ejecuta:

   ```bash
   git status
   ```

Git debería mostrar información del repositorio, incluida la rama actual y el estado de los archivos. Si el repositorio no tiene cambios pendientes, puede aparecer `nothing to commit, working tree clean`.

### 3.2. Alternativa B: clonar desde una terminal

Antes de clonar, comprueba la ubicación actual y decide dónde guardar el repositorio.

**PowerShell, macOS, Linux y WSL:**

```bash
pwd
```

**CMD de Windows:**

```cmd
cd
```

Estos comandos muestran la ubicación actual. Si quieres cambiar de carpeta antes de clonar, puedes usar los siguientes ejemplos **solo si esas rutas existen en tu equipo**.

**PowerShell — ejemplo de Documentos:**

```powershell
Set-Location "$HOME\Documents"
```

**CMD — ejemplo de Documentos:**

```cmd
cd /d "%USERPROFILE%\Documents"
```

**macOS, Linux y WSL — ejemplo de Documentos:**

```bash
cd ~/Documents
```

La carpeta Documentos puede tener otro nombre, estar redirigida a OneDrive o encontrarse en una ubicación personalizada. Si la ruta del ejemplo no existe, utiliza la ruta real de la carpeta donde quieres guardar el proyecto.

Una vez elegida la ubicación, ejecuta estos comandos en PowerShell, CMD, macOS, Linux o WSL:

```bash
git clone https://github.com/Sadzc/Proyecto_skillnest.git
cd Proyecto_skillnest
git status
```

`git clone` crea la carpeta `Proyecto_skillnest` dentro de la ubicación actual; `cd Proyecto_skillnest` entra en ella. Ejecuta los comandos posteriores desde esa carpeta raíz, salvo que una instrucción indique expresamente otra ubicación.

### 3.3. Comprobar que estás en la raíz correcta

Para listar los archivos de la ubicación actual:

**PowerShell:**

```powershell
Get-ChildItem
```

**CMD:**

```cmd
dir
```

**macOS, Linux y WSL:**

```bash
ls -la
```

En la raíz del proyecto deberían encontrarse, entre otros, `README.md`, `requirements.txt`, `.gitignore` y, en la versión actual consultada, `.env.example`.

Si `git status` devuelve `fatal: not a git repository`, probablemente la terminal está en otra carpeta. Comprueba la ubicación, entra en `Proyecto_skillnest` y vuelve a ejecutar `git status`; no reinstales Git como primera medida.

### 3.4. Si ya descargaste el proyecto o no recuerdas dónde está

No vuelvas a clonar el repositorio si ya tienes una copia utilizable.

- En Windows, busca `Proyecto_skillnest` con el Explorador de archivos.
- En macOS, búscalo con Finder.
- En Linux/WSL, puedes buscar dentro de tu directorio personal:

  ```bash
  find ~ -type d -name "Proyecto_skillnest" 2>/dev/null
  ```

  La búsqueda se limita a `~` y puede no encontrar carpetas guardadas en otros lugares o que no tengas permiso para consultar.

Cuando encuentres la carpeta, entra en ella con `cd` o `Set-Location`, según tu terminal, y ejecuta `git status` para comprobar que estás dentro del repositorio.

## 4. Estructura del repositorio

La estructura que se documenta a continuación debe entenderse como una referencia: los archivos pueden variar entre versiones. Los directorios y archivos de la raíz (`docs/`, `prompts/`, `src/`, `tests/`, `.env.example`, `.gitignore`, `README.md`, `app.py` y `requirements.txt`) aparecen en el repositorio consultado; comprueba los contenidos anidados en tu copia si no coinciden.

```text
Proyecto_skillnest/
├── docs/
│   ├── resultados/
│   ├── decision-arquitectura.md
│   ├── diagrama_arquitectura.png
│   ├── evidencia_peticion_autenticada.png
│   └── respuestas_completas.md
├── prompts/
│   ├── banco.py
│   ├── registro_resultados.json
│   └── test_consistencia.py
├── src/
│   ├── consumir_gemini.py
│   └── consumir_gemini costos_latencia.py
├── tests/
├── .env.example
├── .gitignore
├── README.md
├── app.py
└── requirements.txt
```

| Archivo o carpeta | Propósito documentado o comprobado |
|---|---|
| `app.py` | Realiza una solicitud a Gemini e imprime la respuesta en una estructura de salida definida en el código. |
| `src/consumir_gemini.py` | Contiene funciones para preparar y enviar solicitudes a Gemini y extraer el texto de la respuesta. |
| `src/consumir_gemini costos_latencia.py` | Compara modelos, mide latencia, estima costos y registra resultados. |
| `prompts/banco.py` | Define el banco de prompts usado por la prueba de consistencia. |
| `prompts/test_consistencia.py` | Ejecuta intentos con los prompts, evalúa la estructura de las respuestas y guarda un registro JSON. |
| `docs/resultados/` | Directorio utilizado por el script de comparación para guardar informes y registros. |
| `docs/respuestas_completas.md` | Puede corresponder a un informe anterior; el script de comparación genera informes con nombres que incluyen la fecha/hora en `docs/resultados/`. |
| `prompts/registro_resultados.json` | Registro que genera `prompts/test_consistencia.py`. |
| `.env.example` | Plantilla con el nombre de la variable de la clave de Gemini. |
| `.env` | Archivo local que debes crear para guardar tu clave; no debe publicarse. |
| `.gitignore` | Reglas para excluir entornos virtuales, secretos y archivos temporales. |
| `requirements.txt` | Lista de dependencias de Python, con versiones fijadas en la versión consultada. |
| `.venv/` | Entorno virtual local recomendado por esta guía; se crea en tu equipo y no debe subirse a Git. |

**Importante:** los comandos de instalación y ejecución de esta guía se ejecutan desde la raíz `Proyecto_skillnest`, donde se encuentran `app.py` y `requirements.txt`.

## 5. Configurar Python y el entorno virtual

Un entorno virtual mantiene las dependencias de este proyecto separadas de las de otros proyectos de Python. Esta guía utiliza siempre el nombre `.venv`.

### 5.1. Crear el entorno

Puedes crear el entorno con VS Code o desde la terminal. Si `.venv` ya existe y funciona, no necesitas volver a crearlo.

**Alternativa A — VS Code**

1. Abre la carpeta raíz `Proyecto_skillnest`.
2. Instala la extensión **Python** publicada por Microsoft si aún no está instalada.
3. Abre la paleta de comandos (`Ctrl + Shift + P` en Windows/Linux o `Cmd + Shift + P` en macOS).
4. Selecciona `Python: Create Environment`.
5. Elige `Venv` y selecciona una instalación compatible de Python.
6. Espera a que VS Code cree el entorno. Comprueba la ubicación mostrada; normalmente será `.venv`.
7. Si la opción no aparece o falla, sigue las instrucciones de terminal que aparecen a continuación.

**Alternativa B — terminal**

Ejecuta los comandos desde la raíz del repositorio.

**Windows — PowerShell o CMD:**

```powershell
python -m venv .venv
```

Si `python` no está disponible en Windows, prueba este comando:

```powershell
py -m venv .venv
```

**macOS, Ubuntu, Linux y WSL:**

```bash
python3 -m venv .venv
```

La creación puede terminar sin mostrar un mensaje. Comprueba que exista `.venv` con `Get-ChildItem` (PowerShell), `dir` (CMD) o `ls -la` (macOS/Linux/WSL).

Si Ubuntu/WSL indica que falta `venv`, vuelve a los requisitos previos e instala `python3-venv`.

### 5.2. Activar el entorno virtual

**Windows — PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la ejecución del script, puedes permitirla temporalmente para el proceso actual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Después, vuelve a ejecutar el comando de activación. Este ajuste se aplica al proceso actual y no cambia permanentemente la política del sistema.

**Windows — CMD:**

```cmd
.venv\Scripts\activate.bat
```

**macOS, Ubuntu, Linux y WSL:**

```bash
source .venv/bin/activate
```

La señal visual habitual de activación es `(.venv)` al principio del prompt, aunque la apariencia puede variar.

### 5.3. Verificar el intérprete activo

Con el entorno activado, comprueba qué Python se está utilizando.

**PowerShell:**

```powershell
Get-Command python
```

**CMD:**

```cmd
where python
```

**macOS, Linux y WSL:**

```bash
which python
```

La ruta debería apuntar al entorno `.venv`. Si no es así, revisa la activación y, si usas VS Code, la selección del intérprete.

### 5.4. Salir del entorno virtual

Cuando termines, puedes desactivarlo con:

```bash
deactivate
```

Al abrir una terminal nueva normalmente tendrás que volver a activarlo. No necesitas crearlo otra vez si `.venv` sigue existiendo.

## 6. Instalar las dependencias

Ejecuta estos comandos desde la raíz del repositorio y con `.venv` activado:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`python -m pip` utiliza `pip` asociado al intérprete `python` activo, lo que ayuda a evitar instalaciones en otro entorno.

El `requirements.txt` de la versión consultada incluye, entre otras, `google-genai`, `requests`, `python-dotenv` y `pydantic`, con versiones fijadas en el archivo. La lista completa y sus versiones deben consultarse directamente en `requirements.txt`.

Comprueba la versión de Python y de `pip`:

```bash
python --version
python -m pip --version
```

La ruta que muestre `pip` debe ser coherente con el entorno virtual. La instalación se considera completada cuando el comando termina sin errores; revisa el mensaje final en la terminal.

Si `python` no se encuentra en macOS/Linux/WSL, comprueba primero que `.venv` esté activado. Si todavía no creaste el entorno, sigue la sección 5 y utiliza `python3` para crearlo antes de activarlo.

Si falla `pip install -r requirements.txt`, comprueba que:

- Estás en la raíz correcta y existe `requirements.txt`.
- El entorno virtual está activado.
- Tienes conexión a Internet.
- Tu versión de Python es compatible con las dependencias.
- El mensaje de error no identifica una dependencia concreta o un problema de instalación que requiera atención.

No instales paquetes al azar ni modifiques `requirements.txt` sin revisar el error.

## 7. Configurar la API de Gemini y `.env`

Los scripts que consultan Gemini leen la variable `GEMINI_API_KEY`. El código de `src/consumir_gemini.py` y del script de costos/latencia comprueba que la variable exista. El archivo `.env.example` de la versión consultada contiene una plantilla para esa variable.

### 7.1. Comprobar y crear `.env`

Ejecuta estos comandos desde la raíz del repositorio.

**PowerShell:**

```powershell
Test-Path .env.example
Test-Path .env
```

**CMD:**

```cmd
dir .env.example
dir .env
```

**macOS, Linux y WSL:**

```bash
ls -l .env.example
ls -la .env
```

Si `.env.example` existe y `.env` **no** existe, crea la copia con el comando correspondiente:

**PowerShell:**

```powershell
Copy-Item .env.example .env
```

**CMD:**

```cmd
copy .env.example .env
```

**macOS, Linux y WSL:**

```bash
cp .env.example .env
```

Ejecuta el comando de copia solo cuando se cumplan esas condiciones. Si `.env` ya existe, edita el archivo existente en lugar de sobrescribirlo. Si falta `.env.example`, confirma que estás en la raíz y revisa los archivos de tu versión del repositorio.

### 7.2. Editar `.env`

Abre `.env` desde VS Code o utiliza un editor disponible en tu sistema. Ejecuta los comandos desde la raíz del proyecto.

- **Windows — PowerShell o CMD:**

  ```powershell
  notepad .env
  ```

- **macOS:**

  ```bash
  open -e .env
  ```

- **Linux/Ubuntu/WSL**, si `nano` está instalado:

  ```bash
  nano .env
  ```

En `nano`, guarda con `Ctrl + O`, confirma con Enter y sal con `Ctrl + X`.

La variable que espera el código es:

```ini
GEMINI_API_KEY=TU_CLAVE_REAL
```

Reemplaza `TU_CLAVE_REAL` por tu clave auténtica. Es solo un marcador de ejemplo, no una clave válida. No cambies el nombre `GEMINI_API_KEY`, ya que el código consulta exactamente esa variable.

### 7.3. Obtener y proteger la clave

Puedes gestionar la clave desde [Google AI Studio — API keys](https://aistudio.google.com/apikey).

La clave es un secreto: no la incluyas en el README, el código, commits, capturas de pantalla ni mensajes de error públicos. Si una clave real se publica o comparte por accidente, revócala o rótala desde el proveedor. Borrarla en un commit posterior no garantiza que deje de estar expuesta.

### 7.4. Comprobar que Git ignora `.env`

El `.gitignore` consultado ya incluye reglas para `.env`, `.venv/`, `venv/`, `env/`, cachés de Python y archivos de sistema/editor. Comprueba la regla efectiva desde la raíz:

```bash
git check-ignore -v .env
```

Si Git muestra una regla, podrás identificar el archivo y la línea que ignoran `.env`. Si no muestra salida, revisa `.gitignore` y el estado de seguimiento del archivo.

Como mínimo, las reglas relevantes deberían incluir:

```gitignore
.env
.venv/
venv/
__pycache__/
```

No reemplaces el `.gitignore` existente sin revisarlo: conserva sus otras reglas útiles y añade solo las que falten.

**Importante:** `.gitignore` no deja de seguir automáticamente un archivo que ya se había agregado a Git. Si `.env` ya está versionado, comprueba su estado antes de corregir el seguimiento y evita publicar cambios mientras contenga secretos. Si la clave ya se publicó, rótala.

## 8. Ejecutar la aplicación y los scripts

Ejecuta los comandos desde la raíz `Proyecto_skillnest`, con el entorno virtual activado y las dependencias instaladas. Los comandos siguientes usan `python`, que debería apuntar a `.venv` cuando está activado correctamente.

No es obligatorio ejecutar todos los scripts: elige el que corresponda a la tarea que quieras realizar.

### 8.1. Aplicación principal

```bash
python app.py
```

El código consultado carga `.env`, crea un cliente de Gemini y solicita una respuesta al modelo configurado en el archivo. Imprime una estructura de salida definida por el propio script. Necesitarás una clave válida y conectividad con el servicio.

### 8.2. Solicitud a Gemini desde `src/consumir_gemini.py`

```bash
python src/consumir_gemini.py
```

El archivo contiene funciones para preparar la solicitud, enviarla al servicio y extraer el texto de la respuesta. Revisa el código de la versión que tienes para conocer su flujo de ejecución completo. La función que arma la petición requiere `GEMINI_API_KEY`.

### 8.3. Comparar modelos, latencia y costo

El nombre del archivo contiene un espacio; conserva las comillas:

```bash
python "src/consumir_gemini costos_latencia.py"
```

El script consultado ejecuta preguntas de prueba contra varios modelos configurados, mide latencia y estima costos usando tarifas definidas en el propio código. Realiza varias solicitudes, por lo que puede tardar y consumir cuota de la API.

### 8.4. Prueba de consistencia de prompts

```bash
python prompts/test_consistencia.py
```

El script utiliza `prompts/banco.py`, realiza hasta tres intentos por prompt, clasifica los resultados y guarda un registro JSON en `prompts/registro_resultados.json`. Puede necesitar la clave de Gemini y conexión al servicio. No equivale necesariamente a una prueba automatizada de todo el proyecto.

## 9. Resultados y archivos generados

Distingue entre los archivos incluidos en el repositorio y los que se crean al ejecutar los scripts.

- **`prompts/registro_resultados.json`:** el script `prompts/test_consistencia.py` escribe aquí el registro de la ejecución. Si ya existe, la ejecución lo vuelve a escribir; revisa o conserva una copia si necesitas mantener el historial anterior.
- **`docs/resultados/`:** el script `src/consumir_gemini costos_latencia.py` crea el directorio si hace falta.
- **`docs/resultados/respuestas_<identificador>.md`:** el script de costos/latencia crea un informe Markdown con un identificador de ejecución basado en la fecha y hora.
- **`docs/resultados/registro_ejecuciones.jsonl`:** el mismo script agrega registros de cada solicitud en formato JSON Lines.
- **`docs/respuestas_completas.md`:** puede ser un informe de referencia existente. El script de comparación consultado escribe informes nuevos en `docs/resultados/`, no en esta ruta fija.

Los resultados concretos dependen de las solicitudes que terminen correctamente. Para verificar una ejecución, revisa el mensaje de la terminal, el código de salida del proceso y las rutas que el script informe. Si un programa termina sin imprimir lo esperado, consulta su código antes de asumir que hubo un error.

Los costos son estimaciones: dependen de las tarifas configuradas, el modelo solicitado y el consumo informado por la API. Las tarifas pueden cambiar; no interpretes los valores del código como precios universales ni como un importe definitivo de facturación.

## 10. Uso básico de Git

Ejecuta estos comandos desde la raíz del repositorio. Son comunes a PowerShell, CMD, macOS, Linux y WSL.

### 10.1. Consultar el estado

```bash
git status
```

Muestra la rama actual y los archivos modificados, nuevos o preparados para un commit.

### 10.2. Consultar el historial

```bash
git log --oneline
```

Muestra un resumen de los commits anteriores.

### 10.3. Revisar cambios sin preparar

```bash
git diff
```

Muestra los cambios que todavía no están preparados para el próximo commit.

### 10.4. Preparar un archivo concreto

```bash
git add README.md
```

Este ejemplo prepara únicamente `README.md`. Revisa `git status` antes de agregar archivos y no prepares `.env`, claves, entornos virtuales ni resultados sensibles.

### 10.5. Revisar los cambios preparados

```bash
git diff --cached
```

Revisa aquí el contenido exacto que entrará en el próximo commit.

### 10.6. Crear un commit

```bash
git commit -m "readme: actualizar guia de instalacion y uso"
```

Hazlo después de revisar los cambios preparados. Si Git solicita identidad, configura tu nombre y correo con los datos que quieras asociar a tus commits.

### 10.7. Enviar cambios al repositorio remoto

```bash
git push origin main
```

Este comando supone que el remoto se llama `origin`, que la rama se llama `main` y que tienes permisos. Comprueba `git status` y utiliza la rama correcta si tiene otro nombre.

### 10.8. Actualizar la copia local

```bash
git pull
```

Antes de actualizar, comprueba la rama actual y el estado de los cambios locales para evitar conflictos o sobrescrituras no deseadas.

No ejecutes `git add .` automáticamente. Revisa primero `git status` y selecciona de forma explícita los archivos que quieres publicar.

## 11. Solución de problemas frecuentes

### Python no se reconoce

1. Comprueba `python --version`; en Windows prueba `py --version` y en macOS/Linux/WSL prueba `python3 --version`.
2. Si no hay una versión disponible, instala Python.
3. Si está instalado, revisa `PATH` y vuelve a abrir la terminal.
4. Si ya creaste `.venv`, actívalo antes de ejecutar los comandos del proyecto.

### Git no se reconoce

Ejecuta `git --version`. Si falla, instala Git según la sección 2.2 y vuelve a abrir la terminal.

### `fatal: not a git repository`

La terminal probablemente está fuera del repositorio. Comprueba la ubicación con `pwd` (PowerShell/macOS/Linux/WSL) o `cd` (CMD), lista los archivos y entra en la carpeta que contiene `.git` y `README.md`. Después, vuelve a ejecutar `git status`.

### No se encuentra `requirements.txt`

Comprueba que estás en la raíz `Proyecto_skillnest`. Lista los archivos con `Get-ChildItem` (PowerShell), `dir` (CMD) o `ls -la` (macOS/Linux/WSL). No crees un archivo vacío ni reinstales Python como primera solución.

### No se puede activar el entorno virtual

Comprueba que `.venv` existe y que se creó desde la raíz correcta. Usa el comando de activación de la sección 5.2 para tu terminal. Si PowerShell bloquea el script, aplica la alternativa temporal de la sección 5.2 y vuelve a intentar la activación.

### No se encuentra `GEMINI_API_KEY`

1. Comprueba que `.env` existe en la raíz.
2. Confirma que la variable se llama exactamente `GEMINI_API_KEY`.
3. Guarda los cambios del archivo.
4. Revisa que el script cargue las variables de entorno; los scripts consultados utilizan `load_dotenv()`.
5. Comprueba la validez y los permisos de la clave sin imprimirla ni compartirla.

### Error 401 o 403 de Gemini

Puede estar relacionado con credenciales, permisos, acceso al modelo o configuración del servicio. Revisa el mensaje completo de la API, la clave y los permisos aplicables; el código de estado por sí solo no siempre determina una causa única.

### Error 429

Puede indicar límites de solicitudes, cuota o frecuencia de uso. Revisa la cuota y las condiciones vigentes del proveedor. Evita reintentar de forma agresiva; algunos scripts incorporan pausas o reintentos.

### Error 503

Puede indicar indisponibilidad o saturación temporal del servicio. Consulta el estado del servicio y, si corresponde, vuelve a intentarlo prudentemente. El comportamiento depende del script: algunos reintentan ciertas solicitudes y otros devuelven un error.

### No aparecen resultados

Confirma que ejecutaste el script correcto desde la raíz. Revisa si imprime información por consola o guarda archivos, el mensaje de error, el código de salida y las rutas de salida descritas en la sección 9. Un script que no imprime una respuesta no necesariamente ha fallado; verifica su comportamiento en el código.

### Los costos o la latencia son diferentes

Pueden variar según el modelo solicitado y el modelo que responda, las entradas, la cantidad de solicitudes, el tiempo de respuesta, los reintentos, el uso de tokens y las tarifas vigentes. Comprueba los valores configurados en el script antes de comparar resultados.

## 12. Buenas prácticas

- Usa un entorno virtual por proyecto y actívalo antes de instalar o ejecutar dependencias.
- Ejecuta los comandos desde la raíz del repositorio, salvo que una instrucción indique otra ruta.
- Mantén la clave fuera del código y del control de versiones; no compartas `.env`.
- Revisa `git status` antes de preparar cambios y `git diff --cached` antes de crear un commit.
- No publiques `.venv/`, cachés, archivos temporales ni datos sensibles.
- Utiliza `requirements.txt` como referencia de las dependencias instaladas.
- Conserva los registros que necesites para comparar ejecuciones antes de volver a generarlos.
- Comprueba los errores y el código real antes de aplicar soluciones o afirmar que una ejecución produjo un resultado.
- Revisa las tarifas y los modelos configurados antes de interpretar las estimaciones de costos.

## 13. Resumen de instalación y ejecución

Si ya tienes el repositorio clonado, abre una terminal en la carpeta raíz `Proyecto_skillnest`. Si `.venv` ya existe, omite la creación del entorno.

### Crear el entorno virtual

**Windows — PowerShell o CMD:**

```powershell
python -m venv .venv
```

Si `python` no se reconoce, prueba `py -m venv .venv`.

**macOS, Ubuntu, Linux o WSL:**

```bash
python3 -m venv .venv
```

### Activar el entorno virtual

Usa solo el comando que corresponda a la terminal que abriste:

- **PowerShell:** `.\.venv\Scripts\Activate.ps1`
- **CMD:** `.venv\Scripts\activate.bat`
- **macOS, Ubuntu, Linux o WSL:** `source .venv/bin/activate`

### Instalar dependencias y ejecutar

Con el entorno activado, estos comandos son iguales en PowerShell, CMD, macOS, Linux y WSL:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Configura `.env` según la sección 7 si vas a ejecutar scripts que necesitan Gemini. Para iniciar la aplicación principal:

```bash
python app.py
```

Consulta la sección 8 para los otros scripts y la sección 11 si aparece un error.

## Referencias

- [Repositorio Proyecto_skillnest en GitHub](https://github.com/Sadzc/Proyecto_skillnest)
- [Descargas de Python](https://www.python.org/downloads/)
- [Descargas de Git](https://git-scm.com/downloads)
- [Descargas de Visual Studio Code](https://code.visualstudio.com/)
- [Google AI Studio — API keys](https://aistudio.google.com/apikey)
