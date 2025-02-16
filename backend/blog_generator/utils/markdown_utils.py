# import markdown
# from weasyprint import HTML
# from typing import Tuple
# import tempfile
# import os

# class MarkdownConverter:
#     @staticmethod
#     def markdown_to_html(markdown_text: str) -> str:
#         """Convert markdown to HTML with extensions"""
#         return markdown.markdown(
#             markdown_text,
#             extensions=[
#                 'extra',
#                 'codehilite',
#                 'tables',
#                 'toc',
#                 'fenced_code',
#                 'sane_lists'
#             ]
#         )
    
#     @staticmethod
#     def create_pdf(markdown_text: str) -> Tuple[str, str]:
#         """
#         Convert markdown to PDF and return both the PDF path and HTML content
#         """
#         # Convert markdown to HTML
#         html_content = MarkdownConverter.markdown_to_html(markdown_text)
        
#         # Add CSS for better styling
#         styled_html = f"""
#         <!DOCTYPE html>
#         <html>
#             <head>
#                 <meta charset="UTF-8">
#                 <style>
#                     @page {{
#                         margin: 2.5cm;
#                         @top-center {{
#                             content: "Blog Post";
#                         }}
#                         @bottom-center {{
#                             content: counter(page);
#                         }}
#                     }}
#                     body {{
#                         font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
#                         line-height: 1.6;
#                         font-size: 11pt;
#                     }}
#                     h1, h2, h3 {{
#                         color: #1a1a1a;
#                         margin-top: 1.5em;
#                         margin-bottom: 0.5em;
#                     }}
#                     h1 {{ font-size: 24pt; }}
#                     h2 {{ font-size: 18pt; }}
#                     h3 {{ font-size: 14pt; }}
#                     code {{
#                         font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
#                         background-color: #f6f8fa;
#                         padding: 0.2em 0.4em;
#                         border-radius: 3px;
#                         font-size: 85%;
#                     }}
#                     pre {{
#                         background-color: #f6f8fa;
#                         padding: 16px;
#                         border-radius: 6px;
#                         overflow-x: auto;
#                         line-height: 1.45;
#                     }}
#                     blockquote {{
#                         border-left: 4px solid #dfe2e5;
#                         color: #6a737d;
#                         margin: 0;
#                         padding-left: 1em;
#                     }}
#                     img {{
#                         max-width: 100%;
#                         height: auto;
#                     }}
#                     table {{
#                         border-collapse: collapse;
#                         width: 100%;
#                         margin: 1em 0;
#                     }}
#                     th, td {{
#                         border: 1px solid #dfe2e5;
#                         padding: 6px 13px;
#                     }}
#                     th {{
#                         background-color: #f6f8fa;
#                     }}
#                     a {{
#                         color: #0366d6;
#                         text-decoration: none;
#                     }}
#                     ul, ol {{
#                         padding-left: 2em;
#                     }}
#                     li {{
#                         margin: 0.25em 0;
#                     }}
#                 </style>
#             </head>
#             <body>
#                 {html_content}
#             </body>
#         </html>
#         """
        
#         # Create temporary files
#         temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        
#         try:
#             # Convert HTML to PDF using WeasyPrint
#             HTML(string=styled_html).write_pdf(temp_pdf.name)
#             return temp_pdf.name, styled_html
            
#         except Exception as e:
#             # Clean up temporary file if conversion fails
#             os.unlink(temp_pdf.name)
#             raise Exception(f"PDF conversion failed: {str(e)}")
            
#     @staticmethod
#     def cleanup_pdf(pdf_path: str):
#         """Clean up temporary PDF file"""
#         try:
#             os.unlink(pdf_path)
#         except:
#             pass

# # backend/blog_generator/utils/markdown_utils.py

# # backend/blog_generator/utils/markdown_utils.py

# import markdown
# from weasyprint import HTML, CSS
# from typing import Tuple
# import tempfile
# import os
# import base64
# from io import BytesIO
# import requests
# from urllib.parse import urlparse
# import re

# class MarkdownConverter:
#     @staticmethod
#     def download_image(url: str) -> bytes:
#         """Download image from URL and return as bytes"""
#         try:
#             response = requests.get(url, timeout=10)
#             response.raise_for_status()
#             return response.content
#         except Exception as e:
#             print(f"Error downloading image from {url}: {str(e)}")
#             return None

#     @staticmethod
#     def process_images_in_markdown(markdown_text: str) -> Tuple[str, dict]:
#         """Process images in markdown and return updated text and image data"""
#         image_pattern = r'!\[(.*?)\]\((.*?)\)'
#         images = {}
        
#         def replace_image(match):
#             alt_text = match.group(1)
#             url = match.group(2)
            
#             # Generate a unique key for the image
#             img_key = f"img_{len(images)}"
            
#             # Download and store image data
#             image_data = MarkdownConverter.download_image(url)
#             if image_data:
#                 images[img_key] = {
#                     'data': image_data,
#                     'url': url,
#                     'alt': alt_text
#                 }
#                 # Replace URL with key in markdown
#                 return f'![{alt_text}]({img_key})'
            
#             return match.group(0)  # Keep original if download fails
        
#         processed_text = re.sub(image_pattern, replace_image, markdown_text)
#         return processed_text, images

#     @staticmethod
#     def markdown_to_html(markdown_text: str) -> str:
#         """Convert markdown to HTML with extensions"""
#         return markdown.markdown(
#             markdown_text,
#             extensions=[
#                 'extra',
#                 'codehilite',
#                 'tables',
#                 'toc',
#                 'fenced_code',
#                 'sane_lists'
#             ]
#         )

