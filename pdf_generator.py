"""
PDF Generation tool for Kimi Writer MCP Server
Converts markdown projects to professionally formatted PDF documents
"""

import os
import re
import markdown
from pathlib import Path
from typing import List, Dict, Any
import html

# Import utilities
try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    PDF_AVAILABLE = True
except ImportError:
    HTML = None
    CSS = None
    FontConfiguration = None
    PDF_AVAILABLE = False


if PDF_AVAILABLE:
    class PDFGenerator:
        """Generates PDF documents from markdown files"""
        
        def __init__(self, project_path: str):
            self.project_path = Path(project_path)
            self.markdown_files = []
            self.toc_items = []
            
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
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split frontmatter and content
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    metadata_raw = parts[1].strip()
                    content = parts[2].strip()
                else:
                    metadata_raw = ""
                    content = content
            else:
                metadata_raw = ""
            
            # Parse metadata
            metadata = self._parse_frontmatter(metadata_raw)
            
            # Extract title (either from metadata or first heading)
            title = metadata.get('title', '')
            if not title:
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else file_path.stem
            
            # Extract headings for table of contents
            headings = self._extract_headings(content)
            
            return {
                'file_path': file_path,
                'title': title,
                'content': content,
                'metadata': metadata,
                'headings': headings,
                'word_count': len(content.split())
            }
        except Exception as e:
            raise Exception(f"Error reading {file_path}: {e}")
    
    def _parse_frontmatter(self, metadata_raw: str) -> Dict[str, str]:
        """Parse YAML-like frontmatter"""
        metadata = {}
        if not metadata_raw:
            return metadata
        
        for line in metadata_raw.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
        
        return metadata
    
    def _extract_headings(self, content: str) -> List[Dict[str, Any]]:
        """Extract headings for table of contents"""
        headings = []
        lines = content.split('\n')
        
        for line in lines:
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                
                # Create anchor
                anchor = re.sub(r'[^\w\s-]', '', title.lower())
                anchor = re.sub(r'\s+', '-', anchor)
                
                headings.append({
                    'level': min(level, 6),  # Max h6
                    'title': title,
                    'anchor': anchor
                })
        
        return headings
    
    def convert_to_html(self, file_data: Dict[str, Any]) -> str:
        """Convert markdown file content to HTML"""
        try:
            # Configure markdown extensions
            md = markdown.Markdown(extensions=[
                'markdown.extensions.toc',
                'markdown.extensions.tables',
                'markdown.extensions.codehilite',
                'markdown.extensions.fenced_code'
            ])
            
            # Convert to HTML
            html_content = md.convert(file_data['content'])
            
            # Wrap in article structure
            html_doc = f"""
            <article class="chapter" id="{self._create_anchor(file_data['title'])}">
                <h1>{html.escape(file_data['title'])}</h1>
                <div class="chapter-content">
                    {html_content}
                </div>
                <div class="page-break"></div>
            </article>
            """
            
            return html_doc
        except Exception as e:
            raise Exception(f"Error converting {file_data['file_path']} to HTML: {e}")
    
    def _create_anchor(self, title: str) -> str:
        """Create URL-friendly anchor from title"""
        anchor = re.sub(r'[^\w\s-]', '', title.lower())
        anchor = re.sub(r'\s+', '-', anchor)
        return anchor
    
    def generate_table_of_contents(self, all_files_data: List[Dict[str, Any]]) -> str:
        """Generate HTML table of contents"""
        toc_html = """
        <div class="toc">
            <h1>Table of Contents</h1>
            <ul class="toc-list">
        """
        
        for file_data in all_files_data:
            anchor = self._create_anchor(file_data['title'])
            toc_html += f"""
            <li class="toc-item">
                <a href="#{anchor}" class="toc-link">{html.escape(file_data['title'])}</a>
                {self._generate_sub_toc(file_data['headings'])}
            </li>
            """
        
        toc_html += """
            </ul>
        </div>
        <div class="page-break"></div>
        """
        
        return toc_html
    
    def _generate_sub_toc(self, headings: List[Dict[str, Any]]) -> str:
        """Generate sub-table of contents for headings"""
        if not headings:
            return ""
        
        sub_toc = "<ul class='toc-sublist'>"
        current_level = 1
        
        for heading in headings:
            level = heading['level']
            
            # Close previous sublists if needed
            while current_level >= level:
                sub_toc += "</ul>"
                current_level -= 1
            
            # Add new sublist if needed
            if level > current_level:
                sub_toc += "<ul class='toc-sublist'>"
                current_level = level
            
            sub_toc += f"<li><a href='#{heading['anchor']}' class='toc-sublink'>{html.escape(heading['title'])}</a></li>"
        
        # Close remaining sublists
        while current_level > 1:
            sub_toc += "</ul>"
            current_level -= 1
        
        sub_toc += "</ul>"
        return sub_toc
    
    def generate_css(self) -> str:
        """Generate CSS styling for PDF"""
        return """
        @page {
            size: A4;
            margin: 1in;
            @top-center {
                content: "Kimi Writer Project";
                font-size: 10pt;
                color: #666;
            }
            @bottom-center {
                content: counter(page);
                font-size: 10pt;
                color: #666;
            }
        }
        
        body {
            font-family: "Georgia", "Times New Roman", serif;
            line-height: 1.6;
            color: #333;
            max-width: none;
        }
        
        .cover {
            text-align: center;
            padding: 4rem 0;
            page-break-after: always;
        }
        
        .cover h1 {
            font-size: 3rem;
            margin-bottom: 2rem;
            color: #2c3e50;
        }
        
        .cover .subtitle {
            font-size: 1.5rem;
            color: #7f8c8d;
            margin-bottom: 3rem;
        }
        
        .cover .metadata {
            font-size: 1rem;
            color: #95a5a6;
        }
        
        .toc {
            page-break-after: always;
            margin: 2rem 0;
        }
        
        .toc h1 {
            font-size: 2rem;
            text-align: center;
            margin-bottom: 2rem;
            color: #2c3e50;
        }
        
        .toc-list {
            list-style: none;
            margin: 0;
            padding: 0;
        }
        
        .toc-item {
            margin-bottom: 1rem;
        }
        
        .toc-link {
            font-size: 1.2rem;
            font-weight: bold;
            text-decoration: none;
            color: #2c3e50;
        }
        
        .toc-sublist {
            list-style: none;
            margin: 0.5rem 0 0 2rem;
            padding: 0;
        }
        
        .toc-sublink {
            font-size: 1rem;
            text-decoration: none;
            color: #7f8c8d;
        }
        
        .chapter {
            margin-bottom: 3rem;
            page-break-inside: avoid;
        }
        
        .chapter h1 {
            font-size: 2.5rem;
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 0.5rem;
            margin-bottom: 2rem;
        }
        
        .chapter h2 {
            font-size: 2rem;
            color: #34495e;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        
        .chapter h3 {
            font-size: 1.5rem;
            color: #34495e;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }
        
        .chapter h4, .chapter h5, .chapter h6 {
            color: #34495e;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }
        
        .chapter-content p {
            margin-bottom: 1rem;
            text-align: justify;
        }
        
        .chapter-content blockquote {
            border-left: 4px solid #3498db;
            margin: 1rem 0;
            padding: 1rem;
            background-color: #f8f9fa;
            font-style: italic;
        }
        
        .chapter-content pre {
            background-color: #f4f4f4;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 1rem;
            overflow-x: auto;
            font-family: "Courier New", monospace;
        }
        
        .chapter-content code {
            background-color: #f4f4f4;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: "Courier New", monospace;
        }
        
        .chapter-content table {
            border-collapse: collapse;
            width: 100%;
            margin: 1rem 0;
        }
        
        .chapter-content th,
        .chapter-content td {
            border: 1px solid #ddd;
            padding: 0.75rem;
            text-align: left;
        }
        
        .chapter-content th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        
        .page-break {
            page-break-before: always;
        }
        
        .no-break {
            page-break-inside: avoid;
        }
        """
    
    def generate_pdf(self, output_path: str = None) -> str:
        """Generate complete PDF document"""
        if HTML is None:
            raise ImportError("WeasyPrint is required for PDF generation. Install with: pip install weasyprint")
        
        if not self.markdown_files:
            self.scan_project_files()
        
        if not self.markdown_files:
            raise ValueError("No markdown files found in project")
        
        # Extract content from all files
        all_files_data = []
        for file_path in self.markdown_files:
            file_data = self.extract_markdown_content(file_path)
            all_files_data.append(file_data)
        
        # Generate project title
        project_title = self._generate_project_title(all_files_data)
        
        # Create cover page
        cover_html = f"""
        <div class="cover">
            <h1>{html.escape(project_title)}</h1>
            <div class="subtitle">Generated with Kimi Writer MCP Server</div>
            <div class="metadata">
                Generated on: {self._get_current_date()}<br>
                Files: {len(all_files_data)} chapters/sections
            </div>
        </div>
        """
        
        # Generate table of contents
        toc_html = self.generate_table_of_contents(all_files_data)
        
        # Convert all content to HTML
        content_html = ""
        for file_data in all_files_data:
            content_html += self.convert_to_html(file_data)
        
        # Combine all HTML
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{html.escape(project_title)}</title>
            <style>
                {self.generate_css()}
            </style>
        </head>
        <body>
            {cover_html}
            {toc_html}
            {content_html}
        </body>
        </html>
        """
        
        # Generate PDF
        if not output_path:
            output_path = self.project_path / f"{project_title.replace(' ', '_').lower()}.pdf"
        
        # Configure fonts
        font_config = FontConfiguration()
        
        # Create PDF
        html_doc = HTML(string=full_html)
        css = CSS(string=self.generate_css(), font_config=font_config)
        
        html_doc.write_pdf(output_path, stylesheets=[css], font_config=font_config)
        
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
    
    def _get_current_date(self) -> str:
        """Get current date in readable format"""
        from datetime import datetime
        return datetime.now().strftime("%B %d, %Y")


if PDF_AVAILABLE:
    def generate_pdf_from_project(project_path: str, output_path: str = None) -> str:
    """
    Generate PDF from a markdown project
    
    Args:
        project_path: Path to the project directory
        output_path: Optional output path for the PDF
    
    Returns:
        Path to the generated PDF file
    """
    generator = PDFGenerator(project_path)
    return generator.generate_pdf(output_path)


if __name__ == "__main__":
    # Test the PDF generator
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_generator.py <project_directory> [output_pdf_path]")
        sys.exit(1)
    
    project_dir = sys.argv[1]
    output_pdf = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        pdf_path = generate_pdf_from_project(project_dir, output_pdf)
        print(f"✅ PDF generated successfully: {pdf_path}")
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        sys.exit(1)