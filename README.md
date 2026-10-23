# Asistente de Documentación de Data Warehouse

Este repositorio contiene el desarrollo de un asistente inteligente para consultar la documentación de un data warehouse mediante modelos de lenguaje y técnicas de RAG (Retrieval-Augmented Generation). El proyecto forma parte de la Especialización en Desarrollo con IA Generativa de Skillnest y Accenture.

La solución busca responder preguntas sobre columnas, modelos y métricas de negocio utilizando documentación como archivos `schema.yml`, descripciones de modelos dbt y definiciones de KPIs, citando las fuentes utilizadas e identificando posibles brechas de documentación.

Esta guía explica cómo preparar el entorno, instalar las dependencias, configurar las credenciales, ejecutar los scripts y registrar los cambios.

## 1. Herramientas necesarias

- **Python 3:** ejecuta el código del proyecto.
- **pip:** instala paquetes de Python.
- **Git:** registra cambios y permite trabajar con el repositorio.
- **Cuenta y repositorio de GitHub:** necesarios si vas a clonar o publicar el proyecto.
- **Terminal:** permite ejecutar comandos. Visual Studio Code es opcional; puedes trabajar sin él.
- **Clave de API de Gemini:** necesaria para los scripts que consultan Gemini.

### 1.1 Instalar Python

Descarga Python desde https://www.python.org/downloads/ y sigue las instrucciones para tu sistema operativo.

**Windows (PowerShell, CMD o Git Bash):** comprueba la instalación con:

```powershell
python --version
```

Si `python` no se reconoce, prueba:

```powershell
py --version
```

**macOS, Linux, Ubuntu y WSL:** en macOS puedes usar el instalador oficial de Python. En Ubuntu/WSL instala Python y las herramientas de entornos virtuales así:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

Comprueba la instalación:

```bash
python3 --version
python3 -m pip --version
```

> WSL es un entorno Linux dentro de Windows. Instalar Python en Windows no lo instala automáticamente dentro de Ubuntu/WSL.

### 1.2 Instalar Git

Git permite clonar el repositorio desde GitHub y registrar los cambios del proyecto. Si ya está instalado, puedes omitir este paso.

**Windows**

