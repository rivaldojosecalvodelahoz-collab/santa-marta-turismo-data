# Santa Marta Turismo Data

Proyecto académico para la asignatura de Ingeniería de Datos.

## Objetivo

Desarrollar un sistema de información web que permita consultar lugares turísticos de Santa Marta, registrar visitas y transformar los datos almacenados en reportes estadísticos.

## Tecnologías

- Python
- Flask
- SQLite
- HTML
- CSS
- Visual Studio Code

Los reportes visuales funcionan sin depender de librerías JavaScript externas, por lo que la aplicación puede demostrarse aun cuando no haya conexión a Internet.

## Vistas

1. Inicio.
2. Lugares turísticos.
3. Detalle del lugar.
4. Registro de visitas.
5. Panel de estadísticas.
6. Administración de lugares.
7. Formulario de creación y edición.

## Reportes estadísticos

- Visitantes por lugar.
- Visitantes por categoría.
- Visitantes por mes.
- Promedio de calificación por lugar.
- Indicadores generales de visitantes, registros y calificación promedio.

## Base de datos

Tablas principales:

- `categorias`
- `lugares`
- `visitas`

Relaciones:

- Una categoría puede contener varios lugares.
- Un lugar puede tener múltiples visitas.

## Ejecución rápida en Windows

1. Descomprimir el proyecto.
2. Hacer doble clic en `INICIAR_PROYECTO.bat`.
3. Esperar a que aparezca:
   `Running on http://127.0.0.1:5000`
4. Abrir en el navegador:
   `http://127.0.0.1:5000`

## Ejecución manual

```powershell
python -m venv venv
.\venv\Scripts\activate
python -m pip install -r requirements.txt
python app.py
```

Si PowerShell bloquea la activación:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

## Importante para la entrega

No es necesario entregar la carpeta `venv`. El archivo `requirements.txt` permite volver a instalar Flask.

## Publicación

El proyecto incluye `render.yaml` y `requirements-deploy.txt`, por lo que queda preparado para alojarse en Render. Después de publicarlo, se debe reemplazar la URL pendiente del documento de entrega por la URL pública generada por el servicio.
