# Asistente de Documentación de Data Warehouse

Este repositorio contiene el desarrollo de un asistente inteligente para consultar documentación de un Data Warehouse mediante modelos de lenguaje y técnicas de RAG (*Retrieval-Augmented Generation*). El proyecto forma parte de la Especialización en Desarrollo con IA Generativa de Skillnest y Accenture.

La solución busca responder preguntas sobre columnas, modelos y métricas de negocio utilizando documentación como archivos `schema.yml`, descripciones de modelos dbt y definiciones de KPIs, citando las fuentes utilizadas e identificando posibles brechas de documentación.

Esta guía permite instalar y ejecutar el proyecto de dos formas:

- **Camino A — VS Code:** alternativa visual para quienes prefieren trabajar con un editor.
- **Camino B — Terminal:** permite realizar todo el proceso sin VS Code, desde clonar el repositorio hasta configurar las credenciales y ejecutar los scripts.

Ambos caminos llegan al mismo resultado. No necesitas completar los dos: elige uno y sigue sus instrucciones.

---

## 1. Herramientas necesarias

- **Python 3:** ejecuta el código del proyecto.
- **pip:** instala las dependencias de Python.
- **Git:** permite clonar el repositorio y registrar cambios.
- **Cuenta de GitHub:** necesaria para acceder al repositorio si se requieren permisos.
- **Clave de API de Gemini:** necesaria para los scripts que consultan el modelo.
- **VS Code:** opcional; solo se necesita si eliges el Camino A.

### 1.1. Instalar Python

Descarga Python desde https://www.python.org/downloads/.

**Windows — PowerShell:**

```powershell
python --version
```

Si no se reconoce `python`:

```powershell
py --version
```

**Windows — CMD (Símbolo del sistema):**

```cmd
python --version
```

Si no se reconoce:

```cmd
py --version
```

Si ninguno funciona, instala Python y marca la opción **Add Python to PATH** durante la instalación. Después, cierra y vuelve a abrir la terminal.

**macOS — Terminal:**

```bash
python3 --version
```

Si no está instalado, utiliza el instalador oficial de Python.

**Linux / WSL — Terminal:**

```bash
python3 --version
```

Si no está instalado en Ubuntu o WSL:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

> WSL es un entorno Linux dentro de Windows. Instalar Python en Windows no lo instala automáticamente dentro de Ubuntu/WSL.

### 1.2. Instalar Git

Descarga Git desde https://git-scm.com/downloads.

**Windows — PowerShell:**

```powershell
git --version
```

**Windows — CMD (Símbolo del sistema):**

```cmd
git --version
```

Si Git no está instalado en Windows, puedes instalarlo desde el sitio oficial o, si está disponible, mediante:

```powershell
winget install --id Git.Git -e
```

**macOS — Terminal:**

```bash
git --version
```

Si no está instalado, puedes ejecutar:

```bash
xcode-select --install
```

**Linux / WSL — Terminal:**

```bash
sudo apt update
sudo apt install git
```

Comprueba la instalación con `git --version`.

### 1.3. Instalar VS Code (opcional)

Si quieres usar el Camino A, descarga Visual Studio Code desde:

https://code.visualstudio.com/download

Si prefieres el Camino B, puedes continuar sin instalarlo.

---

## 2. Obtener el proyecto

### Camino A — VS Code

1. Abre VS Code.
2. Abre la paleta de comandos con `Ctrl+Shift+P` en Windows o `Cmd+Shift+P` en macOS.
3. Busca `Git: Clone`.
4. Introduce la URL del repositorio:

   `https://github.com/Sadzc/Proyecto_skillnest.git`

5. Selecciona una carpeta de destino.
6. Cuando VS Code pregunte si quieres abrir el repositorio clonado, selecciona **Open**.

### Camino B — Terminal

Abre la terminal que corresponda a tu sistema operativo.

**Windows — PowerShell:**

```powershell
git clone https://github.com/Sadzc/Proyecto_skillnest.git
cd Proyecto_skillnest
```

**Windows — CMD (Símbolo del sistema):**

```cmd
git clone https://github.com/Sadzc/Proyecto_skillnest.git
cd Proyecto_skillnest
```

