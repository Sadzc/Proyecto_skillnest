# Asistente de Documentación de Data Warehouse

Este repositorio contiene el desarrollo de un asistente inteligente para consultar documentación de un Data Warehouse mediante modelos de lenguaje y técnicas de RAG (*Retrieval-Augmented Generation*). El proyecto forma parte de la Especialización en Desarrollo con IA Generativa de Skillnest y Accenture.

La solución busca responder preguntas sobre columnas, modelos y métricas de negocio utilizando documentación como archivos `schema.yml`, descripciones de modelos dbt y definiciones de KPIs, citando las fuentes utilizadas e identificando posibles brechas de documentación.

Esta guía está pensada para personas con o sin experiencia en programación. Puedes configurar y ejecutar el proyecto de dos maneras:

- **Camino A — VS Code:** utiliza una interfaz visual y una terminal integrada.
- **Camino B — Terminal:** permite realizar todo el proceso mediante comandos, sin necesidad de instalar VS Code.

Ambos caminos permiten preparar el proyecto. Elige uno para comenzar; no necesitas completar los dos.

---

## 1. Herramientas necesarias

Antes de comenzar, necesitas:

- **Python 3:** permite ejecutar el código del proyecto.
- **pip:** instala las dependencias de Python.
- **Git:** descarga el repositorio y permite gestionar los cambios.
- **Clave de API de Gemini:** necesaria para los scripts que realizan consultas al modelo.
- **VS Code:** opcional; se utiliza en el Camino A.

También necesitarás conexión a Internet para descargar el proyecto, instalar las dependencias y realizar consultas a la API.

### 1.1. Instalar y comprobar Python

Python es el lenguaje utilizado por el proyecto. Primero comprueba si ya está instalado.

**Windows — PowerShell**

Abre PowerShell y ejecuta:

```powershell
python --version
```

Si aparece un mensaje indicando que no se reconoce el comando, prueba:

```powershell
py --version
```

**Windows — CMD (Símbolo del sistema)**

Abre CMD y ejecuta:

```cmd
python --version
```

Si no funciona, prueba:

```cmd
py --version
```

