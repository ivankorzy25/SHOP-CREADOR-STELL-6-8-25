@echo off
cls
echo ================================================
echo    GENERADOR PREMIUM HTML - Version 2.0
echo ================================================
echo.
echo Iniciando generador premium...
echo.

REM Verificar/instalar dependencias
pip install streamlit google-generativeai pillow pypdf2 -q

REM Limpiar cache de Streamlit
rd /s /q "%USERPROFILE%\.streamlit\cache" 2>nul

REM Iniciar aplicación
streamlit run generador_premium.py --theme.primaryColor="#ff6600"

pause
