"""
EPUB Generation tool for Kimi Writer MCP Server
Converts markdown projects to professionally formatted EPUB ebooks
"""

import os
import re
import json
import zipfile
import markdown
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import html
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

# Import utilities
try:
    from ebooklib import epub
    from bs4 import BeautifulSoup
    import frontmatter
    EPUB_AVAILABLE = True
except ImportError:
    epub = None
    BeautifulSoup = None
    frontmatter = None
    EPUB_AVAILABLE = False


if EPUB_AVAILABLE:
    class EPUBGenerator:
        """Generates EPUB documents from markdown files"""
        
        def __init__(self, project_path: str):
            self.project_path = Path(project_path)
            self.markdown_files = []
            self.book = None
            
        def scan_project_files(self) -> List[Path]:
        """Scan project directory for markdown files"""
        if not self.project_path.exists():
            raise FileNotFoundError(f"Project directory not found: {self.project_path}")
        
        # Find all markdown files, excluding context summaries
        self.markdown_files = [
            f for f in self.project_path.glob("*.md") 
            if not f.name.startswith('.context')
        ]
        
        # Sort files naturally (chapter_01.md, chapter_02.md, etc.)
        self.markdown_files.sort(key=self._natural_sort_key)
        return self.markdown_files
    
    def _natural_sort_key(self, path: Path) -> List:
        """Natural sorting key for file names"""
        def convert(text):
            return [int(text) if text.isdigit() else text.lower()]
        
        return [convert(chunk) for chunk in re.split(r'(\d+)', path.stem)]
    
    def extract_markdown_content(self, file_path: Path) -> Dict[str, Any]:
        """Extract content and metadata from markdown file"""
        try:
            # Use python-frontmatter for better metadata handling
            if frontmatter:
                post = frontmatter.load(file_path)
                metadata = {k: str(v) for k, v in post.metadata.items()}
                content = post.content
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                metadata = {}
            
            # Extract title (either from metadata or first heading)
            title = metadata.get('title', '')
            if not title:
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else file_path.stem
            
            # Extract description from metadata or first paragraph
            description = metadata.get('description', '')
            if not description:
                desc_match = re.search(r'^# .+$', content, re.MULTILINE)
                if desc_match:
                    # Use first paragraph after title as description
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.strip() and not line.startswith('#'):
                            description = line.strip()
                            break
            
            # Extract headings for table of contents
            headings = self._extract_headings(content)
            
            return {
                'file_path': file_path,
                'title': title,
                'content': content,
                'metadata': metadata,
                'headings': headings,
                'description': description,
                'word_count': len(content.split())
            }
        except Exception as e:
            raise Exception(f"Error reading {file_path}: {e}")
    
    def _extract_headings(self, content: str) -> List[Dict[str, Any]]:
        """Extract headings for table of contents"""
        headings = []
        lines = content.split('\n')
        
        for line in lines:
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                
                # Create anchor
                anchor = self._create_anchor(title)
                
                headings.append({
                    'level': min(level, 6),  # Max h6
                    'title': title,
                    'anchor': anchor
                })
        
        return headings
    
    def _create_anchor(self, title: str) -> str:
        """Create URL-friendly anchor from title"""
        anchor = re.sub(r'[^\w\s-]', '', title.lower())
        anchor = re.sub(r'\s+', '-', anchor)
        return anchor
    
    def convert_to_xhtml(self, file_data: Dict[str, Any], index: int) -> epub.EpubHtml:
        """Convert markdown file content to XHTML"""
        try:
            # Configure markdown extensions
            md = markdown.Markdown(extensions=[
                'markdown.extensions.toc',
                'markdown.extensions.tables',
                'markdown.extensions.codehilite',
                'markdown.extensions.fenced_code',
                'markdown.extensions.attr_list'
            ])
            
            # Convert to HTML
            html_content = md.convert(file_data['content'])
            
            # Clean and format HTML
            if BeautifulSoup:
                soup = BeautifulSoup(html_content, 'html.parser')
                # Add IDs to headings for navigation
                for i, heading in enumerate(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])):
                    if not heading.get('id'):
                        heading['id'] = f"chapter_{index}_heading_{i}"
                
                # Clean up HTML
                for code_block in soup.find_all('pre'):
                    code_block['class'] = code_block.get('class', []) + ['code-block']
                
                for code in soup.find_all('code'):
                    if not code.find_parent('pre'):
                        code['class'] = code.get('class', []) + ['inline-code']
                
                html_content = str(soup)
            
            # Create XHTML document
            title = file_data['title']
            xhtml_content = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{html.escape(title)}</title>
    <link rel="stylesheet" type="text/css" href="style.css"/>
    <meta http-equiv="Content-Type" content="application/xhtml+xml; charset=utf-8"/>
