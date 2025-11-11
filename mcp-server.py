#!/usr/bin/env python3
"""
MCP Server that exposes Kimi Writer tools
Allows other AI models to access creative writing capabilities
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

# Add kimi-writer directory to path to import its tools
try:
    # Try to get the script directory first
    script_dir = Path(__file__).parent
except NameError:
    # Fallback if __file__ is not available
    script_dir = Path.cwd()

# The MCP server is in kimi-writer-mcp/, so we need to go up twice to reach kimi-writer/
kimi_writer_path = script_dir.parent.parent / "kimi-writer"
sys.path.insert(0, str(kimi_writer_path))

try:
    from tools import write_file_impl, create_project_impl, compress_context_impl
    from utils import get_tool_map
except ImportError as e:
    print(f"Error importing Kimi Writer: {e}")
    print("Make sure the kimi-writer directory is in the correct location")
    sys.exit(1)

# Document generation capabilities (optional)
PDF_AVAILABLE = False
EPUB_AVAILABLE = False

def generate_pdf_from_project(project_path: str, output_path: str = None) -> str:
    raise ImportError("PDF generation not available. Install dependencies first.")

def generate_epub_from_project(project_path: str, output_path: str = None, 
                              title: str = None, author: str = "Kimi Writer", 
                              description: str = None) -> str:
    raise ImportError("EPUB generation not available. Install dependencies first.")

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    Tool,
    GetPromptResult,
    ListPromptsResult,
    Prompt
)

# Initialize MCP server
app = Server("kimi-writer-mcp")

# Global configuration
OUTPUT_DIRECTORY = "output"
ACTIVE_PROJECT = None

@app.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """
    Lists all available writing tools and document generation capabilities.
    
    Returns:
        ListToolsResult: Contains all available tools with their descriptions and parameters
    """
    return ListToolsResult(
        tools=[
            Tool(
                name="create_project",
                description="Creates a new writing project in the output directory. "
                          "Only one project can be active at a time.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "description": "Name of the project (will be automatically sanitized)"
                        }
                    },
                    "required": ["project_name"]
                }
            ),
            Tool(
                name="write_file",
                description="Writes content to a markdown file in the active project. "
                          "Supports three modes: create new, append to existing, or overwrite.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the .md file to create"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to the file"
                        },
                        "mode": {
                            "type": "string",
                            "enum": ["create", "append", "overwrite"],
                            "description": "Write mode: 'create' (new), 'append' (add), 'overwrite' (replace)"
                        }
                    },
                    "required": ["filename", "content", "mode"]
                }
            ),
            Tool(
                name="get_project_info",
                description="Gets information about the current active project",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="list_project_files",
                description="Lists all files in the active project",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="create_writing_template",
                description="Creates template files for different types of writing",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "template_type": {
                            "type": "string",
                            "enum": ["novel", "short_story", "book", "poetry"],
                            "description": "Type of template to create"
                        },
                        "title": {
                            "type": "string",
                            "description": "Title of the work"
                        },
                        "chapters": {
                            "type": "integer",
                            "description": "Number of chapters (for novels)"
                        }
                    },
                    "required": ["template_type", "title"]
                }
            ),
            Tool(
                name="read_file",
                description="Reads the content of a file in the active project",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the .md file to read"
                        }
                    },
                    "required": ["filename"]
                }
            ),
            Tool(
                name="get_file_stats",
                description="Gets statistics of a file (size, modification date)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the .md file to analyze"
                        }
                    },
                    "required": ["filename"]
                }
            )
        ]
    )

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> CallToolResult:
    """
    Executes Kimi Writer tools and document generation features.
    
    Args:
        name: Name of the tool to execute
        arguments: Dictionary of arguments for the tool
        
    Returns:
        CallToolResult: Contains the execution result or error information
    """
    
    try:
        if name == "create_project":
            project_name = arguments.get("project_name", "")
            if not project_name:
                return CallToolResult(
                    content=[{"type": "text", "text": "Error: project_name is required"}],
                    isError=True
                )
            
            # Ensure output directory exists
            os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
            
            # Call Kimi Writer tool
            result = create_project_impl(project_name)
            
            # Update active project
            update_active_project(result)
            
            return CallToolResult(
                content=[{"type": "text", "text": result}]
            )
        
        elif name == "write_file":
            filename = arguments.get("filename", "")
            content = arguments.get("content", "")
            mode = arguments.get("mode", "create")
            
            if not filename or not content:
                return CallToolResult(
                    content=[{"type": "text", "text": "Error: filename and content are required"}],
                    isError=True
                )
            
            # Ensure active project exists
            if not ACTIVE_PROJECT:
                return CallToolResult(
                    content=[{"type": "text", "text": "Error: No active project. Create one first with create_project."}],
                    isError=True
                )
            
            # Call Kimi Writer tool
            result = write_file_impl(filename, content, mode)
            return CallToolResult(
                content=[{"type": "text", "text": result}]
            )
        
        elif name == "get_project_info":
            if not ACTIVE_PROJECT:
                return CallToolResult(
                    content=[{"type": "text", "text": "No active project. Create one first with create_project."}]
                )
            
            info = {
                "active_project": ACTIVE_PROJECT,
                "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "output_directory": OUTPUT_DIRECTORY,
                "status": "active"
            }
            
            return CallToolResult(
                content=[{"type": "text", "text": json.dumps(info, ensure_ascii=False, indent=2)}]
            )
        
        elif name == "list_project_files":
            if not ACTIVE_PROJECT:
                return CallToolResult(
                    content=[{"type": "text", "text": "No active project."}]
                )
            
            if not os.path.exists(ACTIVE_PROJECT):
                return CallToolResult(
                    content=[{"type": "text", "text": f"Project directory not found: {ACTIVE_PROJECT}"}]
                )
            
            files = []
            for file in os.listdir(ACTIVE_PROJECT):
                if file.endswith('.md') and not file.startswith('.context'):
                    file_path = os.path.join(ACTIVE_PROJECT, file)
                    size = os.path.getsize(file_path)
                    mod_date = datetime.fromtimestamp(os.path.getmtime(file_path))
                    files.append({
                        "name": file,
                        "size_bytes": size,
                        "size_kb": round(size / 1024, 2),
                        "modified_date": mod_date.strftime("%Y-%m-%d %H:%M:%S"),
                        "path": file_path
                    })
            
            return CallToolResult(
                content=[{"type": "text", "text": json.dumps({"files": files, "total": len(files)}, ensure_ascii=False, indent=2)}]
            )
        
        elif name == "create_writing_template":
            template_type = arguments.get("template_type", "")
            title = arguments.get("title", "")
            chapters = arguments.get("chapters", 5)
            
            templates = {
                "novel": f"""# {title}