Si ninguno funciona, instala Python desde [python.org](https://www.python.org/downloads/). Durante la instalación, si aparece la opción **Add Python to PATH**, actívala. Después, cierra y vuelve a abrir la terminal.

**macOS — Terminal**

```bash
python3 --version
```

Si Python no está instalado, utiliza el instalador oficial de [Python](https://www.python.org/downloads/).

**Linux — Ubuntu**

```bash
python3 --version
```

Si no está instalado, ejecuta:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

Introduce tu contraseña si Ubuntu la solicita. Mientras escribes la contraseña en la terminal, es normal que no aparezcan caracteres en pantalla.

**Si utilizas WSL:** WSL permite ejecutar Linux dentro de Windows. Python instalado en Windows no queda instalado automáticamente dentro de Ubuntu/WSL.

Una respuesta como `Python 3.12.4` indica que Python está disponible. El número de versión puede ser diferente.

### 1.2. Instalar y comprobar Git

Git permite descargar el proyecto desde GitHub.

Descárgalo desde [git-scm.com/downloads](https://git-scm.com/downloads) si todavía no lo tienes instalado.

**Windows — PowerShell o CMD**

```powershell
git --version
```

Si no está instalado, puedes descargarlo desde la página oficial o, si tu sistema dispone de `winget`, ejecutar en PowerShell:

```powershell
winget install --id Git.Git -e
```

Después, cierra y vuelve a abrir la terminal.

**macOS — Terminal**

```bash
git --version
```

Si macOS indica que necesitas herramientas de desarrollo, puedes ejecutar:

```bash
xcode-select --install
```

Sigue las instrucciones que aparezcan en pantalla.

**Linux — Ubuntu**

```bash
git --version
```

Si no está instalado:

```bash
sudo apt update
sudo apt install git
```

Para comprobar que todo quedó correctamente instalado, vuelve a ejecutar `git --version`. Deberías ver un número de versión.

### 1.3. Instalar VS Code (opcional)

Si utilizarás el Camino A, descarga Visual Studio Code desde:

[https://code.visualstudio.com/download](https://code.visualstudio.com/download)

Si prefieres trabajar exclusivamente con terminal, puedes omitir este paso.

---

## 2. Obtener el proyecto

Repositorio de GitHub:

[https://github.com/Sadzc/Proyecto_skillnest](https://github.com/Sadzc/Proyecto_skillnest)

### Camino A — Descargar el proyecto mediante VS Code

**Paso 1. Abre VS Code.**

Inicia Visual Studio Code desde el menú de aplicaciones de tu sistema operativo.

**Paso 2. Abre la paleta de comandos.**

- Windows y Linux: presiona `Ctrl + Shift + P`.
- macOS: presiona `Cmd + Shift + P`.

Aparecerá una barra de búsqueda en la parte superior de la ventana.

**Paso 3. Busca Git Clone.**

Escribe:

```text
Git: Clone
```

Selecciona la opción que aparezca en los resultados.

**Paso 4. Introduce la dirección del repositorio.**

Copia y pega esta dirección:

```text
https://github.com/Sadzc/Proyecto_skillnest.git
```

Presiona Enter.

**Paso 5. Elige dónde guardar el proyecto.**

VS Code abrirá una ventana para seleccionar la carpeta de destino. Elige una ubicación fácil de encontrar, como Documentos o una carpeta de proyectos.

Espera a que termine la descarga.

**Paso 6. Abre el repositorio.**

Si VS Code pregunta si quieres abrir el repositorio clonado, selecciona **Open** o **Abrir**.

Deberías ver el contenido del proyecto en el panel izquierdo.

Si el repositorio es privado, necesitarás autorización y autenticarte con una cuenta que tenga acceso.

### Camino B — Descargar el proyecto desde la terminal

Primero, abre una terminal:

- **Windows:** busca PowerShell o CMD en el menú Inicio.
- **macOS:** abre Terminal desde Aplicaciones o Spotlight.
- **Ubuntu:** abre Terminal desde el menú de aplicaciones.
- **WSL:** abre tu distribución Ubuntu.

Ejecuta el siguiente comando, según tu sistema.

**Windows — PowerShell**

```powershell
git clone https://github.com/Sadzc/Proyecto_skillnest.git
cd Proyecto_skillnest
```

**Windows — CMD (Símbolo del sistema)**

```cmd
git clone https://github.com/Sadzc/Proyecto_skillnest.git
cd Proyecto_skillnest
```

**macOS, Linux o WSL — Terminal**

```bash
git clone https://github.com/Sadzc/Proyecto_skillnest.git
cd Proyecto_skillnest
```

El primer comando descarga el repositorio en una carpeta llamada `Proyecto_skillnest`. El segundo entra en esa carpeta.

Si aparece un error que indica que `git` no se reconoce, vuelve a la sección 1.2.

Si aparece un error relacionado con permisos o autenticación, comprueba que el repositorio sea accesible para tu cuenta.

### 2.1. Comprueba que descargaste el proyecto

Una vez dentro de la carpeta, ejecuta:

```bash
git status
```

Este comando consulta el estado del repositorio. Si está limpio, verás un mensaje parecido a:

```text
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

El texto puede variar si existen cambios locales o si la rama tiene otro nombre.

Ahora comprueba que los archivos se hayan descargado.

**Windows — PowerShell**

```powershell
Get-ChildItem
```

**Windows — CMD**

```cmd
dir
```

**macOS, Linux o WSL**

```bash
ls -la
```

En la carpeta raíz deberías encontrar archivos como `README.md`, `requirements.txt` y `.env.example`, siempre que formen parte de la versión actual del repositorio.

Si no los encuentras, comprueba que estés dentro de `Proyecto_skillnest` y no en la carpeta que la contiene.

---

## 3. Estructura del repositorio

La siguiente estructura es una referencia de los archivos y directorios del proyecto. Puede variar si se agregan archivos o si algunas carpetas se generan durante la ejecución.

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

**Función de los archivos principales**

| Archivo o carpeta | Función |
|---|---|
| `app.py` | Punto de entrada de la aplicación, según su implementación actual. |
| `src/consumir_gemini.py` | Realiza una consulta individual a Gemini y gestiona la respuesta y el costo estimado. |
| `src/consumir_gemini costos_latencia.py` | Script de comparación de modelos y medición de latencia y costo. |
| `prompts/banco.py` | Banco de prompts del proyecto. |
| `prompts/test_consistencia.py` | Ejecuta pruebas de consistencia de prompts. |
| `prompts/registro_resultados.json` | Archivo de resultados de pruebas, si está presente en la versión descargada. |
| `docs/decision-arquitectura.md` | Documento de decisiones de arquitectura. |
| `docs/diagrama_arquitectura.png` | Diagrama de arquitectura. |
| `docs/evidencia_peticion_autenticada.png` | Evidencia visual de una petición autenticada. |
| `docs/respuestas_completas.md` | Informe de referencia, si está incluido o se genera durante la ejecución. |
| `docs/resultados/` | Carpeta destinada a informes o resultados, si la versión del script la utiliza. |
| `.env.example` | Plantilla de configuración sin tu clave personal. |
| `.env` | Archivo local donde se configura la clave de API. No debe publicarse. |
| `.gitignore` | Define qué archivos locales debe ignorar Git. |
| `requirements.txt` | Lista las dependencias de Python. |
| `.venv/` | Entorno virtual local recomendado para esta guía. No debe subirse a GitHub. |

No es necesario que todas las carpetas de resultados existan antes de ejecutar el proyecto.

---

## 4. Crear el entorno virtual

Un entorno virtual mantiene las dependencias de este proyecto separadas de las de otros proyectos de Python.

En esta guía utilizaremos siempre una carpeta llamada **`.venv`** para evitar confusiones entre los distintos sistemas y VS Code.

Debes crear el entorno una sola vez. Cuando abras una terminal nueva, normalmente tendrás que activarlo de nuevo.

### Camino A — Crear el entorno desde VS Code

**Paso 1. Instala la extensión de Python.**

1. En la barra izquierda de VS Code, haz clic en el icono de **Extensiones**. Parece un conjunto de cuadrados.
2. Escribe `Python` en el buscador.
3. Busca la extensión **Python**, publicada por Microsoft.
4. Haz clic en **Instalar** y espera a que termine.

**Paso 2. Abre la paleta de comandos.**

Presiona `Ctrl + Shift + P` en Windows/Linux o `Cmd + Shift + P` en macOS.

**Paso 3. Busca la opción para crear el entorno.**

Escribe:

```text
Python: Create Environment
```

Selecciona esa opción en los resultados.

**Paso 4. Elige el tipo de entorno.**

Selecciona `Venv`.

**Paso 5. Selecciona el intérprete de Python.**

VS Code mostrará las versiones de Python que detecta en tu equipo. Selecciona una versión instalada y compatible.

Espera mientras VS Code crea el entorno virtual. Puede tardar unos momentos.

**Paso 6. Comprueba la terminal.**

En el menú superior, selecciona **Terminal → Nueva terminal**.

Normalmente, VS Code detectará el entorno y lo activará automáticamente. Deberías ver algo parecido a:

```text
(.venv)
```

al comienzo de la línea de comandos.

Para comprobar la versión de Python, ejecuta el comando que corresponda a tu terminal:

**Windows — PowerShell o CMD**

```powershell
python --version
```

Si `python` no funciona, prueba `py --version` en una terminal compatible.

**macOS, Linux o WSL**

```bash
python --version
```

Si no funciona, prueba:

```bash
python3 --version
```

**¿No aparece `Python: Create Environment`?**

- Comprueba que la extensión Python de Microsoft esté instalada.
- Verifica que hayas abierto la carpeta del proyecto.
- Comprueba que Python esté instalado.
- Si VS Code no detecta ningún intérprete, reinícialo después de instalar Python.
- Si no consigues crear el entorno desde VS Code, utiliza el Camino B.

**Importante:** si VS Code crea una carpeta llamada `venv` en lugar de `.venv`, puedes continuar usando esa carpeta, pero debes mantener el mismo nombre en todos los comandos posteriores. Esta guía utiliza `.venv`.

### Camino B — Crear el entorno desde la terminal

Primero, confirma que estás en la raíz del proyecto, donde se encuentra `requirements.txt`.

**Windows — PowerShell**

```powershell
Get-Location
```

**Windows — CMD**

```cmd
cd
```

**macOS, Linux o WSL**

```bash
pwd
```

La ruta debe terminar en `Proyecto_skillnest`. Si no es así, entra en la carpeta correcta utilizando `cd` seguido de su ruta.

Ahora crea el entorno.

**Windows — PowerShell**

```powershell
python -m venv .venv
```

Si no se reconoce `python`:

```powershell
py -m venv .venv
```

**Windows — CMD**

```cmd
python -m venv .venv
```

Si no se reconoce `python`:

```cmd
py -m venv .venv
```

**macOS, Linux o WSL**

```bash
python3 -m venv .venv
```

El comando puede terminar sin mostrar ningún mensaje. Eso es normal: si no aparecen errores, comprueba que se haya creado la carpeta `.venv`.

**Si Ubuntu muestra un error relacionado con `venv`:**

Instala el paquete necesario:

```bash
sudo apt update
sudo apt install python3-venv python3-pip
```

Después, vuelve a ejecutar el comando de creación del entorno.

### 4.1. Activar el entorno virtual

Crear el entorno no es lo mismo que activarlo. Ejecuta el comando correspondiente a tu terminal.

**Windows — PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea el script, puedes permitir su ejecución solo en la sesión actual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Después, vuelve a ejecutar el comando de activación.

Este ajuste solo afecta a la sesión actual de PowerShell. Si prefieres no modificar esa configuración temporal, puedes utilizar CMD.

**Windows — CMD**

```cmd
.venv\Scripts\activate.bat
```

**macOS, Linux o WSL**

```bash
source .venv/bin/activate
```

Si la activación funciona, normalmente aparecerá `(.venv)` al comienzo de la línea de comandos.

Para comprobar que el entorno existe, puedes listar los archivos de la carpeta del proyecto:

- PowerShell: `Get-ChildItem`
- CMD: `dir`
- macOS, Linux o WSL: `ls -la`

Si `.venv` no aparece, vuelve a crear el entorno desde la raíz correcta.

### 4.2. Salir del entorno virtual

Cuando termines de trabajar, puedes desactivarlo con:

```bash
deactivate
```

El comando funciona en las terminales habituales donde el entorno está activado.

La próxima vez que abras una terminal, vuelve a activar el entorno. No necesitas crearlo otra vez si la carpeta `.venv` sigue existiendo.

---

## 5. Instalar las dependencias

Las dependencias son las bibliotecas que necesita el proyecto para funcionar. Están enumeradas en `requirements.txt`.

Antes de instalarlas:

1. Comprueba que estás en la raíz del repositorio.
2. Activa el entorno virtual.
3. Verifica que `requirements.txt` exista.

Es preferible utilizar `python -m pip` o `python3 -m pip` para instalar los paquetes en el entorno de Python correcto.

**Windows — PowerShell o CMD**

Si `python` funciona:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si necesitas utilizar el lanzador `py`:

```powershell
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

**macOS, Linux o WSL**

Si `python` funciona dentro del entorno activado:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si necesitas utilizar `python3`:

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

Espera a que termine la instalación. Puede aparecer bastante texto en la terminal; eso es normal.

Para comprobar que pip está disponible, ejecuta:

```bash
python -m pip --version
```

En macOS o Linux, si utilizas `python3`, puedes ejecutar:

```bash
python3 -m pip --version
```

Si aparece un error de archivo no encontrado para `requirements.txt`, vuelve a comprobar tu ubicación. Si aparece un error durante la instalación de una dependencia, revisa el mensaje concreto antes de continuar.

---

## 6. Configurar las variables de entorno

Los scripts que consultan Gemini necesitan una clave de API. La guardaremos en un archivo llamado `.env`, separado del código fuente.

**Importante:** `.env.example` es una plantilla. No contiene tu clave personal. Debes crear una copia llamada `.env` y editarla.

### 6.1. Crear el archivo `.env`

Primero, comprueba que `.env.example` exista en la raíz del repositorio.

**Windows — PowerShell**

```powershell
Test-Path .env.example
```

Si devuelve `True`, puedes crear la copia:

```powershell
Copy-Item .env.example .env
```

**Windows — CMD**

```cmd
dir .env.example
copy .env.example .env
```

**macOS, Linux o WSL**

```bash
ls -l .env.example
cp .env.example .env
```

Estos comandos crean `.env` en la carpeta actual.

**Si `.env` ya existe:** no lo sobrescribas automáticamente, porque podrías perder una clave que ya hayas configurado. Abre el archivo existente y edítalo.

Si `.env.example` no existe, comprueba que estés en la raíz del proyecto y revisa el contenido real del repositorio antes de continuar.

### 6.2. Abrir y editar `.env`

Puedes editar el archivo desde VS Code o mediante un editor de texto.

**Opción A — VS Code**

1. En el panel izquierdo, busca el archivo `.env`.
2. Haz clic en él para abrirlo.
3. Edita la línea correspondiente a la clave.
4. Guarda con `Ctrl + S` en Windows/Linux o `Cmd + S` en macOS.

Si el archivo no aparece, revisa que lo hayas creado correctamente. Algunos archivos que empiezan por punto pueden no ser visibles en ciertos paneles o exploradores.

**Opción B — Windows PowerShell**

```powershell
notepad .env
```

**Opción C — Windows CMD**

```cmd
notepad .env
```

Se abrirá el Bloc de notas. Si Windows pregunta si deseas crear un archivo nuevo, cancela y verifica primero que `.env` exista.

**Opción D — macOS**

```bash
open -e .env
```

Este comando intenta abrir el archivo con TextEdit.

**Opción E — Linux o Ubuntu**

Si tienes instalado `nano`:

```bash
nano .env
```

Para guardar en `nano`, presiona `Ctrl + O`, confirma con Enter y sal con `Ctrl + X`.

### 6.3. Agregar la clave de Gemini

Obtén tu clave desde el servicio oficial:

[https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)

En el archivo `.env`, configura la variable con el nombre exacto esperado por el proyecto:

```dotenv
GEMINI_API_KEY=TU_CLAVE_REAL
```

Reemplaza `TU_CLAVE_REAL` por tu clave personal. Esa expresión es un ejemplo, no una clave válida.

No agregues la clave al código Python, no la publiques en GitHub y no la compartas en capturas de pantalla o mensajes.

Guarda el archivo después de editarlo.

### 6.4. Comprobar que `.env` existe

**Windows — PowerShell**

```powershell
Test-Path .env
```

El resultado esperado es:

```text
True
```

**Windows — CMD**

```cmd
dir .env
```

**macOS, Linux o WSL**

```bash
ls -la .env
```

Estos comandos permiten comprobar que el archivo existe. No demuestran por sí solos que la clave sea válida ni que el programa esté leyendo correctamente las variables de entorno.

### 6.5. Comprobar que Git ignora `.env`

Ejecuta el siguiente comando desde la raíz del repositorio. Funciona en PowerShell, CMD, macOS, Linux y WSL:

```bash
git check-ignore -v .env
```

Si Git muestra una regla de `.gitignore`, el archivo está siendo ignorado por esa regla.

Si no aparece ninguna salida, revisa `.gitignore` y confirma que incluya, como mínimo:

```gitignore
.env
.venv/
venv/
__pycache__/
```

Si `.env` ya estaba versionado anteriormente, agregarlo a `.gitignore` no lo elimina del historial ni deja de versionarlo automáticamente. En ese caso, comprueba el estado del repositorio antes de publicar cambios.

**Nunca subas una clave de API a GitHub.** Si una clave real se publicó o compartió por error, revócala y genera una nueva.

---

## 7. Ejecutar los scripts

Antes de ejecutar un script, comprueba lo siguiente:

- Estás en la raíz del repositorio.
- El entorno virtual está activado.
- Las dependencias se instalaron correctamente.
- El archivo `.env` existe y contiene la variable necesaria.
- Tu clave de API es válida y tienes acceso al modelo configurado.

Los comandos de esta sección se ejecutan desde la raíz del proyecto, no desde dentro de `src` o `prompts`.

### 7.1. Aplicación principal: `app.py`

**Windows — PowerShell o CMD**

```powershell
python app.py
```

Si necesitas usar el lanzador de Windows:

```powershell
py app.py
```

**macOS, Linux o WSL**

```bash
python app.py
```

Si necesitas utilizar `python3`:

```bash
python3 app.py
```

La salida exacta depende de la implementación de `app.py`. Si el archivo ejecuta una consulta a Gemini, necesitará que la configuración de la API sea correcta.

No se debe asumir que muestra una interfaz gráfica, que repite solicitudes o que guarda resultados, salvo que eso esté implementado en el código.

### 7.2. Consulta individual a Gemini

Archivo: `src/consumir_gemini.py`.

**Windows — PowerShell o CMD**

```powershell
python src/consumir_gemini.py
```

**macOS, Linux o WSL**

```bash
python src/consumir_gemini.py
```

Si utilizas el lanzador `py` en Windows o `python3` en macOS/Linux, sustituye el nombre del ejecutable según corresponda.

Este script realiza una petición a Gemini y calcula un costo estimado a partir de los datos de uso disponibles en la respuesta. La salida concreta depende de la respuesta de la API y de las tarifas configuradas en el código.

Si aparece un error, conserva el mensaje completo para poder identificar si se trata de un problema de credenciales, conexión, cuota, modelo o respuesta del servicio.

### 7.3. Comparativa de modelos, latencia y costo

Archivo: `src/consumir_gemini costos_latencia.py`.

El nombre contiene espacios, por lo que debes mantener las comillas alrededor de la ruta.

**Windows — PowerShell o CMD**

```powershell
python "src/consumir_gemini costos_latencia.py"
```

**macOS, Linux o WSL**

```bash
python "src/consumir_gemini costos_latencia.py"
```

La comparativa utiliza los modelos configurados en el script. Puede tardar más que una petición individual si realiza varias solicitudes o reintenta operaciones.

Los archivos de salida dependen de la versión actual del script. Revisa los mensajes de la terminal y las rutas configuradas en el código para saber dónde se guardaron los resultados.

Los costos son estimaciones basadas en las tarifas configuradas. Antes de interpretar las cifras, comprueba que los modelos y los precios correspondan a la API utilizada.

### 7.4. Prueba de consistencia de prompts

Archivo: `prompts/test_consistencia.py`.

**Windows — PowerShell o CMD**

```powershell
python prompts/test_consistencia.py
```

**macOS, Linux o WSL**

```bash
python prompts/test_consistencia.py
```

La salida depende de los prompts configurados, de las respuestas del modelo y de la disponibilidad de la API. Si falla una solicitud, revisa el error devuelto antes de concluir que el código está defectuoso.

---

## 8. Resultados y archivos generados

Los resultados dependen de los scripts que ejecutes y de cómo esté configurada la versión actual del proyecto.

Entre los archivos y directorios de referencia pueden encontrarse:

- `docs/respuestas_completas.md`: informe de comparación, si está incluido o se genera en la ejecución.
- `docs/resultados/`: carpeta destinada a resultados.
- `prompts/registro_resultados.json`: registro de pruebas de consistencia, si el script lo utiliza.

No asumas que todos estos archivos se crearán automáticamente. Comprueba los mensajes que aparecen en la terminal y las rutas de salida definidas en el script correspondiente.

Si necesitas conservar la trazabilidad de las pruebas, no elimines los informes históricos ni los registros acumulados sin revisar primero su contenido.

---

## 9. Uso básico de Git

Esta sección es opcional si solo quieres ejecutar el proyecto. Git también permite guardar y publicar cambios en el repositorio.

Los comandos siguientes se pueden utilizar en PowerShell, CMD, macOS, Linux y WSL, siempre que estés dentro de la carpeta del repositorio.

### 9.1. Revisar el estado

```bash
git status
```

Muestra los archivos modificados, los archivos nuevos y los cambios preparados para un commit.

### 9.2. Consultar el historial

```bash
git log --oneline
```

Muestra un resumen de los commits anteriores.

### 9.3. Preparar un archivo específico

Por ejemplo, para preparar solo el README:

```bash
git add README.md
```

### 9.4. Revisar los cambios preparados

```bash
git diff --cached
```

Este comando permite revisar qué cambios se incluirán en el próximo commit.

### 9.5. Crear un commit

```bash
git commit -m "Actualiza documentación"
```

Un commit registra los cambios que preparaste localmente.

### 9.6. Publicar los cambios

```bash
git push origin main
```

Este comando intenta subir los commits locales a la rama `main` del repositorio remoto. Necesitarás los permisos y la autenticación correspondientes.

Si el repositorio utiliza otra rama, comprueba primero el nombre con `git status`.

### 9.7. Descargar cambios remotos

```bash
git pull
```

Descarga e integra los cambios de la rama remota configurada.

**Importante:** antes de ejecutar `git add .`, revisa `git status`. No prepares ni publiques `.env`, claves de API, archivos sensibles o la carpeta `.venv`.

---

## 10. Solución de problemas

### Python no se reconoce

- Windows: prueba `py --version`.
- macOS, Linux o WSL: prueba `python3 --version`.
- Si Python está instalado pero no se encuentra, cierra y vuelve a abrir la terminal.
- En WSL, recuerda que Python debe estar disponible dentro del entorno Linux.

### Git no se reconoce

Comprueba que Git esté instalado y vuelve a abrir la terminal. Si el problema persiste, revisa la instalación desde [git-scm.com/downloads](https://git-scm.com/downloads).

### No se encuentra `requirements.txt`

Probablemente estás en una carpeta incorrecta.

- PowerShell: ejecuta `Get-ChildItem`.
- CMD: ejecuta `dir`.
- macOS, Linux o WSL: ejecuta `ls -la`.

Entra en la carpeta `Proyecto_skillnest` y vuelve a intentarlo.

### No se encuentra el comando de activación

Comprueba que el entorno se haya creado y que estés utilizando el comando correspondiente a tu sistema:

- PowerShell: `.\.venv\Scripts\Activate.ps1`
- CMD: `.venv\Scripts\activate.bat`
- macOS, Linux o WSL: `source .venv/bin/activate`

Si creaste el entorno con otro nombre, utiliza ese nombre en la ruta.

### PowerShell bloquea la activación

Puedes permitir la ejecución del script solo durante la sesión actual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Después, vuelve a ejecutar el comando de activación. Como alternativa, utiliza CMD y ejecuta `.venv\Scripts\activate.bat`.

### No se encuentra `GEMINI_API_KEY`

1. Comprueba que `.env` exista en la raíz del proyecto.
2. Abre el archivo y confirma que la variable se llama exactamente `GEMINI_API_KEY`.
3. Comprueba que hayas guardado el archivo.
4. Verifica que la clave sea válida y tenga los permisos necesarios.
5. Confirma que el código del script cargue o lea correctamente las variables de entorno.

No publiques el contenido del archivo para solicitar ayuda.

### La API devuelve un error 401 o 403

Puede existir un problema con la clave, los permisos, el acceso al modelo o la configuración del servicio. Comprueba las credenciales y los permisos de tu cuenta.

### La API devuelve un error 429

Puede indicar que alcanzaste un límite de solicitudes o cuota. Revisa los límites de tu cuenta y espera antes de volver a intentarlo.

### La API devuelve un error 503

El servicio puede estar temporalmente saturado. El comportamiento ante este error depende del script: algunos pueden reintentar solicitudes y otros devolverán un error directamente.

### El costo parece incorrecto

Verifica las tarifas configuradas en el código, el modelo utilizado y los datos de uso devueltos por la API. El costo calculado puede no coincidir con una factura si las tarifas, los tipos de tokens o las condiciones del servicio son diferentes.

### El comando termina sin mostrar resultados

Comprueba el código del script para identificar qué debería imprimir o guardar. No todos los scripts generan informes ni muestran una respuesta en pantalla.

---

## 11. Buenas prácticas

- No escribas claves de API directamente en el código fuente.
- No publiques `.env` ni compartas su contenido.
- Mantén `.env` y `.venv/` excluidos de Git.
- Activa el entorno virtual antes de ejecutar los scripts.
- Mantén `requirements.txt` actualizado cuando cambien las dependencias.
- Revisa los resultados antes de sobrescribir o eliminar informes históricos.
- Verifica los modelos y las tarifas configuradas antes de interpretar las métricas.
- Revisa `git status` antes de preparar y publicar cambios.
- Si compartes un error para recibir ayuda, elimina las claves, tokens y demás datos sensibles del mensaje.

---

## 12. Flujo de trabajo resumido

Para preparar el proyecto desde cero:

1. Instala Python y Git.
2. Descarga el repositorio mediante VS Code o la terminal.
3. Entra en la carpeta `Proyecto_skillnest`.
4. Crea el entorno virtual `.venv`.
5. Activa el entorno virtual.
6. Instala las dependencias desde `requirements.txt`.
7. Crea el archivo `.env` a partir de `.env.example`.
8. Abre `.env`, agrega tu clave de API de Gemini y guarda los cambios.
9. Comprueba que Git ignore `.env`.
10. Ejecuta el script que necesites.
11. Revisa los mensajes de la terminal y los resultados generados.
12. Si realizaste cambios en el proyecto, revisa el estado de Git antes de crear commits o publicarlos.

**Recuerda:** puedes completar la configuración y ejecutar los scripts usando únicamente la terminal. VS Code es opcional.