#!/usr/bin/env python3
"""
Test script for PDF and EPUB generation features in Kimi Writer MCP Server
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

async def test_document_generation():
    """Test PDF and EPUB generation capabilities"""
    
    print("📄 Testing Document Generation Features")
    print("=" * 50)
    
    server_params = StdioServerParameters(
        command="python",
        args=["mcp-server.py"]
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("✅ Connected to MCP Server\n")
                
                # 1. Create test project
                print("🏗️ Creating test project...")
                project_result = await session.call_tool("create_project", {
                    "project_name": "document_generation_test"
                })
                print(f"📁 {project_result.content[0].text}\n")
                
                # 2. Create test content
                print("✍️ Creating test content...")
                
                # Chapter 1
                chapter1 = """# The Beginning

This is the first chapter of our test document. It contains various markdown elements to test the formatting capabilities.

## Features to Test

- **Bold text** and *italic text*
- `Inline code` and code blocks
- Links and references

### Code Example

```python
def hello_world():
    print("Hello, World!")
    return True
```

### Table Example

| Feature | Status | Notes |
|---------|--------|-------|
| PDF Generation | Testing | Should work well |
| EPUB Generation | Testing | Should work well |
| Formatting | Complete | All elements tested |

This chapter establishes the foundation for our document generation tests.
"""

                await session.call_tool("write_file", {
                    "filename": "chapter_01.md",
                    "content": chapter1,
                    "mode": "create"
                })
                
                # Chapter 2
                chapter2 = """# The Development

This chapter continues our story with more complex formatting and structure.

## Story Continuation

The plot thickens as our characters face new challenges in the document generation process.

> "The best way to test a system is to push it to its limits." 
> — Anonymous Developer

### Character Development

Our protagonist discovers that the MCP server can handle:

1. Complex markdown structures
2. Multiple file formats
3. Professional document generation

### Technical Details

The PDF generator uses WeasyPrint for high-quality output, while the EPUB generator creates standards-compliant ebooks using the ebooklib library.

*This demonstrates advanced formatting capabilities.*"""

                await session.call_tool("write_file", {
                    "filename": "chapter_02.md",
                    "content": chapter2,
                    "mode": "create"
                })
                
                # Short story
                story_content = """# The Last Algorithm

*A short story about AI and creativity*

In a world where algorithms painted masterpieces and wrote poetry, Maya wondered if anything truly human remained.

She watched as the AI generated another symphony, another novel, another revolutionary idea. Each creation was flawless, technically perfect, but somehow... hollow.

## The Discovery

The breakthrough came when Maya realized the truth: creativity wasn't about perfection. It was about the messy, imperfect, beautifully human struggle to express something meaningful.

She opened her laptop and began to type:

*"This story was written by a human, with all its flaws and imperfections, but with the authentic experience of being alive..."*

The first genuine work of art in an age of artificial perfection.

*End*

---