1. Descarga Git desde la [página oficial](https://git-scm.com/install/).
2. Ejecuta el instalador y mantén las opciones predeterminadas si no sabes cuáles elegir.
3. Abre PowerShell, Git Bash o la terminal de VS Code y verifica la instalación:

```bash
git --version
```

Como alternativa, puedes instalar Git desde PowerShell si tienes `winget` disponible:

```powershell
winget install --id Git.Git -e
```

**Ubuntu / WSL**

```bash
sudo apt update
sudo apt install git
git --version
```

**macOS**

Abre la terminal y ejecuta:

```bash
xcode-select --install
git --version
```

Si aparece un número de versión, Git está disponible. Si acabas de instalarlo y no se reconoce el comando, abre una terminal nueva y vuelve a intentarlo.

**Siguiente paso:** continúa con la clonación del repositorio desde GitHub.

### 1.3 Editor opcional

Puedes instalar Visual Studio Code desde https://code.visualstudio.com/download. No es obligatorio: los comandos también se pueden ejecutar desde una terminal independiente. Si usas WSL, puedes instalar VS Code en Windows y la extensión WSL.

## 2. Obtener el proyecto

Puedes descargar y descomprimir el repositorio desde la plataforma del curso, o clonarlo desde GitHub. Para clonar, copia la URL real desde el botón **Code** del repositorio y ejecuta en cualquier terminal:

```bash
git clone URL_DEL_REPOSITORIO
cd asistente_documentacion_data_warehouse
```

Reemplaza `URL_DEL_REPOSITORIO` por la URL real. Si descargaste un ZIP, abre una terminal dentro de la carpeta descomprimida y continúa desde allí.

Comprueba que estás en la raíz del proyecto (donde están `requirements.txt` y `README.md`):

```bash
git status
```

## 3. Estructura del repositorio

```text
plantilla-repositorio-base/
asistente_documentacion_data_warehouse/
├── docs/
│   ├── decision-arquitectura.md
│   ├── diagrama_arquitectura.png
│   ├── evidencia_peticion_autenticada.png
│   ├── respuestas_completas.md
│   └── resultados/
│       ├── respuestas_ID.md
│       └── registro_ejecuciones.jsonl
├── prompts/
├── src/
├── tests/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── app.py
```

- `src/`: scripts principales del proyecto.
- `prompts/`: banco de prompts y archivos relacionados con pruebas y registro de resultados.
- `tests/`: espacio para pruebas automatizadas.
- `docs/`: documentación, diagramas, evidencias e informes.
- `docs/respuestas_completas.md`: informe más reciente de la comparativa de modelos.
- `docs/resultados/`: historial de informes por ejecución y registro estructurado acumulativo; se crea automáticamente.
- `prompts/registro_resultados.json`: archivo existente del proyecto; su estructura y finalidad deben mantenerse según el código que lo utiliza.
- `requirements.txt`: dependencias Python necesarias para reconstruir el entorno.
- `.env`: variables privadas como la clave de API. No se versiona.
- `.gitignore`: reglas para excluir archivos locales y sensibles.
- `venv/`: entorno virtual local creado durante la instalación; no debe subirse a GitHub.
- `__pycache__/`: caché generada por Python; no necesita versionarse.
- `app.py`: archivo Python en la raíz; su función concreta depende de su implementación.

## 4. Crear y activar el entorno virtual

Un entorno virtual mantiene las dependencias del proyecto separadas de las de otros proyectos. Ejecuta el comando de creación desde la raíz del repositorio.

**Windows (PowerShell, CMD o Git Bash):**

```bash
python -m venv venv
```

Si `python` no está disponible en Windows, prueba:

```powershell
py -m venv venv
```

**macOS, Linux, Ubuntu y WSL:**

```bash
python3 -m venv venv
```

Activa el entorno con el comando correspondiente a tu terminal:

**Windows — PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación, puedes permitir scripts solo en la sesión actual y volver a activar:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Respeta las políticas de seguridad de tu equipo; no cambies políticas administradas sin autorización.

**Windows — CMD:**

```bat
venv\Scripts\activate.bat
```

**Windows — Git Bash:**

```bash
source venv/Scripts/activate
```

**macOS, Linux, Ubuntu y WSL:**

```bash
source venv/bin/activate
```

Si la activación funcionó, normalmente verás `(venv)` al inicio de la línea de comandos. Para salir del entorno, usa el mismo comando en todas las terminales:

```bash
deactivate
```

## 5. Instalar dependencias

Con el entorno virtual activado y desde la raíz del repositorio, instala las librerías registradas en `requirements.txt`:

```bash
python -m pip install -r requirements.txt
```

En macOS/Linux/WSL, si el comando `python` no existe, usa:

```bash
python3 -m pip install -r requirements.txt
```

No hace falta instalar manualmente cada librería que ya figure en `requirements.txt`. Para revisar los paquetes instalados:

```bash
python -m pip list
```

Para comprobar algunas importaciones utilizadas por el proyecto:

```bash
python -c "import requests; import dotenv; print('Dependencias OK')"
```

Si instalas una nueva dependencia, hazlo con el entorno activado y actualiza `requirements.txt` de forma consciente. Este comando reemplaza el archivo completo por todos los paquetes instalados en el entorno, así que úsalo solo después de revisar lo que contiene:

```bash
python -m pip freeze > requirements.txt
```

## 6. Configurar las variables de entorno

El proyecto utiliza una clave de API de Gemini para realizar consultas. La clave se almacena en un archivo `.env`, que contiene información privada y no debe subirse a GitHub.

### 6.1. Crear el archivo `.env`

En la raíz del proyecto, copia el archivo de ejemplo.

**Ubuntu, Linux, macOS y WSL:**

```bash
cp .env.example .env
```

**Windows PowerShell:**

```powershell
Copy-Item .env.example .env
```

**Windows CMD:**

```cmd
copy .env.example .env
```

Si ya tienes un archivo `.env` configurado con tu clave real, consérvalo y no lo sobrescribas.

### 6.2. Configurar la clave

Abre el archivo `.env` y reemplaza el valor de ejemplo por tu clave real:

```dotenv
GEMINI_API_KEY=TU_CLAVE_REAL
```

El nombre de la variable debe coincidir exactamente con el que utiliza el código.

### 6.3. Proteger las credenciales

El archivo `.env` debe estar excluido de Git. Comprueba que `.gitignore` contenga:

```gitignore
.env
```

El archivo `.env.example` sí debe subirse al repositorio porque contiene únicamente un valor de ejemplo.

Verifica que Git ignore tu archivo privado:

```bash
git check-ignore -v .env
```

Si la clave real se publicó anteriormente en GitHub, debes revocarla o reemplazarla y revisar el historial del repositorio. Agregar `.env` a `.gitignore` no elimina los secretos de commits anteriores.

Si el archivo ya se subió a Git en un commit anterior, agregarlo a `.gitignore` no borra ese historial. Si una clave quedó expuesta, revócala o genera otra desde el proveedor y revisa el historial del repositorio.

## 7. Ejecutar los scripts

Antes de ejecutar, confirma que estás en la raíz del repositorio, que el entorno virtual está activado, que instalaste las dependencias y que `.env` contiene la clave requerida.

Ejecutar el script de consumo de Gemini:

```bash
python src/consumir_gemini.py
```

Ejecutar la comparativa de modelos, costos y latencia:

```bash
python "src/consumir_gemini costos_latencia.py"
```

Las comillas son necesarias porque el nombre del archivo contiene espacios. En macOS/Linux/WSL puedes usar `python3` en lugar de `python` si ese es el comando de tu instalación.

Ejecutar el script de consistencia de prompts:

```bash
python prompts/test_consistencia.py
```

Que el archivo se llame `test_consistencia.py` no garantiza por sí solo que use `pytest`; este comando simplemente ejecuta el archivo Python.

## 8. Resultados de la comparativa: historial y registros

La comparativa guarda los resultados de cada ejecución para facilitar su revisión posterior.

- `docs/resultados/respuestas_ID.md`: contiene las respuestas y métricas de una ejecución específica. El identificador permite conservar ejecuciones anteriores.
- `docs/resultados/registro_ejecuciones.jsonl`: registro acumulativo que añade una línea JSON por cada pregunta procesada, tanto si termina correctamente como si falla.

La carpeta `docs/resultados/` se crea automáticamente al ejecutar la comparativa. El registro JSONL conserva los resultados de ejecuciones anteriores, por lo que no se debe reemplazar si se quiere mantener el historial.

El costo calculado depende de los precios por token configurados en el script. Verifica que los nombres de modelos y los precios correspondan a los modelos disponibles y a las tarifas vigentes del proveedor antes de interpretar los costos como definitivos.

## 9. Uso básico de Git

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

Preparar todos los cambios después de revisar `git status`:

```bash
git add .
```

Crear un commit:

```bash
git commit -m "Actualiza documentación y registro de resultados"
```

Subir la rama `main` al remoto `origin`, si están configurados:

```bash
git push origin main
```

Actualizar tu rama con los cambios remotos:

```bash
git pull
```

No subas `.env`, entornos virtuales ni credenciales. Revisa siempre `git status` antes de preparar cambios.

## 10. Solución de problemas

### Python no se reconoce

En Windows prueba `py --version`; en macOS/Linux/WSL prueba `python3 --version`. Si usas WSL, instala Python dentro de Ubuntu, no solo en Windows.

### No se encuentra `requirements.txt`

Asegúrate de ejecutar los comandos desde la raíz del repositorio. Para listar archivos:

- PowerShell: `Get-ChildItem`
- CMD: `dir`
- Git Bash/macOS/Linux/WSL: `ls -la`

### No se activa el entorno virtual

Verifica que exista la carpeta `venv/` y usa el comando de activación que corresponda a tu terminal.

### No se encuentra `GEMINI_API_KEY`

Confirma que `.env` está en la raíz y que el nombre de variable coincide exactamente con el leído por el script. No compartas el valor de la clave para diagnosticar el error.

### La API devuelve un error

Comprueba la validez de la clave, el acceso al modelo, la conectividad, los límites de uso y los nombres de modelos configurados. Un error 429 normalmente indica límites de solicitudes o cuota; respeta los límites y las políticas del proveedor.

## 11. Buenas prácticas

- Nunca escribas claves de API directamente en el código ni las publiques en GitHub.
- Usa un entorno virtual independiente para este proyecto.
- Mantén `requirements.txt` actualizado y revisado.
- Conserva los resultados históricos para permitir trazabilidad y comparación.
- Revisa `git status` antes de hacer `git add` o `git push`.
- Documenta cambios relevantes en `docs/` y mantén los scripts organizados.
- Distingue entre el informe más reciente y los registros históricos acumulativos.

## 12. Flujo de trabajo resumido

1. Instala Python y Git.
2. Clona o descomprime el repositorio.
3. Abre una terminal en la raíz del proyecto.
4. Crea y activa `venv`.
5. Instala dependencias desde `requirements.txt`.
6. Comprueba el archivo `.env` sin compartir sus credenciales.
7. Ejecuta el script necesario.
8. Revisa los informes y registros generados.
9. Comprueba `git status`, prepara los cambios, crea un commit y súbelo si corresponde.