#     @staticmethod
#     def create_pdf(markdown_text: str) -> Tuple[str, str]:
#         """Convert markdown to PDF and return both base64 encoded PDF and HTML content"""
#         try:
#             # Process images in markdown
#             processed_markdown, images = MarkdownConverter.process_images_in_markdown(markdown_text)
            
#             # Convert to HTML
#             html_content = MarkdownConverter.markdown_to_html(processed_markdown)
            
#             # Create temporary directory for images
#             with tempfile.TemporaryDirectory() as temp_dir:
#                 # Save images to temporary directory
#                 for img_key, img_data in images.items():
#                     img_path = os.path.join(temp_dir, f"{img_key}.jpg")
#                     with open(img_path, 'wb') as f:
#                         f.write(img_data['data'])
                    
#                     # Replace image keys with file paths in HTML
#                     html_content = html_content.replace(
#                         f'src="{img_key}"',
#                         f'src="file://{img_path}"'
#                     )
                
#                 # Add styling
#                 styled_html = MarkdownConverter.get_styled_html(html_content)
                
#                 # Convert to PDF using BytesIO
#                 pdf_buffer = BytesIO()
#                 HTML(string=styled_html).write_pdf(pdf_buffer)
                
#                 # Get base64 encoded PDF
#                 pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
                
#                 return pdf_base64, styled_html
            
#         except Exception as e:
#             raise Exception(f"PDF conversion failed: {str(e)}")

#     @staticmethod
#     def get_styled_html(html_content: str) -> str:
#         """Returns HTML with styling"""
#         return f"""
#         <!DOCTYPE html>
#         <html>
#             <head>
#                 <meta charset="UTF-8">
#                 <style>
#                     /* Previous styles remain the same */
                    
#                     /* Add image-specific styles */
#                     img {{
#                         max-width: 100%;
#                         height: auto;
#                         margin: 1em 0;
#                         display: block;
#                     }}
                    
#                     .image-caption {{
#                         font-size: 0.9em;
#                         color: #666;
#                         text-align: center;
#                         margin-top: 0.5em;
#                     }}
                    
#                     .image-credits {{
#                         border-top: 1px solid #ddd;
#                         margin-top: 2em;
#                         padding-top: 1em;
#                     }}
                    
#                     .image-credit-item {{
#                         margin-bottom: 0.5em;
#                         font-size: 0.9em;
#                     }}
#                 </style>
#             </head>
#             <body>
#                 {html_content}
#             </body>
#         </html>
#         """

#     @staticmethod
#     def create_pdf(markdown_text: str) -> Tuple[str, str]:
#         """
#         Convert markdown to PDF and return both base64 encoded PDF and HTML content
#         Returns:
#             Tuple[str, str]: (base64_encoded_pdf, html_content)
#         """
#         try:
#             # Convert markdown to HTML
#             html_content = MarkdownConverter.markdown_to_html(markdown_text)
            
#             # Add styling
#             styled_html = MarkdownConverter.get_styled_html(html_content)
            
#             # Convert to PDF using BytesIO
#             pdf_buffer = BytesIO()
#             HTML(string=styled_html).write_pdf(pdf_buffer)
            
#             # Get base64 encoded PDF
#             pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
            
#             return pdf_base64, styled_html
            
#         except Exception as e:
#             raise Exception(f"PDF conversion failed: {str(e)}")

#     @staticmethod
#     def create_pdf_file(markdown_text: str) -> Tuple[str, str]:
#         """
#         Convert markdown to PDF file and return both the PDF path and HTML content
#         (For compatibility with existing code that needs file output)
#         """
#         # Convert markdown to HTML
#         html_content = MarkdownConverter.markdown_to_html(markdown_text)
#         styled_html = MarkdownConverter.get_styled_html(html_content)
        
#         # Create temporary file
#         temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        
#         try:
#             # Convert HTML to PDF using WeasyPrint
#             HTML(string=styled_html).write_pdf(temp_pdf.name)
#             return temp_pdf.name, styled_html
            
#         except Exception as e:
#             # Clean up temporary file if conversion fails
#             os.unlink(temp_pdf.name)
#             raise Exception(f"PDF conversion failed: {str(e)}")

#     @staticmethod
#     def cleanup_pdf(pdf_path: str):
#         """Clean up temporary PDF file"""
#         try:
#             if os.path.exists(pdf_path):
#                 os.unlink(pdf_path)
#         except Exception as e:
#             print(f"Error cleaning up PDF file: {str(e)}")


# backend/blog_generator/utils/markdown_utils.py

import markdown
from weasyprint import HTML, CSS
from typing import Tuple
import base64
from io import BytesIO

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
    def get_styled_html(html_content: str) -> str:
        """Returns HTML with styling"""
        return f"""
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
                    .mermaid {{
                        text-align: center;
                    }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
        </html>
        """

    @staticmethod
    def create_pdf(markdown_text: str) -> Tuple[str, str]:
        """
        Convert markdown to PDF and return both base64 encoded PDF and HTML content
        Returns:
            Tuple[str, str]: (base64_encoded_pdf, html_content)
        """
        try:
            # Convert markdown to HTML
            html_content = MarkdownConverter.markdown_to_html(markdown_text)
            styled_html = MarkdownConverter.get_styled_html(html_content)
            
            # Convert to PDF using BytesIO
            pdf_buffer = BytesIO()
            HTML(string=styled_html).write_pdf(pdf_buffer)
            
            # Convert to base64
            pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
            
            return pdf_base64, styled_html
            
        except Exception as e:
            print(f"PDF conversion error: {str(e)}")
            raise Exception(f"PDF conversion failed: {str(e)}")