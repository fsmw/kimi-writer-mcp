# Kimi Writer MCP Server

An MCP (Model Context Protocol) server that exposes Kimi Writer's creative writing capabilities so other AI models can access them.

## What is an MCP Server?

The **Model Context Protocol (MCP)** allows AI models to interact safely and structured with external tools and resources. This MCP server exposes Kimi Writer's writing tools so any MCP client can use them.

## Features

### 🔧 Available Tools

1. **create_project** - Creates organized writing projects
2. **write_file** - Writes content to markdown files with three modes:
   - `create`: Creates new file (fails if exists)
   - `append`: Adds content to the end
   - `overwrite`: Replaces all content
3. **get_project_info** - Gets information about the active project
4. **list_project_files** - Lists all project files
5. **read_file** - Reads file contents
6. **get_file_stats** - Gets file statistics
7. **create_writing_template** - Creates templates for different writing types:
   - `novel` - Novel structure
   - `short_story` - Short story
   - `book` - Non-fiction book
   - `poetry` - Poetry collection

### 📝 Structured Prompts

1. **write_novel** - Generates complete prompts for novels
2. **write_short_story** - Creates prompts for short stories
3. **write_nonfiction_book** - Designed for educational/technical books

### 📚 Document Generation

1. **generate_pdf** - Converts markdown project to professional PDF document
2. **generate_epub** - Creates standards-compliant EPUB ebook

## Instalación

### 1. Install Dependencies

```bash
# Install MCP dependencies
pip install -r requirements.txt

# Install Kimi Writer dependencies (from parent directory)
cd ../kimi-writer
pip install -r requirements.txt
cd ../kimi-writer-mcp

# For PDF/EPUB generation (optional)
pip install -r requirements-extended.txt
```

### 2. Configurar Entorno

Asegúrate de que tu archivo `.env` en el directorio `../kimi-writer/` esté configurado:

```bash
# ../kimi-writer/.env
MOONSHOT_API_KEY=tu-api-key-aqui
MOONSHOT_BASE_URL=http://localhost:11434/v1
```

## Uso

### Ejecutar el Servidor MCP

```bash
python mcp-server.py
```

El servidor esperará conexiones MCP via stdio.

### Test Clients

To test all capabilities:

```bash
# Basic functionality test
python test-client.py

# Test PDF and EPUB generation (requires extended dependencies)
python test-documents.py
```

These execute comprehensive test suites demonstrating:
- Project creation and management
- File writing and reading
- Template generation
- Structured prompts
- Document export (PDF/EPUB)
- Error handling

## Integración con Otros Clientes

### Claude Desktop

Para usar en Claude Desktop, agrega a tu configuración:

```json
{
  "mcpServers": {
    "kimi-writer": {
      "command": "python",
      "args": ["/ruta/completa/a/kimi-writer-mcp/mcp-server.py"],
      "cwd": "/ruta/completa/a/kimi-writer-mcp"
    }
  }
}
```

### Cliente MCP Personalizado

```python
import asyncio
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

async def usar_kimi_writer_mcp():
    server_params = StdioServerParameters(
        command="python",
        args=["mcp-server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Crear proyecto
            await session.call_tool("create_project", {
                "project_name": "mi_novela"
            })
            
            # Escribir contenido
            await session.call_tool("write_file", {
                "filename": "capitulo_01.md",
                "content": "# Mi Novela\n\nEra una vez...",
                "mode": "create"
            })
            
            print("¡Proyecto creado exitosamente!")

asyncio.run(usar_kimi_writer_mcp())
```

## Arquitectura

### Estructura del Proyecto

```
kimi-writer-mcp/
├── mcp-server.py          # Servidor MCP principal
├── test-client.py         # Cliente de prueba completo
├── requirements.txt       # Dependencias MCP
└── README.md             # Este archivo

../kimi-writer/           # Directorio padre con Kimi Writer
├── kimi-writer.py        # Aplicación principal
├── tools/                # Herramientas de escritura
├── utils.py              # Utilidades
└── requirements.txt      # Dependencias de Kimi Writer
```

