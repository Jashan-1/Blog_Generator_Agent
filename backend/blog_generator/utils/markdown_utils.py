import markdown
from weasyprint import HTML
from typing import Tuple
import tempfile
import os

class MarkdownConverter:
    @staticmethod
    def markdown_to_html(markdown_text: str) -> str:
        """Convert markdown to HTML with extensions"""
        return markdown.markdown(
            markdown_text,
            extensions=[
                'extra',
                'codehilite',
                'tables',
                'toc',
                'fenced_code',
                'sane_lists'
            ]
        )
    
    @staticmethod
    def create_pdf(markdown_text: str) -> Tuple[str, str]:
        """
        Convert markdown to PDF and return both the PDF path and HTML content
        """
        # Convert markdown to HTML
        html_content = MarkdownConverter.markdown_to_html(markdown_text)
        
        # Add CSS for better styling
        styled_html = f"""
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    @page {{
                        margin: 2.5cm;
                        @top-center {{
                            content: "Blog Post";
                        }}
                        @bottom-center {{
                            content: counter(page);
                        }}
                    }}
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                        line-height: 1.6;
                        font-size: 11pt;
                    }}
                    h1, h2, h3 {{
                        color: #1a1a1a;
                        margin-top: 1.5em;
                        margin-bottom: 0.5em;
                    }}
                    h1 {{ font-size: 24pt; }}
                    h2 {{ font-size: 18pt; }}
                    h3 {{ font-size: 14pt; }}
                    code {{
                        font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
                        background-color: #f6f8fa;
                        padding: 0.2em 0.4em;
                        border-radius: 3px;
                        font-size: 85%;
                    }}
                    pre {{
                        background-color: #f6f8fa;
                        padding: 16px;
                        border-radius: 6px;
                        overflow-x: auto;
                        line-height: 1.45;
                    }}
                    blockquote {{
                        border-left: 4px solid #dfe2e5;
                        color: #6a737d;
                        margin: 0;
                        padding-left: 1em;
                    }}
                    img {{
                        max-width: 100%;
                        height: auto;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 1em 0;
                    }}
                    th, td {{
                        border: 1px solid #dfe2e5;
                        padding: 6px 13px;
                    }}
                    th {{
                        background-color: #f6f8fa;
                    }}
                    a {{
                        color: #0366d6;
                        text-decoration: none;
                    }}
                    ul, ol {{
                        padding-left: 2em;
                    }}
                    li {{
                        margin: 0.25em 0;
                    }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
        </html>
        """
        
        # Create temporary files
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        
        try:
            # Convert HTML to PDF using WeasyPrint
            HTML(string=styled_html).write_pdf(temp_pdf.name)
            return temp_pdf.name, styled_html
            
        except Exception as e:
            # Clean up temporary file if conversion fails
            os.unlink(temp_pdf.name)
            raise Exception(f"PDF conversion failed: {str(e)}")
            
    @staticmethod
    def cleanup_pdf(pdf_path: str):
        """Clean up temporary PDF file"""
        try:
            os.unlink(pdf_path)
        except:
            pass