## Novel

*A complete work of fiction*

### Project Structure
- {chapters} planned chapters
- Character development
- Plot and subplot development
- Satisfying resolution

### Chapter 1

[Chapter content goes here]

*Develop the introduction, present main characters, and establish the conflict.*

---

*Novel project created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Tools: Kimi Writer MCP Server*""",
                
                "short_story": f"""# {title}

## Short Story

*A self-contained narrative*

### Narrative Elements
- Introduction and setup
- Conflict development
- Climax and resolution
- Central message or theme

### The Story

[Complete story content here]

*A story that should be read in one sitting, with a beginning, development, and satisfying ending.*

---

*Short story created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Tools: Kimi Writer MCP Server*""",
                
                "book": f"""# {title}

## Book

*A non-fiction or extensive fiction work*

### Book Structure
- Introduction
- Thematic chapters
- Conclusions
- References (if applicable)

### Introduction

[Introduction content here]

### Chapter 1: [Chapter Topic]

[Chapter content here]

*Develop each chapter as a coherent section of the book.*

---

*Book created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Tools: Kimi Writer MCP Server*""",
                
                "poetry": f"""# {title}

## Poetry Collection

*A lyrical exploration of the theme*

### About This Collection
This collection explores the theme through different poetic forms and perspectives.

### Poem 1: [Title]

[First poem content here]

### Poem 2: [Title]