</head>
<body>
    <div class="chapter" id="chapter_{index}">
        <h1 class="chapter-title">{html.escape(title)}</h1>
        <div class="chapter-content">
            {html_content}
        </div>
    </div>
</body>
</html>"""
            
            # Create EPUB chapter
            chapter = epub.EpubHtml(
                title=title,
                file_name=f'chapter_{index:02d}.xhtml',
                lang='en'
            )
            chapter.content = xhtml_content
            
            return chapter
            
        except Exception as e:
            raise Exception(f"Error converting {file_data['file_path']} to XHTML: {e}")
    
    def generate_css(self) -> str:
        """Generate CSS styling for EPUB"""
        return """
/* EPUB Stylesheet for Kimi Writer Projects */

body {
    font-family: "Georgia", "Times New Roman", serif;
    line-height: 1.6;
    color: #333;
    margin: 0;
    padding: 1em;
}

h1 {
    font-size: 2.5em;
    color: #2c3e50;
    border-bottom: 2px solid #3498db;
    padding-bottom: 0.5em;
    margin-bottom: 1em;
    page-break-after: avoid;
}

h2 {
    font-size: 2em;
    color: #34495e;
    margin-top: 1.5em;
    margin-bottom: 0.75em;
    page-break-after: avoid;
}

h3 {
    font-size: 1.5em;
    color: #34495e;
    margin-top: 1.25em;
    margin-bottom: 0.5em;
    page-break-after: avoid;
}

h4, h5, h6 {
    color: #34495e;
    margin-top: 1em;
    margin-bottom: 0.5em;
    page-break-after: avoid;
}

p {
    margin-bottom: 1em;
    text-align: justify;
    orphans: 2;
    widows: 2;
}

.chapter {
    page-break-before: always;
}

.chapter:first-child {
    page-break-before: auto;
}

.chapter-title {
    text-align: center;
    margin-bottom: 2em;
    font-size: 2.5em;
    color: #2c3e50;
}

.chapter-content blockquote {
    border-left: 4px solid #3498db;
    margin: 1em 0;
    padding: 1em;
    background-color: #f8f9fa;
    font-style: italic;
}

pre {
    background-color: #f4f4f4;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 1em;
    overflow-x: auto;
    font-family: "Courier New", "Monaco", monospace;
    font-size: 0.9em;
    page-break-inside: avoid;
}

.code-block {
    background-color: #f8f8f8;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 1em;
    margin: 1em 0;
    overflow-x: auto;
    font-family: "Courier New", "Monaco", monospace;
    font-size: 0.85em;
}

.inline-code {
    background-color: #f4f4f4;
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-family: "Courier New", "Monaco", monospace;
    font-size: 0.9em;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}

th, td {
    border: 1px solid #ddd;
    padding: 0.75em;
    text-align: left;
}

th {
    background-color: #f2f2f2;
    font-weight: bold;
}

ul, ol {
    margin-bottom: 1em;
    padding-left: 2em;
}

li {
    margin-bottom: 0.5em;
}