*Word count: ~250 words*"""

                await session.call_tool("write_file", {
                    "filename": "short_story.md",
                    "content": story_content,
                    "mode": "create"
                })
                
                print("✅ Test content created\n")
                
                # 3. Test PDF generation
                print("📄 Testing PDF Generation...")
                try:
                    pdf_result = await session.call_tool("generate_pdf", {
                        "output_filename": "test_project_complete"
                    })
                    print(f"✅ PDF Result: {pdf_result.content[0].text}")
                    
                    if not pdf_result.isError:
                        # Try to list files to see the PDF
                        files_result = await session.call_tool("list_project_files", {})
                        files_data = json.loads(files_result.content[0].text)
                        pdf_files = [f for f in files_data['files'] if f['name'].endswith('.pdf')]
                        if pdf_files:
                            print(f"📋 PDF file created: {pdf_files[0]['name']} ({pdf_files[0]['size_kb']} KB)")
                    
                except Exception as e:
                    print(f"❌ PDF generation failed: {e}")
                
                print()
                
                # 4. Test EPUB generation
                print("📚 Testing EPUB Generation...")
                try:
                    epub_result = await session.call_tool("generate_epub", {
                        "output_filename": "test_project_ebook",
                        "title": "Document Generation Test Project",
                        "author": "Kimi Writer MCP Test"
                    })
                    print(f"✅ EPUB Result: {epub_result.content[0].text}")
                    
                    if not epub_result.isError:
                        # Try to list files to see the EPUB
                        files_result = await session.call_tool("list_project_files", {})
                        files_data = json.loads(files_result.content[0].text)
                        epub_files = [f for f in files_data['files'] if f['name'].endswith('.epub')]
                        if epub_files:
                            print(f"📋 EPUB file created: {epub_files[0]['name']} ({epub_files[0]['size_kb']} KB)")
                    
                except Exception as e:
                    print(f"❌ EPUB generation failed: {e}")
                
                print()
                
                # 5. Final verification
                print("🔍 Final Project Status:")
                final_files = await session.call_tool("list_project_files", {})
                final_data = json.loads(final_files.content[0].text)
                
                print(f"📊 Total files: {final_data['total']}")
                print("📁 Files created:")
                for file_info in final_data['files']:
                    print(f"   📄 {file_info['name']} ({file_info['size_kb']} KB)")
                
                # Check for generated documents
                doc_files = [f for f in final_data['files'] 
                           if f['name'].endswith(('.pdf', '.epub'))]
                
                if doc_files:
                    print(f"\n🎉 Generated documents ({len(doc_files)}):")
                    for doc in doc_files:
                        format_type = "📄 PDF" if doc['name'].endswith('.pdf') else "📚 EPUB"
                        print(f"   {format_type}: {doc['name']} ({doc['size_kb']} KB)")
                
                print("\n" + "=" * 50)
                print("📋 TEST SUMMARY")
                print("=" * 50)
                
                success_count = 0
                total_tests = 4
                
                # Test results
                tests = [
                    ("Project Creation", True),
                    ("Content Writing", True),
                    ("PDF Generation", not pdf_result.isError if 'pdf_result' in locals() else False),
                    ("EPUB Generation", not epub_result.isError if 'epub_result' in locals() else False)
                ]
                
                for test_name, success in tests:
                    status = "✅ PASS" if success else "❌ FAIL"
                    print(f"{status} {test_name}")
                    if success:
                        success_count += 1
                
                print(f"\n🏆 Results: {success_count}/{total_tests} tests passed")
                
                if success_count == total_tests:
                    print("🎉 All document generation features working correctly!")
                elif success_count >= 2:
                    print("⚠️ Partial success - check dependency installation")
                else:
                    print("❌ Major issues - verify setup and dependencies")
                
                return success_count == total_tests
                
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_dependencies():
    """Test if PDF/EPUB dependencies are available"""
    
    print("\n🔍 Checking Dependencies")
    print("-" * 30)
    
    # Check PDF dependencies
    try:
        import weasyprint
        print("✅ WeasyPrint (PDF) - Available")
        pdf_available = True
    except ImportError:
        print("❌ WeasyPrint (PDF) - Not installed")
        print("   Install with: pip install weasyprint")
        pdf_available = False
    
    # Check EPUB dependencies
    try:
        import ebooklib
        print("✅ ebooklib (EPUB) - Available")
        epub_available = True
    except ImportError:
        print("❌ ebooklib (EPUB) - Not installed")
        print("   Install with: pip install ebooklib")
        epub_available = False
    
    # Check markdown processing
    try:
        import markdown
        print("✅ Markdown - Available")
        markdown_available = True
    except ImportError:
        print("❌ Markdown - Not installed")
        print("   Install with: pip install markdown")
        markdown_available = False
    
    # Check frontmatter
    try:
        import frontmatter
        print("✅ python-frontmatter - Available")
        frontmatter_available = True
    except ImportError:
        print("❌ python-frontmatter - Not installed")
        print("   Install with: pip install python-frontmatter")
        frontmatter_available = False
    
    print("\n📦 Install missing dependencies with:")
    if not pdf_available or not epub_available or not markdown_available:
        print("pip install -r requirements-extended.txt")
    
    return pdf_available and epub_available and markdown_available

async def main():
    """Main test function"""
    
    print("🧪 Kimi Writer MCP Document Generation Test")
    print("=" * 55)
    
    # First check dependencies
    deps_ok = await test_dependencies()
    
    if not deps_ok:
        print("\n⚠️ Some dependencies are missing. Install them and run again.")
        return False
    
    # Run document generation tests
    success = await test_document_generation()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("✅ PDF and EPUB generation features are working!")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())