[Second poem content here]

*Each poem can approach the theme from a different angle or be part of a narrative sequence.*

---

*Poetry collection created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Tools: Kimi Writer MCP Server*"""
            }
            
            if template_type not in templates:
                return CallToolResult(
                    content=[{"type": "text", "text": f"Invalid template type: {template_type}. Use: novel, short_story, book, poetry"}],
                    isError=True
                )
            
            if not ACTIVE_PROJECT:
                return CallToolResult(
                    content=[{"type": "text", "text": "Error: No active project. Create one first with create_project."}],
                    isError=True
                )
            
            content = templates[template_type]
            filename = f"{template_type}_{title.replace(' ', '_').lower()}.md"
            
            # Create file using Kimi Writer tool
            result = write_file_impl(filename, content, "create")
            return CallToolResult(
                content=[{"type": "text", "text": f"Template created: {result}"}]
            )
        
        elif name == "read_file":
            filename = arguments.get("filename", "")
            
            if not filename:
                return CallToolResult(
                    content=[{"type": "text", "text": "Error: filename is required"}],
                    isError=True
                )
            
            if not ACTIVE_PROJECT:
                return CallToolResult(
                    content=[{"type": "text", "text": "Error: No active project."}],
                    isError=True
                )
            
            file_path = os.path.join(ACTIVE_PROJECT, filename)
            if not file_path.endswith('.md'):
                file_path += '.md'
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                return CallToolResult(
                    content=[{"type": "text", "text": f"Content of {filename}:\n\n{content}"}]
                )
            except FileNotFoundError:
                return CallToolResult(
                    content=[{"type": "text", "text": f"Error: File {filename} not found in active project."}],
                    isError=True
                )
            except Exception as e:
                return CallToolResult(
                    content=[{"type": "text", "text": f"Error reading file: {str(e)}"}],
                    isError=True
                )
        
        elif name == "get_file_stats":
            filename = arguments.get("filename", "")
            
            if not filename:
                return CallToolResult(
                    content=[{"type": "text", "text": "Error: filename is required"}],
                    isError=True
                )
            
            if not ACTIVE_PROJECT:
                return CallToolResult(
                    content=[{"type": "text", "text": "Error: No active project."}],
                    isError=True
                )
            
            file_path = os.path.join(ACTIVE_PROJECT, filename)
            if not file_path.endswith('.md'):
                file_path += '.md'
            
            try:
                stat = os.stat(file_path)
                stats_info = {
                    "name": filename,
                    "full_path": file_path,
                    "size_bytes": stat.st_size,
                    "size_kb": round(stat.st_size / 1024, 2),
                    "created_date": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
                    "modified_date": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    "exists": True
                }
                
                return CallToolResult(
                    content=[{"type": "text", "text": json.dumps(stats_info, ensure_ascii=False, indent=2)}]
                )
            except FileNotFoundError:
                return CallToolResult(
                    content=[{"type": "text", "text": f"Error: File {filename} not found."}],
                    isError=True
                )
            except Exception as e:
                return CallToolResult(
                    content=[{"type": "text", "text": f"Error getting statistics: {str(e)}"}],
                    isError=True
                )
        
        elif name == "generate_pdf":
            if not PDF_AVAILABLE:
                return CallToolResult(
                    content=[{"type": "text", "text": "PDF generation is not available. Install dependencies with: pip install weasyprint markdown"}],
                    isError=True
                )
            
            if not ACTIVE_PROJECT:
                return CallToolResult(
                    content=[{"type": "text", "text": "Error: No active project. Create one first with create_project."}],
                    isError=True
                )
            
            output_filename = arguments.get("output_filename", "")
            
            try:
                if output_filename and not output_filename.endswith('.pdf'):
                    output_filename += '.pdf'
                
                pdf_path = generate_pdf_from_project(ACTIVE_PROJECT, output_filename)
                
                return CallToolResult(
                    content=[{"type": "text", "text": f"PDF generated successfully: {os.path.basename(pdf_path)}"}]
                )
            except Exception as e:
                return CallToolResult(
                    content=[{"type": "text", "text": f"Error generating PDF: {str(e)}"}],
                    isError=True
                )
        
        elif name == "generate_epub":
            if not EPUB_AVAILABLE:
                return CallToolResult(
                    content=[{"type": "text", "text": "EPUB generation is not available. Install dependencies with: pip install ebooklib beautifulsoup4 markdown2 python-frontmatter"}],
                    isError=True
                )
            
            if not ACTIVE_PROJECT:
                return CallToolResult(
                    content=[{"type": "text", "text": "Error: No active project. Create one first with create_project."}],
                    isError=True
                )
            
            output_filename = arguments.get("output_filename", "")
            title = arguments.get("title", "")
            author = arguments.get("author", "Kimi Writer")
            
            try:
                if output_filename and not output_filename.endswith('.epub'):
                    output_filename += '.epub'
                
                epub_path = generate_epub_from_project(
                    ACTIVE_PROJECT, 
                    output_filename, 
                    title or None, 
                    author
                )
                
                return CallToolResult(
                    content=[{"type": "text", "text": f"EPUB generated successfully: {os.path.basename(epub_path)}"}]
                )
            except Exception as e:
                return CallToolResult(
                    content=[{"type": "text", "text": f"Error generating EPUB: {str(e)}"}],
                    isError=True
                )
        
        else:
            return CallToolResult(
                content=[{"type": "text", "text": f"Tool '{name}' not found"}],
                isError=True
            )
    
    except Exception as e:
        return CallToolResult(
            content=[{"type": "text", "text": f"Error executing tool '{name}': {str(e)}"}],
            isError=True
        )

@app.list_prompts()
async def handle_list_prompts() -> ListPromptsResult:
    """
    Lists predefined prompts for different types of writing.
    
    Returns:
        ListPromptsResult: Contains all available prompts with their arguments and descriptions
    """
    return ListPromptsResult(
        prompts=[
            Prompt(
                name="write_novel",
                description="Prompt for creating a complete novel",
                arguments=[
                    {
                        "name": "theme",
                        "description": "Main theme of the novel",
                        "required": True
                    },
                    {
                        "name": "genre",
                        "description": "Literary genre (fiction, mystery, romance, sci-fi, etc.)",
                        "required": True
                    },
                    {
                        "name": "chapters",
                        "description": "Number of chapters (default: 8-12)",
                        "required": False
                    },
                    {
                        "name": "length",
                        "description": "Approximate length per chapter (short, medium, long)",
                        "required": False
                    }
                ]
            ),
            Prompt(
                name="write_short_story",
                description="Prompt for creating a short story",
                arguments=[
                    {
                        "name": "theme",
                        "description": "Theme or premise of the story",
                        "required": True
                    },
                    {
                        "name": "length",
                        "description": "Desired length (short: 1k-2k, medium: 2k-4k, long: 4k-6k words)",
                        "required": False
                    },
                    {
                        "name": "tone",
                        "description": "Story tone (dramatic, comedic, reflective, etc.)",
                        "required": False
                    }
                ]
            ),
            Prompt(
                name="write_nonfiction_book",
                description="Prompt for creating a non-fiction book",
                arguments=[
                    {
                        "name": "theme",
                        "description": "Main theme of the book",
                        "required": True
                    },
                    {
                        "name": "audience",
                        "description": "Target audience (beginners, experts, general)",
                        "required": False
                    },
                    {
                        "name": "chapters",
                        "description": "Number of planned chapters",
                        "required": False
                    }
                ]
            )
        ]
    )

@app.get_prompt()
async def handle_get_prompt(name: str, arguments: dict) -> GetPromptResult:
    """
    Gets a specific prompt for writing based on the prompt name and arguments.
    
    Args:
        name: Name of the prompt to retrieve
        arguments: Dictionary of arguments to customize the prompt
        
    Returns:
        GetPromptResult: Contains the generated prompt and description
    """
    
    if name == "write_novel":
        theme = arguments.get("theme", "")
        genre = arguments.get("genre", "")
        chapters = arguments.get("chapters", "8-12")
        length = arguments.get("length", "medium")
        
        word_counts = {
            "short": "1500-2500",
            "medium": "2500-4000", 
            "long": "4000-6000"
        }
        
        words = word_counts.get(length, "2500-4000")
        
        prompt = f"""
