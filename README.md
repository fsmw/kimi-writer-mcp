# Kimi Writer MCP Server 🚀

[![GitHub stars](https://img.shields.io/github/stars/fsmw/kimi-writer-mcp?style=social)](https://github.com/fsmw/kimi-writer-mcp/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/fsmw/kimi-writer-mcp?style=social)](https://github.com/fsmw/kimi-writer-mcp/network)
[![GitHub issues](https://img.shields.io/github/issues/fsmw/kimi-writer-mcp)](https://github.com/fsmw/kimi-writer-mcp/issues)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A complete **Model Context Protocol (MCP) server** that exposes Kimi Writer's creative writing capabilities to other AI models. Transform your AI writing workflow with professional document generation and structured prompts.

## ✨ Features

### 🔧 Writing Tools (8 tools)
- **create_project** - Create organized writing projects
- **write_file** - Write markdown with create/append/overwrite modes  
- **get_project_info** - Get active project information
- **list_project_files** - List project files with metadata
- **read_file** - Read file contents from active project
- **get_file_stats** - Get file statistics (size, dates, etc.)
- **create_writing_template** - Generate templates for novels, short stories, books, poetry

### 📝 Structured Prompts (3 prompts)
- **write_novel** - Complete novel writing prompts with genre-specific guidance
- **write_short_story** - Short story prompts with tone and length options
- **write_nonfiction_book** - Non-fiction book prompts with audience targeting

### 📚 Document Generation (Optional - 2 tools)
- **generate_pdf** - Professional PDFs with TOC, typography, pagination
- **generate_epub** - Standards-compliant EPUBs with metadata and navigation

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/fsmw/kimi-writer-mcp.git
cd kimi-writer-mcp
```

### 2. Install dependencies
```bash
# Install MCP dependencies
pip install -r requirements.txt

# Install Kimi Writer dependencies
cd ../kimi-writer
pip install -r requirements.txt
cd ../kimi-writer-mcp

# For PDF/EPUB generation (optional)
pip install -r requirements-extended.txt
```

### 3. Run the server
```bash
python mcp-server.py
```

### 4. Test functionality
```bash
python test-client.py
```

## 🤖 Claude Desktop Integration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "kimi-writer": {
      "command": "python",
      "args": ["/path/to/kimi-writer-mcp/mcp-server.py"],
      "cwd": "/path/to/kimi-writer-mcp"
    }
  }
}
```

## 💻 Usage Examples

### Writing a Novel with PDF Export
```python
# Create project and write content
await session.call_tool("create_project", {"project_name": "cyberpunk_novel"})
await session.call_tool("write_file", {
    "filename": "chapter_01.md",
    "content": "# Chapter 1\n\nIn the neon-lit streets...",
    "mode": "create"
})

# Generate PDF when complete
await session.call_tool("generate_pdf", {"output_filename": "complete_novel"})
```

### Creating a Short Story Collection
```python
# Get structured prompt
prompt = await session.get_prompt("write_short_story", {
    "theme": "AI and consciousness",
    "length": "medium",
    "tone": "philosophical"
})

# Write stories using the prompt
# ... your AI model generates content ...
```

## 📊 Project Status

✅ **COMPLETE AND TESTED**

- ✅ All 8 MCP tools functioning correctly
- ✅ Project creation and management working
- ✅ File operations (read, write, append, overwrite) tested  
- ✅ Template generation for all writing types
- ✅ Structured prompts with specific guidance
- ✅ Professional documentation and examples
- ✅ Cross-platform compatibility

## 🔧 Architecture

- **MCP Protocol Compliance** - Universal AI model compatibility
- **Modular Design** - Clean separation of concerns
- **Graceful Degradation** - Optional features work without errors
- **Professional Code Quality** - Kimi Writer standards with comprehensive docstrings
- **Unicode Support** - International content handling
- **Cross-Platform** - Unix/Linux/Windows compatibility

## 📦 Dependencies

### Core (Required)
- `mcp>=1.0.0` - Model Context Protocol
- `openai>=1.0.0` - OpenAI SDK (Kimi Writer compatibility)
- `httpx>=0.24.0` - HTTP client
- `python-dotenv>=1.0.0` - Environment management
- `markdown>=3.5.1` - Markdown processing

### Document Generation (Optional)
- `weasyprint>=60.0` - PDF generation
- `ebooklib>=0.18` - EPUB creation
- `beautifulsoup4>=4.12.0` - HTML parsing
- `python-frontmatter>=1.0.0` - Metadata handling

## 🧪 Testing

Run comprehensive test suites:

```bash
# Test all MCP features
python test-client.py

# Test document generation
python test-documents.py

# Check dependencies
python start.py --check
```

## 📚 Documentation

- [📖 README.md](README.md) - Complete documentation
- [🔧 IMPLEMENTATION.md](IMPLEMENTATION.md) - Technical details
- [💡 EXAMPLES.md](EXAMPLES.md) - Usage examples
- [📋 SUMMARY.md](SUMMARY.md) - Project summary

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python test-client.py`
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🌟 Credits

Created by **Fernando San Martin** with 🧡 Crush

Transforming Kimi Writer into a powerful, reusable writing tool that can be integrated with any MCP-compatible AI system.

---

**🚀 Ready for Claude Desktop integration!**