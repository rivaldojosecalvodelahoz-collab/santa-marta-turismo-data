# Techmopau Turismo Data

Proyecto de curso de Ingeniería de Datos orientado al turismo en Santa Marta.

## Qué incluye

- Python + Flask.
- Base de datos SQLite creada automáticamente.
- 6 vistas principales: Inicio, Lugares, Registrar visita, Estadísticas, Datos y Acerca.
- 5 reportes estadísticos como mínimo.
- Registro de nuevas visitas.
- Exportación de datos a CSV.
- Diseño responsive y sin dependencia de plantillas externas.
- Archivo principal: `techmopau.py`.
- Archivos listos para publicación en Render.

## Forma más fácil de abrirlo en Windows

1. Descomprime la carpeta.
2. Haz doble clic en `ABRIR_PROYECTO.bat`.
3. Espera a que instale las dependencias.
4. El navegador abrirá `http://127.0.0.1:5000`.

El archivo BAT no activa scripts de PowerShell, por lo que evita el problema de `Activate.ps1` bloqueado por Windows.

## Desde Visual Studio Code

Abre una terminal dentro de esta carpeta y ejecuta:

```powershell
py -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe techmopau.py
```

Luego abre `http://127.0.0.1:5000`.

## Publicación

El repositorio incluye `Procfile` y `render.yaml`. En Render el comando de inicio es:

```text
gunicorn techmopau:app
```