a {
    color: #3498db;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

img {
    max-width: 100%;
    height: auto;
    margin: 1em 0;
}

.page-break {
    page-break-before: always;
}

/* Typography enhancements */
.lead {
    font-size: 1.25em;
    font-weight: 300;
    line-height: 1.6;
}

.text-center {
    text-align: center;
}

.text-right {
    text-align: right;
}

/* Print-specific styles */
@media print {
    body {
        font-size: 12pt;
        line-height: 1.5;
    }
    
    h1 {
        font-size: 24pt;
        page-break-after: avoid;
    }
    
    h2 {
        font-size: 18pt;
        page-break-after: avoid;
    }
    
    h3 {
        font-size: 14pt;
        page-break-after: avoid;
    }
    
    .chapter {
        page-break-before: always;
    }
}
        """
    
    def create_ncx_table_of_contents(self, chapters: List[epub.EpubHtml]) -> str:
        """Create NCX table of contents XML"""
        nav_points = []
        
        for i, chapter in enumerate(chapters):
            nav_point = f"""
    <navPoint id="navpoint-{i+1}" playOrder="{i+1}">
        <navLabel>
            <text>{html.escape(chapter.title)}</text>
        </navLabel>
        <content src="{chapter.file_name}"/>
    </navPoint>"""
            nav_points.append(nav_point)
        
        ncx_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
    <head>
        <meta content="1" name="dtb:depth"/>
        <meta content="0" name="dtb:totalPageCount"/>
        <meta content="0" name="dtb:maxPageNumber"/>
    </head>
    <docTitle>
        <text>Kimi Writer Project</text>
    </docTitle>
    <navMap>
        {''.join(nav_points)}
    </navMap>
</ncx>"""
        
        return ncx_content
    
    def generate_epub(self, output_path: str = None, title: str = None, 
                     author: str = "Kimi Writer", description: str = None) -> str:
        """Generate complete EPUB document"""
        if epub is None:
            raise ImportError("ebooklib is required for EPUB generation. Install with: pip install ebooklib")
        
        if not self.markdown_files:
            self.scan_project_files()
        
        if not self.markdown_files:
            raise ValueError("No markdown files found in project")
        
        # Extract content from all files
        all_files_data = []
        for file_path in self.markdown_files:
            file_data = self.extract_markdown_content(file_path)
            all_files_data.append(file_data)
        
        # Generate project metadata
        if not title:
            title = self._generate_project_title(all_files_data)
        if not description:
            description = self._generate_project_description(all_files_data)
        
        # Create EPUB book
        self.book = epub.EpubBook()
        
        # Set metadata
        self.book.set_identifier('kimi-writer-project')
        self.book.set_title(title)
        self.book.set_language('en')
        self.book.add_author(author)
        if description:
            self.book.add_metadata('DC', 'description', description)
        self.book.add_metadata('DC', 'creator', 'Kimi Writer MCP Server')
        self.book.add_metadata('DC', 'date', datetime.now().isoformat())
        
        # Add CSS
        css = self.generate_css()
        nav_css = epub.EpubItem(
            uid="nav_css",
            file_name="style.css",
            media_type="text/css",
            content=css
        )
        self.book.add_item(nav_css)
        
        # Convert all files to EPUB chapters
        chapters = []
        for i, file_data in enumerate(all_files_data):
            chapter = self.convert_to_xhtml(file_data, i)
            chapters.append(chapter)
            self.book.add_item(chapter)
        
        # Add chapters to spine
        self.book.spine = ['nav'] + chapters
        
        # Create table of contents
        self.book.toc = chapters
        
        # Add navigation
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())
        
        # Generate NCX table of contents
        ncx_content = self.create_ncx_table_of_contents(chapters)
        ncx_item = epub.EpubItem(
            uid="ncx",
            file_name="toc.ncx",
            media_type="application/x-dtbncx+xml",
            content=ncx_content
        )
        self.book.add_item(ncx_item)
        
        # Generate EPUB
        if not output_path:
            output_path = self.project_path / f"{title.replace(' ', '_').lower()}.epub"
        
        epub.write_epub(str(output_path), self.book, {})
        
        return str(output_path)
    
    def _generate_project_title(self, all_files_data: List[Dict[str, Any]]) -> str:
        """Generate project title from files or metadata"""
        # Check for common project indicators
        for file_data in all_files_data:
            metadata = file_data.get('metadata', {})
            if 'project_title' in metadata:
                return metadata['project_title']
            if 'title' in metadata and 'novel' in file_data['file_path'].name.lower():
                return metadata['title']
        
        # Use the first file's title as fallback
        if all_files_data:
            return all_files_data[0]['title']
        
        return "Kimi Writer Project"
    
    def _generate_project_description(self, all_files_data: List[Dict[str, Any]]) -> str:
        """Generate project description"""
        if all_files_data:
            descriptions = []
            for file_data in all_files_data[:3]:  # First 3 files
                if file_data.get('description'):
                    descriptions.append(file_data['description'])
            
            if descriptions:
                return ' '.join(descriptions)[:500]  # Limit length
        
        return f"A creative writing project with {len(all_files_data)} sections, generated with Kimi Writer MCP Server."


if EPUB_AVAILABLE:
    def generate_epub_from_project(project_path: str, output_path: str = None, 
                                  title: str = None, author: str = "Kimi Writer", 
                                  description: str = None) -> str:
    """
    Generate EPUB from a markdown project
    
    Args:
        project_path: Path to the project directory
        output_path: Optional output path for the EPUB
        title: Optional title for the EPUB
        author: Optional author name
        description: Optional description
    
    Returns:
        Path to the generated EPUB file
    """
    generator = EPUBGenerator(project_path)
    return generator.generate_epub(output_path, title, author, description)


if __name__ == "__main__":
    # Test the EPUB generator
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python epub_generator.py <project_directory> [output_epub_path] [title]")
        sys.exit(1)
    
    project_dir = sys.argv[1]
    output_epub = sys.argv[2] if len(sys.argv) > 2 else None
    title = sys.argv[3] if len(sys.argv) > 3 else None
    
    try:
        epub_path = generate_epub_from_project(project_dir, output_epub, title)
        print(f"✅ EPUB generated successfully: {epub_path}")
    except Exception as e:
        print(f"❌ Error generating EPUB: {e}")
        sys.exit(1)