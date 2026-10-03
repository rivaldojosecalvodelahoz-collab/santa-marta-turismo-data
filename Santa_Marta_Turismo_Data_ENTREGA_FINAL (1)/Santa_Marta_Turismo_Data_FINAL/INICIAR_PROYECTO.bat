@echo off
title Santa Marta Turismo Data
cd /d "%~dp0"

echo =====================================================
echo          SANTA MARTA TURISMO DATA
echo =====================================================
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta agregado al PATH.
    echo Instala Python y vuelve a ejecutar este archivo.
    pause
    exit /b 1
)

if not exist "venv\Scripts\python.exe" (
    echo Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo No fue posible crear el entorno virtual.
        pause
        exit /b 1
    )
)

echo Instalando/verificando dependencias...
"venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: No fue posible instalar las dependencias.
    echo Revisa tu conexion a Internet e intenta nuevamente.
    pause
    exit /b 1
)

echo.
echo Iniciando servidor...
echo.
echo Abre en el navegador: http://127.0.0.1:5000
echo Para detener el servidor presiona CTRL+C.
echo.
"venv\Scripts\python.exe" app.py

pause
