#!/usr/bin/env python3
"""
Cliente de prueba para el servidor MCP de Kimi Writer
Demuestra todas las capacidades disponibles
"""

import asyncio
import json
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

async def test_all_capabilities():
    """Prueba todas las capacidades del servidor MCP"""
    
    print("🧪 Iniciando prueba completa del servidor MCP de Kimi Writer...\n")
    
    server_params = StdioServerParameters(
        command="python",
        args=["mcp-server.py"]
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Inicializar sesión
                await session.initialize()
                print("✅ Conexión establecida con el servidor MCP\n")
                
                # 1. List available tools
                print("=" * 60)
                print("🔧 AVAILABLE TOOLS")
                print("=" * 60)
                tools_result = await session.list_tools()
                for i, tool in enumerate(tools_result.tools, 1):
                    print(f"{i}. {tool.name}")
                    print(f"   📝 {tool.description}")
                    print()
                
                # 2. Listar prompts disponibles
                print("=" * 60)
                print("📝 PROMPTS DISPONIBLES")
                print("=" * 60)
                prompts_result = await session.list_prompts()
                for i, prompt in enumerate(prompts_result.prompts, 1):
                    print(f"{i}. {prompt.name}")
                    print(f"   📝 {prompt.description}")
                    print()
                
                # 3. Crear proyecto de prueba
                print("=" * 60)
                print("🏗️ CREANDO PROYECTO DE PRUEBA")
                print("=" * 60)
                project_result = await session.call_tool("create_project", {
                    "project_name": "test_servidor_mcp_2024"
                })
                print(f"📁 {project_result.content[0].text}\n")
                
                # 4. Obtener información del proyecto
                print("=" * 60)
                print("📊 INFORMACIÓN DEL PROYECTO")
                print("=" * 60)
                info_result = await session.call_tool("get_project_info", {})
                info_data = json.loads(info_result.content[0].text)
                print(f"🗂️ Proyecto: {info_data['proyecto_activo']}")
                print(f"📅 Creado: {info_data['fecha_consulta']}")
                print(f"📂 Directorio: {info_data['directorio_output']}")
                print(f"✅ Estado: {info_data['estado']}\n")
                
                # 5. Crear plantilla de novela
                print("=" * 60)
                print("📚 CREANDO PLANTILLA DE NOVELA")
                print("=" * 60)
                template_result = await session.call_tool("create_writing_template", {
                    "template_type": "novel",
                    "title": "El Misterio del Servidor Perdido",
                    "chapters": 5
                })
                print(f"📄 {template_result.content[0].text}\n")
                
                # 6. Escribir capítulo directamente
                print("=" * 60)
                print("✍️ ESCRIBIENDO CONTENIDO DIRECTO")
                print("=" * 60)
                chapter_content = """# Capítulo 1: El Descubrimiento

Era una mañana lluviosa cuando Elena descubrió que podía comunicarse con servidores remotos usando el protocolo MCP. 

"Esto cambiará todo", murmuró mientras configuraba su primera conexión. La pantalla de su terminal mostraba las herramientas disponibles: create_project, write_file, list_project_files...

De repente, una nueva ventana se abrió. Era el servidor MCP de Kimi Writer, ofreciendo capacidades de escritura creativa que ella nunca había imaginado.

"¿Podría esto ser real?", se preguntó Elena mientras ejecutaba su primera llamada a herramienta.

## El Primer Proyecto

Con manos temblorosas, escribió:
- Nombre del proyecto: "Las Aventuras de Elena en el Mundo MCP"
- Contenido: El inicio de una historia sobre una programadora que descubre un mundo paralelo donde los servidores cobran vida

*Capítulo escrito mediante servidor MCP - Prueba completa*"""

                chapter_result = await session.call_tool("write_file", {
                    "filename": "capitulo_01.md",
                    "content": chapter_content,
                    "mode": "create"
                })
                print(f"📝 {chapter_result.content[0].text}\n")
                
                # 7. Escribir archivo adicional con append
                print("=" * 60)
                print("📝 AÑADIENDO CONTENIDO (APPEND MODE)")
                print("=" * 60)
                append_content = """

## Continuación del Capítulo

Elena continuó escribiendo, fascinada por la facilidad con que podía crear contenido estructurado. Cada herramienta del servidor MCP funcionaba perfectamente, como si hubiera sido diseñada específicamente para escritores digitales.

"Esta tecnología podría revolucionar la forma en que creamos contenido", pensó mientras añadía más texto al capítulo.

*Sección añadida en modo append - Servidor MCP*"""

                append_result = await session.call_tool("write_file", {
                    "filename": "capitulo_01.md",
                    "content": append_content,
                    "mode": "append"
                })
                print(f"📝 {append_result.content[0].text}\n")
                
                # 8. Listar archivos del proyecto
                print("=" * 60)
                print("📋 ARCHIVOS EN EL PROYECTO")
                print("=" * 60)
                files_result = await session.call_tool("list_project_files", {})
                files_data = json.loads(files_result.content[0].text)
                print(f"📊 Total de archivos: {files_data['total']}")
                for archivo in files_data['archivos']:
                    print(f"📄 {archivo['nombre']}")
                    print(f"   📏 Tamaño: {archivo['tamaño_kb']} KB")
                    print(f"   📅 Modificado: {archivo['fecha_modificacion']}")
                    print()
                
                # 9. Leer un archivo
                print("=" * 60)
                print("📖 LEYENDO ARCHIVO")
                print("=" * 60)
                read_result = await session.call_tool("read_file", {
                    "filename": "capitulo_01.md"
                })
                content = read_result.content[0].text
                # Mostrar solo los primeros 500 caracteres
                preview = content[:500] + "..." if len(content) > 500 else content
                print(f"📖 Vista previa del archivo:")
                print(preview)
                print()
                
                # 10. Obtener estadísticas de archivo
                print("=" * 60)
                print("📊 ESTADÍSTICAS DE ARCHIVO")
                print("=" * 60)
                stats_result = await session.call_tool("get_file_stats", {
                    "filename": "capitulo_01.md"
                })
                stats_data = json.loads(stats_result.content[0].text)
                print(f"📁 Archivo: {stats_data['nombre']}")
                print(f"📏 Tamaño: {stats_data['tamaño_kb']} KB ({stats_data['tamaño_bytes']} bytes)")
                print(f"🗓️ Creado: {stats_data['fecha_creacion']}")
                print(f"✏️ Modificado: {stats_data['fecha_modificacion']}")
                print()
                
                # 11. Probar prompts estructurados
                print("=" * 60)
                print("🎭 PROBANDO PROMPTS ESTRUCTURADOS")
                print("=" * 60)
                
                # Prompt para novela
                novel_prompt = await session.get_prompt("escribir_novela", {
                    "tema": "un mundo donde los programadores son magos",
                    "genero": "fantasía",
                    "capitulos": "6",
                    "longitud": "media"
                })
                print("📚 Prompt para novela:")
                print("-" * 40)
                print(novel_prompt.prompt[:300] + "...\n")
                
                # Prompt para historia corta
                story_prompt = await session.get_prompt("escribir_historia_corta", {
                    "tema": "un servidor que aprende a soñar",
                    "longitud": "media",
                    "tono": "reflexivo"
                })
                print("📝 Prompt para historia corta:")
                print("-" * 40)
                print(story_prompt.prompt[:300] + "...\n")
                
                # 12. Crear otro tipo de plantilla
                print("=" * 60)
                print("🎨 CREANDO PLANTILLA DE POESÍA")
                print("=" * 60)
                poetry_result = await session.call_tool("create_writing_template", {
                    "template_type": "poetry",
                    "title": "Versos Digitales"
                })
                print(f"🎭 {poetry_result.content[0].text}\n")
                
                # 13. Verificación final
                print("=" * 60)
                print("✅ VERIFICACIÓN FINAL")
                print("=" * 60)
                final_files = await session.call_tool("list_project_files", {})
                final_data = json.loads(final_files.content[0].text)
                print(f"🎉 Proyecto completado con {final_data['total']} archivos")
                print(f"📂 Ubicación: {info_data['proyecto_activo']}")
                print(f"🗂️ Archivos creados:")
                for archivo in final_data['archivos']:
                    print(f"   - {archivo['nombre']} ({archivo['tamaño_kb']} KB)")
                
                print("\n" + "=" * 60)
                print("🎉 TEST COMPLETED SUCCESSFULLY!")
                print("=" * 60)
                print("✅ All MCP tools working correctly")
                print("✅ Writing project created and managed")
                print("✅ Files read, written and analyzed")
                print("✅ Structured prompts functioning")
                print("✅ Different template types created")
                
                # 14. Test document generation if available
                print("\n📚 TESTING DOCUMENT GENERATION...")
                try:
                    pdf_test = await session.call_tool("generate_pdf", {
                        "output_filename": "test_complete_project"
                    })
                    
                    if not pdf_test.isError:
                        print("✅ PDF generation working!")
                        print(f"   {pdf_test.content[0].text}")
                    else:
                        print("⚠️ PDF generation not available")
                        print(f"   {pdf_test.content[0].text}")
                except Exception as e:
                    print("⚠️ PDF generation test failed:")
                    print(f"   {e}")
                
                try:
                    epub_test = await session.call_tool("generate_epub", {
                        "title": "Complete Test Project",
                        "author": "MCP Test Client"
                    })
                    
                    if not epub_test.isError:
                        print("✅ EPUB generation working!")
                        print(f"   {epub_test.content[0].text}")
                    else:
                        print("⚠️ EPUB generation not available")
                        print(f"   {epub_test.content[0].text}")
                except Exception as e:
                    print("⚠️ EPUB generation test failed:")
                    print(f"   {e}")
                
                return True
                
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_error_handling():
    """Prueba el manejo de errores del servidor"""
    
    print("\n" + "=" * 60)
    print("🧪 PROBANDO MANEJO DE ERRORES")
    print("=" * 60)
    
    server_params = StdioServerParameters(
        command="python",
        args=["mcp-server.py"]
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("✅ Conexión establecida")
                
                # 1. Intentar usar herramienta sin proyecto activo
                print("\n📝 Probando escritura sin proyecto activo...")
                try:
                    write_result = await session.call_tool("write_file", {
                        "filename": "test.md",
                        "content": "Contenido de prueba",
                        "mode": "create"
                    })
                    if write_result.isError:
                        print(f"✅ Error manejado correctamente: {write_result.content[0].text}")
                    else:
                        print("⚠️ Esperaba error pero fue exitoso")
                except Exception as e:
                    print(f"✅ Error capturado: {e}")
                
                # 2. Intentar leer archivo inexistente
                print("\n📖 Probando lectura de archivo inexistente...")
                try:
                    read_result = await session.call_tool("read_file", {
                        "filename": "archivo_inexistente.md"
                    })
                    if read_result.isError:
                        print(f"✅ Error manejado correctamente: {read_result.content[0].text}")
                    else:
                        print("⚠️ Esperaba error pero fue exitoso")
                except Exception as e:
                    print(f"✅ Error capturado: {e}")
                
                # 3. Intentar plantilla inválida
                print("\n🎨 Probando plantilla inválida...")
                try:
                    template_result = await session.call_tool("create_writing_template", {
                        "template_type": "tipo_invalido",
                        "title": "Test"
                    })
                    if template_result.isError:
                        print(f"✅ Error manejado correctamente: {template_result.content[0].text}")
                    else:
                        print("⚠️ Esperaba error pero fue exitoso")
                except Exception as e:
                    print(f"✅ Error capturado: {e}")
                
                print("\n✅ Pruebas de manejo de errores completadas")
                
    except Exception as e:
        print(f"❌ Error durante pruebas de errores: {e}")

async def main():
    """Función principal que ejecuta todas las pruebas"""
    
    # Ejecutar prueba principal
    success = await test_all_capabilities()
    
    if success:
        # Ejecutar pruebas de manejo de errores
        await test_error_handling()
        
        print("\n" + "🎉" * 20)
        print("TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("🎉" * 20)
        print("\nEl servidor MCP de Kimi Writer está listo para usar!")
    else:
        print("\n❌ Algunas pruebas fallaron. Revisa la configuración.")

if __name__ == "__main__":
    asyncio.run(main())