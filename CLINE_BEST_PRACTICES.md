# Mejores Prácticas para Cline - Mi Configuración

## Distribución de Uso por Provider

### Gemini CLI (GRATIS - 1000 requests/día)
- Generación de código boilerplate
- Refactoring simple
- Análisis de archivos pequeños
- Documentación básica
- Tareas repetitivas
- Primera opción para todo

### Claude Sonnet 4 (Plan Max)
- Debugging medio
- Generación de features completas
- Code reviews
- Refactoring moderado

### Claude Opus 4 (Plan Max)
- Arquitectura de sistemas
- Debugging ultra complejo
- Decisiones críticas
- Refactoring mayor

### Gemini 2.5 Pro (Google Pro)
- Análisis de proyectos completos (1M tokens)
- Generación desde imágenes/PDFs
- Tareas con WebFetch
- Procesamiento masivo

## Horario Optimizado
- 9:00-14:00: Usar Gemini CLI (500 requests)
- 14:00-18:00: Usar Claude Sonnet 4
- 18:00-22:00: Usar Gemini CLI (500 requests)
- 22:00-9:00: Usar Gemini 2.5 Pro

## Comandos Rápidos
- `/mcp` - Ver estado de servidores MCP
- `/workflow` - Ejecutar workflows
- `Ctrl+Shift+1-4` - Cambiar providers
- `Ctrl+Shift+W` - Ejecutar workflow

## Recordatorios
1. Siempre empezar con Gemini CLI
2. Escalar a Claude solo si es necesario
3. Usar workflows para tareas repetitivas
4. Monitorear uso diario
5. WebFetch disponible en Claude 4 y Gemini 2.5
