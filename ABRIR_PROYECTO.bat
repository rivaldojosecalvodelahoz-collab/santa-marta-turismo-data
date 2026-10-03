@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ==============================================
echo   TECHMOPAU - SANTA MARTA TURISMO DATA
echo ==============================================
echo.
where py >nul 2>nul
if %errorlevel%==0 (
  set PYCMD=py
) else (
  set PYCMD=python
)
if not exist venv\Scripts\python.exe (
  echo [1/3] Creando entorno virtual...
  %PYCMD% -m venv venv
)
echo [2/3] Instalando dependencias...
venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo ERROR: no fue posible instalar las dependencias.
  pause
  exit /b 1
)
echo [3/3] Iniciando aplicacion...
echo.
echo Abre en tu navegador: http://127.0.0.1:5000
echo Para detener el servidor presiona CTRL+C.
echo.
start "" http://127.0.0.1:5000
venv\Scripts\python.exe techmopau.py
pause
