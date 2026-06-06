# Guía de Despliegue Local: Dashboard Analítico en Streamlit

Este documento detalla los pasos necesarios para inicializar y ejecutar el dashboard de análisis bibliométrico sobre la aplicación de Inteligencia Artificial en la Salud Materno-Infantil.

## 1. Requisitos Previos

Asegúrate de contar con lo siguiente antes de iniciar:

*   **Python 3.8** o superior instalado en tu sistema.
*   Los siguientes **tres archivos** ubicados exactamente en la misma carpeta (directorio raíz):
    *   `app.py` (El código fuente de la aplicación).
    *   `requirements.txt` (El manifiesto de librerías).
    *   `scopus_PA3.csv` (La base de datos extraída).

## 2. Configuración del Entorno (Recomendado)

Para evitar conflictos con otras librerías en tu computadora, es una buena práctica técnica usar un entorno virtual. Abre tu terminal o consola de comandos en la carpeta del proyecto y ejecuta:

### A. Crear el entorno virtual
```bash
python -m venv venv
```

### B. Activar el entorno virtual
*   **En Windows:**
    ```bash
    venv\Scripts\activate
    ```
*   **En macOS / Linux:**
    ```bash
    source venv/bin/activate
    ```

*(Sabrás que está activado porque aparecerá el prefijo `(venv)` al inicio de tu línea de comandos).*

## 3. Instalación de Dependencias

Con el entorno virtual activado, procede a instalar las librerías necesarias mediante el gestor de paquetes de Python:

```bash
pip install -r requirements.txt
```

## 4. Inicialización del Servidor Local

Una vez que las librerías se hayan instalado correctamente, levanta el servidor de Streamlit ejecutando el siguiente comando:

```bash
streamlit run app.py
```

## 5. Acceso a la Interfaz

El comando anterior iniciará un servidor local. Tu navegador web predeterminado debería abrirse automáticamente mostrando el dashboard.

Si el navegador no se abre de forma automática, puedes acceder a la interfaz copiando y pegando la siguiente URL en tu navegador:

```plaintext
http://localhost:8501
```

Para detener el servidor una vez que termines de evaluar el dashboard, simplemente presiona `Ctrl + C` en tu terminal.