Create a {genre} novel about "{theme}" with approximately {chapters} chapters.

GENERAL INSTRUCTIONS:
1. First create a writing project using the create_project tool
2. Develop a detailed plan for the novel
3. Write each chapter as a separate file (chapter_01.md, chapter_02.md, etc.)
4. Make sure each chapter has {words} words
5. Include typical elements of the {genre} genre

REQUIRED STRUCTURE:
- Introduction and character establishment
- Development of the main conflict
- Various chapters that develop the plot
- Exciting climax
- Satisfying resolution

WRITING GUIDELINES:
- Develop memorable and realistic characters
- Create interesting and progressive conflicts
- Maintain appropriate narrative pace
- Include natural dialogue and vivid descriptions
- Provide a satisfying ending for all narrative arcs

SPECIFIC TO {genre.upper()}:
{genre_specific_guidance(genre)}

Remember to use the MCP server tools to create and manage your writing project in an organized manner.
        """
        
        return GetPromptResult(
            description=f"Create a {genre} novel about {theme} with {chapters} chapters",
            prompt=prompt.strip()
        )
    
    elif name == "write_short_story":
        theme = arguments.get("theme", "")
        length = arguments.get("length", "medium")
        tone = arguments.get("tone", "narrative")
        
        word_counts = {
            "short": "1000-2000",
            "medium": "2000-4000", 
            "long": "4000-6000"
        }
        
        words = word_counts.get(length, "2000-4000")
        
        prompt = f"""