**macOS / Linux / WSL — Terminal:**

```bash
git clone https://github.com/Sadzc/Proyecto_skillnest.git
cd Proyecto_skillnest
```

Si el repositorio es privado, necesitarás los permisos y la autenticación correspondientes.

### 2.1. Verificar que el proyecto se descargó correctamente

En cualquiera de las terminales:

```bash
git status
```

Si el repositorio está limpio, deberías ver un mensaje parecido a:

```text
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

Comprueba también que existen los archivos principales.

**Windows — PowerShell:**

```powershell
Get-ChildItem
```

**Windows — CMD (Símbolo del sistema):**

```cmd
dir
```

**macOS / Linux / WSL — Terminal:**

```bash
ls -la
```

Debes encontrar, entre otros, `README.md`, `requirements.txt` y `.env.example`.

---

## 3. Estructura del repositorio

La estructura de referencia es:

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

La carpeta `docs/resultados/` puede aparecer después de ejecutar la comparativa, ya que se genera durante su ejecución.

### Función de los archivos principales

- `app.py`: script principal de la aplicación.
- `src/consumir_gemini.py`: consulta individual a Gemini, manejo de errores y cálculo de costo.
- `src/consumir_gemini costos_latencia.py`: comparativa de modelos y medición de latencia y costo.
- `prompts/banco.py`: banco de prompts del proyecto.
- `prompts/test_consistencia.py`: prueba la consistencia de los prompts contra la API.
- `prompts/registro_resultados.json`: registro de resultados de las pruebas de consistencia.
- `docs/decision-arquitectura.md`: documenta decisiones de arquitectura y selección de modelo.
- `docs/diagrama_arquitectura.png`: diagrama de arquitectura.
- `docs/evidencia_peticion_autenticada.png`: evidencia de una petición autenticada.
- `docs/respuestas_completas.md`: informe de referencia de la comparativa.
- `docs/resultados/`: informes históricos y registros generados por la comparativa.
- `.env.example`: plantilla de configuración sin credenciales reales.
- `.env`: archivo local con la clave de API; no debe subirse a GitHub.
- `.gitignore`: reglas para excluir archivos locales y sensibles.
- `requirements.txt`: dependencias de Python.
- `venv/`: entorno virtual local; no debe subirse a GitHub.

---

## 4. Crear y activar el entorno virtual

Un entorno virtual mantiene las dependencias del proyecto separadas de las de otros proyectos.

Debes crear el entorno una sola vez. Después, tendrás que activarlo cada vez que abras una terminal nueva para trabajar en el proyecto.

Ejecuta los comandos desde la raíz del repositorio, donde se encuentra `requirements.txt`.

### Camino A — VS Code

1. Abre la carpeta del proyecto.
2. Abre la paleta de comandos con `Ctrl+Shift+P` o `Cmd+Shift+P`.
3. Selecciona `Python: Create Environment`.
4. Elige `Venv` y selecciona tu intérprete de Python.
5. Abre una terminal integrada y verifica que el entorno esté activo.

Si no aparece esa opción, instala la extensión Python de Microsoft.

### Camino B — Terminal

#### Paso 1. Crear el entorno virtual

**Windows — PowerShell:**

```powershell
python -m venv venv
```

Si `python` no se reconoce:

```powershell
py -m venv venv
```

**Windows — CMD (Símbolo del sistema):**

```cmd
python -m venv venv
```

Si `python` no se reconoce:

```cmd
py -m venv venv
```

**macOS / Linux / WSL — Terminal:**

```bash
python3 -m venv venv
```

Si el comando termina sin errores, normalmente el entorno se habrá creado.

#### Paso 2. Activar el entorno virtual

**Windows — PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la ejecución de scripts, puedes permitirla solo para la sesión actual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Después, vuelve a ejecutar:

```powershell
.\venv\Scripts\Activate.ps1
```

**Windows — CMD (Símbolo del sistema):**

```cmd
venv\Scripts\activate
```

**macOS / Linux / WSL — Terminal:**

```bash
source venv/bin/activate
```

Cuando se active correctamente, normalmente verás `(venv)` al principio de la línea de comandos.

#### ¿Qué hacer si no se encuentra la ruta?

Comprueba que estás en la raíz del repositorio y que la carpeta `venv` existe.

**PowerShell:**

```powershell
Get-ChildItem
```

**CMD:**

```cmd
dir
```

**macOS / Linux / WSL:**

```bash
ls -la
```

Si `venv` no aparece, vuelve a ejecutar el comando de creación desde la raíz correcta. Si creaste el entorno en otra carpeta, debes entrar en la carpeta adecuada o crear el entorno en la ubicación del proyecto.

#### Salir del entorno virtual

Cuando termines de trabajar:

```bash
deactivate
```

Este comando funciona en las terminales habituales. La próxima vez que abras una terminal, vuelve a activar el entorno.

---

## 5. Instalar dependencias

Con el entorno virtual activado y desde la raíz del repositorio, instala las dependencias definidas en `requirements.txt`.

**Windows — PowerShell:**

```powershell
pip install -r requirements.txt
```

**Windows — CMD (Símbolo del sistema):**

```cmd
pip install -r requirements.txt
```

**macOS / Linux / WSL — Terminal:**

```bash
pip install -r requirements.txt
```

Si `pip` no se reconoce, puedes utilizar el módulo de Python correspondiente:

**Windows:**

```powershell
python -m pip install -r requirements.txt
```

**macOS / Linux / WSL:**

```bash
python3 -m pip install -r requirements.txt
```

Para comprobar los paquetes instalados:

```bash
pip list
```

Deberías ver las dependencias que utiliza el proyecto, como `requests` y `python-dotenv`.

---

## 6. Configurar las variables de entorno

El proyecto necesita una clave de API de Gemini para realizar consultas. Esta clave se almacena en un archivo llamado `.env`.

**Importante:** `.env.example` es solo una plantilla. No contiene tu clave personal. Debes crear una copia llamada `.env` y colocar allí tu propia clave.

Esta sección se puede completar totalmente desde terminal. No necesitas VS Code.

### 6.1. Crear el archivo `.env`

Primero, confirma que estás en la raíz del repositorio y que existe `.env.example`.

**Windows — PowerShell:**

```powershell
Copy-Item .env.example .env
```

**Windows — CMD (Símbolo del sistema):**

```cmd
copy .env.example .env
```

**macOS / Linux / WSL — Terminal:**

```bash
cp .env.example .env
```

Estos comandos crean una copia llamada `.env` en la carpeta actual.

Si el archivo `.env` ya existe y contiene una clave válida, no lo sobrescribas. Conserva el archivo existente.

### 6.2. Abrir y editar `.env` sin usar VS Code

Una vez creado el archivo, debes abrirlo con un editor de texto y reemplazar el valor de ejemplo por tu clave de Gemini.

**Windows — PowerShell:**

```powershell
notepad .env
```

**Windows — CMD (Símbolo del sistema):**

```cmd
notepad .env
```

Se abrirá el Bloc de notas con el archivo `.env`. Si Windows pregunta si quieres crearlo porque no existe, vuelve al paso anterior y confirma que lo creaste correctamente.

**macOS — Terminal:**

```bash
open -e .env
```

**Linux / WSL — Terminal:**

Si tienes instalado el editor de terminal `nano`:

```bash
nano .env
```

En `nano`, guarda con `Ctrl+O`, confirma con Enter y sal con `Ctrl+X`.

También puedes usar VS Code si ya lo tienes instalado, pero no es obligatorio.

### 6.3. Colocar la clave de API

Dentro del archivo `.env`, debes tener una línea con este formato:

```dotenv
GEMINI_API_KEY=TU_CLAVE_REAL
```

Reemplaza `TU_CLAVE_REAL` por tu propia clave obtenida desde:

https://aistudio.google.com/apikey

Por ejemplo, el archivo debe contener una asignación con el nombre exacto `GEMINI_API_KEY`. No agregues la clave directamente al código Python ni la compartas en capturas, mensajes o repositorios públicos.

Guarda los cambios y cierra el editor.

### 6.4. Verificar que el archivo existe

**Windows — PowerShell:**

```powershell
Test-Path .env
```

**Windows — CMD (Símbolo del sistema):**

```cmd
dir .env
```

**macOS / Linux / WSL — Terminal:**

```bash
ls -la .env
```

### 6.5. Verificar que Git ignora el archivo

Este paso ayuda a evitar que la clave se publique accidentalmente.

**Windows — PowerShell:**

```powershell
git check-ignore -v .env
```

**Windows — CMD (Símbolo del sistema):**

```cmd
git check-ignore -v .env
```

**macOS / Linux / WSL — Terminal:**

```bash
git check-ignore -v .env
```

Si Git muestra una regla de `.gitignore` que excluye `.env`, está siendo ignorado por esa regla.

Si no muestra ninguna salida, revisa `.gitignore` y asegúrate de que incluya:

```gitignore
.env
venv/
__pycache__/
```

Si `.env` ya estaba versionado anteriormente, agregarlo a `.gitignore` no lo elimina del historial ni deja de versionarlo automáticamente. En ese caso, debes comprobar el estado del repositorio antes de publicar cambios.

**Nunca subas la clave de API a GitHub.** Si una clave real se ha publicado o compartido por error, revócala y genera una nueva.

---

## 7. Ejecutar los scripts

Antes de ejecutar un script, confirma que:

- Estás en la raíz del repositorio.
- El entorno virtual está activado.
- El archivo `.env` existe y contiene tu clave.
- Las dependencias están instaladas.

Los comandos siguientes se ejecutan desde la raíz del proyecto.

### 7.1. Script principal: `app.py`

**Windows — PowerShell:**

```powershell
python app.py
```

**Windows — CMD (Símbolo del sistema):**

```cmd
python app.py
```

**macOS / Linux / WSL — Terminal:**

```bash
python3 app.py
```

El resultado exacto depende de la implementación de `app.py`. Si el script realiza una petición correcta, debería mostrar la respuesta de Gemini y la información que haya programado para imprimir.

El manejo de errores y los reintentos dependen del código real de este archivo.

### 7.2. Módulo de consumo de Gemini

Archivo: `src/consumir_gemini.py`.

**Windows — PowerShell:**

```powershell
python src/consumir_gemini.py
```

**Windows — CMD (Símbolo del sistema):**

```cmd
python src\consumir_gemini.py
```

**macOS / Linux / WSL — Terminal:**

```bash
python3 src/consumir_gemini.py
```

La salida esperada incluye el costo estimado de la petición y el texto generado, por ejemplo:

```text
Costo de la petición: $0.00xxxx USD
[texto generado por el modelo]
```

Este script maneja errores de conexión, tiempo de espera y respuestas HTTP. No implementa reintentos automáticos en la versión documentada aquí.

### 7.3. Comparativa de modelos, latencia y costo

Archivo: `src/consumir_gemini costos_latencia.py`.

**Windows — PowerShell:**

```powershell
python "src/consumir_gemini costos_latencia.py"
```

**Windows — CMD (Símbolo del sistema):**

```cmd
python "src/consumir_gemini costos_latencia.py"
```

**macOS / Linux / WSL — Terminal:**

```bash
python3 "src/consumir_gemini costos_latencia.py"
```

Las comillas son necesarias porque el nombre del archivo contiene espacios.

Este script compara los modelos configurados y registra métricas de latencia y costo. Puede tardar más si hay errores o reintentos.

Los nombres de modelos y las tarifas configuradas deben verificarse frente a la disponibilidad y los precios vigentes del proveedor. El costo mostrado es una estimación basada en esos valores.

### 7.4. Test de consistencia de prompts

Archivo: `prompts/test_consistencia.py`.

**Windows — PowerShell:**

```powershell
python prompts/test_consistencia.py
```

**Windows — CMD (Símbolo del sistema):**

```cmd
python prompts\test_consistencia.py
```

**macOS / Linux / WSL — Terminal:**

```bash
python3 prompts/test_consistencia.py
```

El resultado depende de los prompts configurados, las respuestas de Gemini y la disponibilidad de la API. Los errores de servicio no significan necesariamente que el código esté roto.

---

## 8. Resultados de la comparativa

La comparativa puede generar informes y registros dentro de `docs/resultados/`, según la versión del script.

En la configuración documentada del proyecto se utilizan:

- `docs/respuestas_completas.md`: informe de referencia o último informe, según la implementación actual.
- `docs/resultados/`: informes de ejecuciones.
- `docs/resultados/registro_ejecuciones.jsonl`: registro acumulativo de ejecuciones, si está habilitado en la versión utilizada.

La carpeta de resultados puede crearse automáticamente durante la ejecución.

No elimines ni sobrescribas los registros históricos si necesitas conservar trazabilidad de las pruebas.

---

## 9. Uso básico de Git

Los siguientes comandos funcionan en Windows PowerShell, Windows CMD (Símbolo del sistema), macOS, Linux y WSL, siempre que Git esté instalado y estés dentro del repositorio.

Revisar el estado:

```bash
git status
```

Ver el historial:

```bash
git log --oneline
```

Preparar un archivo específico:

```bash
git add README.md
```

Preparar todos los cambios, después de revisar el estado:

```bash
git add .
```

Crear un commit:

```bash
git commit -m "Actualiza documentación"
```

Subir cambios a la rama `main`:

```bash
git push origin main
```

Traer cambios remotos:

```bash
git pull
```

Antes de ejecutar `git add .`, revisa siempre `git status`. No subas `.env`, credenciales ni la carpeta del entorno virtual.

---

## 10. Solución de problemas

### Python no se reconoce

- Windows: prueba `py --version`.
- macOS / Linux / WSL: prueba `python3 --version`.
- En WSL, instala Python dentro de Ubuntu; la instalación de Windows es independiente.

### No se encuentra `requirements.txt`

Estás en una carpeta incorrecta. Vuelve a la raíz del repositorio.

Para listar archivos:

- PowerShell: `Get-ChildItem`
- CMD (Símbolo del sistema): `dir`
- macOS / Linux / WSL: `ls -la`

### No se puede activar el entorno virtual

Comprueba que la carpeta `venv` existe en la raíz del proyecto. Usa el comando de activación que corresponde a la terminal que estás utilizando.

### No se encuentra `GEMINI_API_KEY`

1. Comprueba que `.env` está en la raíz del repositorio.
2. Ábrelo con el editor de texto correspondiente a tu sistema.
3. Confirma que la variable se llama exactamente `GEMINI_API_KEY`.
4. Comprueba que la clave es válida, sin mostrarla ni compartirla.

### La API devuelve un error 429

Puede indicar que alcanzaste un límite de solicitudes o cuota. Revisa los límites de tu cuenta y espera antes de volver a intentarlo.

### La API devuelve un error 503

El servicio puede estar temporalmente saturado. El comportamiento ante este error depende del script: algunos implementan reintentos y otros devuelven un error.

### La API devuelve un error 401 o 403

Comprueba la clave, los permisos, el acceso al modelo y la configuración de la API. Si la clave fue expuesta, revócala y genera otra.

### El costo parece incorrecto

Verifica los nombres de modelos y las tarifas por token configuradas. El resultado depende de los precios introducidos en el código y de los datos de uso que devuelve la API.

---

## 11. Buenas prácticas

- No escribas claves de API directamente en el código.
- No publiques `.env` ni compartas su contenido.
- Activa el entorno virtual antes de ejecutar los scripts.
- Mantén `requirements.txt` actualizado.
- Conserva los resultados históricos que necesites para comparar ejecuciones.
- Revisa `git status` antes de `git add` y `git push`.
- Comprueba que el modelo y las tarifas configuradas corresponden a la API utilizada.
- Mantén la documentación alineada con el comportamiento real de los scripts.

---

## 12. Flujo de trabajo resumido

1. Instala Python y Git.
2. Clona el repositorio.
3. Abre una terminal en la raíz del proyecto.
4. Crea el entorno virtual.
5. Activa el entorno virtual.
6. Instala las dependencias desde `requirements.txt`.
7. Crea `.env` a partir de `.env.example`.
8. Abre `.env` con un editor de texto, agrega tu clave y guarda el archivo.
9. Comprueba que `.env` está excluido de Git.
10. Ejecuta el script que necesites.
11. Revisa los resultados generados.
12. Comprueba `git status`, crea un commit y publica los cambios si corresponde.

**Puedes completar todo este flujo usando únicamente terminal. VS Code es opcional.**