### Flujo de Operación

1. **Cliente se conecta** via stdio al servidor MCP
2. **Lista herramientas disponibles** usando `list_tools()`
3. **Obtiene prompts** con `list_prompts()` y `get_prompt()`
4. **Ejecuta herramientas** usando `call_tool()`
5. **Recibe resultados** estructurados para usar en su contexto

### Manejo de Estado

- **Proyecto Activo**: Se mantiene globalmente durante la sesión
- **Directorio de Salida**: `output/` relativo al directorio del servidor
- **Gestión de Archivos**: Todos los archivos se crean en el proyecto activo

## Usage Examples

### Writing a Novel with PDF Export

```python
# 1. Create project
await session.call_tool("create_project", {
    "project_name": "cyberpunk_mystery"
})

# 2. Get structured prompt
prompt = await session.get_prompt("write_novel", {
    "theme": "a detective in a cyberpunk city",
    "genre": "mystery",
    "chapters": "10",
    "length": "medium"
})

# 3. Write content using your model
await session.call_tool("write_file", {
    "filename": "chapter_01.md",
    "content": "content_generated_by_your_model",
    "mode": "create"
})

# 4. Generate PDF when complete
pdf_result = await session.call_tool("generate_pdf", {
    "output_filename": "complete_novel"
})
```

### Creating Short Story with EPUB Export

```python
# 1. Use predefined template
await session.call_tool("create_writing_template", {
    "template_type": "short_story",
    "title": "The Last Human"
})

# 2. Write your story content
await session.call_tool("write_file", {
    "filename": "the_last_human.md",
    "content": "Your short story content here...",
    "mode": "overwrite"
})

# 3. Generate EPUB ebook
epub_result = await session.call_tool("generate_epub", {
    "title": "The Last Human - A Short Story",
    "author": "Your Name",
    "output_filename": "short_story_collection"
})
```

### Batch Document Generation

```python
# Create multiple projects and export all as documents
projects = ["novel_1", "short_story_collection", "poetry_book"]

for project_name in projects:
    # Create project and content...
    
    # Generate both PDF and EPUB
    await session.call_tool("generate_pdf", {})
    await session.call_tool("generate_epub", {
        "title": f"{project_name.replace('_', ' ').title()}"
    })
```

## Depuración

### Logs del Servidor

El servidor MCP muestra información útil:
- ✅ Conexiones establecidas
- 📁 Proyectos creados
- 📝 Archivos escritos
- 🔧 Herramientas ejecutadas

### Cliente de Prueba

Ejecuta `test-client.py` para verificar:
- Todas las herramientas funcionan
- El manejo de errores es correcto
- Los prompts se generan correctamente

### Problemas Comunes

**Error de importación Kimi Writer:**
- Verifica que el path `../kimi-writer` existe
- Asegúrate de que las dependencias estén instaladas

**Proyecto no encontrado:**
- El proyecto debe crearse antes de escribir archivos
- Verifica que el directorio de salida tenga permisos de escritura

## Desarrollo

### Agregar Nuevas Herramientas

1. Define la herramienta en `handle_list_tools()`
2. Implementa la lógica en `handle_call_tool()`
3. Agrega validación y manejo de errores

### Extender Prompts

1. Agrega el prompt en `handle_list_prompts()`
2. Implementa la generación en `handle_get_prompt()`
3. Incluye guías específicas por género/tono/audiencia

## Contribuciones

Para contribuir al servidor MCP:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Implementa los cambios con pruebas
4. Ejecuta `test-client.py` para verificar funcionalidad
5. Envía un pull request

## Licencia

Este servidor MCP hereda la licencia de Kimi Writer (MIT).

## Soporte

Para reportar problemas o solicitar features:

1. Ejecuta `test-client.py` para obtener información de diagnóstico
2. Verifica que todas las dependencias estén instaladas
3. Consulta la documentación de MCP para problemas de protocolo

---

**¡El servidor MCP de Kimi Writer te permite integrar capacidades de escritura creativa en cualquier flujo de trabajo basado en MCP!**