Write a short story about "{theme}" with approximately {words} words.

INSTRUCTIONS:
1. First create a writing project using the create_project tool
2. Develop a clear narrative structure (introduction, development, climax, ending)
3. Write the complete story in a single file (short_story.md)
4. Focus on a specific aspect of the theme {theme}
5. Maintain a {tone} tone throughout the narrative

NARRATIVE STRUCTURE:
- Introduction: Present characters, setting, and situation
- Development: Establish the conflict or problematic situation
- Climax: Moment of greatest tension or revelation
- Resolution: End that closes the story

OBJECTIVES:
- Self-contained and complete story
- Clear and resonant theme or message
- Literary style appropriate for the {tone} tone
- Satisfying ending that resolves the main conflict
- Convincing characters even in a short narrative

SPECIFIC TONE: {tone.upper()}
{tone_specific_guidance(tone)}

Use the MCP server tools to create and manage your writing project.
        """
        
        return GetPromptResult(
            description=f"Short story about {theme} ({length}) with {tone} tone",
            prompt=prompt.strip()
        )
    
    elif name == "write_nonfiction_book":
        theme = arguments.get("theme", "")
        audience = arguments.get("audience", "general")
        chapters = arguments.get("chapters", "8-12")
        
        prompt = f"""
Create a non-fiction book about "{theme}" targeted at a {audience} audience.

INSTRUCTIONS:
1. First create a writing project using the create_project tool
2. Develop a complete book structure
3. Write each chapter as a separate file (chapter_01.md, chapter_02.md, etc.)
4. Make sure each chapter has 2000-3000 words
5. Include introduction, thematic development, and conclusions

BOOK STRUCTURE:
- Introduction: Present the theme and establish the book's purpose
- {chapters} thematic chapters that develop the main theme
- Conclusion: Summarize key points and provide closure

AUDIENCE GUIDELINES:
{audience_specific_guidance(audience)}

REQUIRED ELEMENTS:
- Factual and verifiable information
- Practical examples and case studies
- Logical and progressive structure
- Clear and accessible language
- References or sources when appropriate
- Exercises or reflection questions

