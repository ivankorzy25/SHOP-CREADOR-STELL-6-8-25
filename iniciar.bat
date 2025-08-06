@echo off
echo ====================================
echo   GENERADOR DE DESCRIPCIONES v1.0
echo ====================================
echo.
echo Iniciando aplicacion...
echo.

REM Instalar dependencias si no existen
pip install streamlit google-generativeai pillow pypdf2 -q

REM Iniciar la aplicación
streamlit run generador_simple.py

pause