Use the MCP server tools to create and manage your writing project in an organized manner.
        """
        
        return GetPromptResult(
            description=f"Non-fiction book about {theme} for {audience} audience with {chapters} chapters",
            prompt=prompt.strip()
        )
    
    else:
        return GetPromptResult(
            description="Prompt not found",
            prompt=f"Prompt '{name}' not available. Available prompts: write_novel, write_short_story, write_nonfiction_book."
        )

def genre_specific_guidance(genre: str) -> str:
    """Provides specific guidance based on genre"""
    guidance = {
        "mystery": "- Include clues and red herrings\n- Develop convincing detective\n- Maintain suspense until the end\n- Resolve all plot threads",
        "romance": "- Develop chemistry between characters\n- Include believable relationship obstacles\n- Focus on emotional growth\n- Provide satisfying happy ending",
        "sci-fi": "- Develop consistent worldbuilding\n- Explore technological/scientific implications\n- Create characters that adapt to the future world\n- Balance action with reflection",
        "fantasy": "- Create coherent magic/world systems\n- Develop rich mythology\n- Include classic fantasy archetypes\n- Balance adventure with character development",
        "thriller": "- Maintain fast pace\n- Use cliffhangers between chapters\n- Create constant tension\n- Include unexpected twists",
        "fiction": "- Focus on character development\n- Explore universal themes\n- Use symbolism and metaphors\n- Create emotional resonance"
    }
    return guidance.get(genre, "- Maintain narrative consistency\n- Develop believable characters\n- Create interesting conflicts")

def tone_specific_guidance(tone: str) -> str:
    """Provides specific guidance based on tone"""
    guidance = {
        "dramatic": "- Use emotive and powerful language\n- Explore deep internal conflicts\n- Create moments of high emotional tension",
        "comedic": "- Include humor in situations and dialogue\n- Use irony and satire when appropriate\n- Maintain lightness without trivializing the theme",
        "reflective": "- Use contemplation and introspection\n- Explore philosophical or existential themes\n- Create contemplative and paced rhythm",
        "narrative": "- Focus on telling the story clearly\n- Use direct and accessible prose\n- Balance dialogue with description",
        "melancholic": "- Use poetic and evocative language\n- Explore themes of loss, nostalgia, or sadness\n- Create nostalgic atmosphere",
        "optimistic": "- Focus on hope and growth\n- Use positive and uplifting language\n- Highlight hopeful aspects of the situation"
    }
    return guidance.get(tone, "- Maintain tonal consistency\n- Use language appropriate for the theme\n- Ensure tone serves the story")

def audience_specific_guidance(audience: str) -> str:
    """Provides specific guidance based on audience"""
    guidance = {
        "beginners": "- Use simple and clear language\n- Define technical terms\n- Provide basic examples\n- Avoid specialized jargon",
        "experts": "- Use precise terminology\n- Include academic references\n- Assume base knowledge of the topic\n- Deepen into technical details",
        "general": "- Balance accessibility with depth\n- Explain concepts when necessary\n- Use varied examples\n- Maintain interest of common reader"
    }
    return guidance.get(audience, "- Use clear and professional language\n- Provide relevant examples\n- Maintain logical structure")

def update_active_project(result_text: str):
    """Extracts and stores the active project path from the result"""
    global ACTIVE_PROJECT
    
    # Search for the path in the result message
    lines = result_text.split('\n')
    for line in lines:
        if "output/" in line and ("activated" in line.lower() or "set as active" in line.lower() or "created" in line.lower()):
            # Extract the project path using quotes or context
            start = line.find("'")
            if start != -1:
                end = line.find("'", start + 1)
                if end != -1:
                    ACTIVE_PROJECT = line[start+1:end]
                    break
            # Also search without quotes
            elif "output/" in line:
                parts = line.split()
                for part in parts:
                    if "output/" in part:
                        ACTIVE_PROJECT = part.rstrip('.,')
                        break

async def main():
    """
    Main function to run the MCP server and handle all incoming connections.
    
    Initializes the server, creates necessary directories, and starts listening
    for MCP client connections via stdio.
    """
    try:
        # Ensure output directory exists
        os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
        
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="kimi-writer-mcp",
                    server_version="1.0.0",
                    capabilities=app.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )
    except KeyboardInterrupt:
        pass  # Clean shutdown
    except Exception as e:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())