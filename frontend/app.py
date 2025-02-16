# frontend/app.py

import streamlit as st
import requests
import json
import base64
from typing import Optional
import time

class BlogGeneratorApp:
    def __init__(self):
        self.API_BASE_URL = "http://localhost:8000/api"
    
    @staticmethod
    def display_pdf_base64(pdf_base64: str):
        """Display PDF from base64 string in Streamlit"""
        try:
            # Create PDF display HTML with responsive width
            pdf_display = f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="100%" height="800" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error displaying PDF: {str(e)}")
    
    def generate_blog(self):
        st.write("### Create Your Blog Post")
        
        # Blog creation form
        with st.form("blog_form"):
            title = st.text_input("Blog Title", 
                                help="Enter a clear, engaging title for your blog post")
            
            prompts = st.text_area("Blog Prompts", 
                                 help="Enter specific topics, keywords, or aspects you want to cover")
            
            submitted = st.form_submit_button("Generate Blog")
        
        if submitted:
            if not title or not prompts:
                st.warning("Please enter both title and prompts")
                return

            with st.spinner("Generating your blog post... This may take a few minutes."):
                try:
                    response = requests.post(
                        f"{self.API_BASE_URL}/blogs/generate_blog/",
                        json={"title": title, "prompts": prompts},
                        timeout=300  # 5-minute timeout
                    )
                    
                    try:
                        blog_data = response.json()
                    except json.JSONDecodeError:
                        st.error(f"Invalid response from server: {response.text}")
                        return

                    if response.status_code == 201:
                        st.success("Blog post generated successfully!")
                        
                        # Create tabs for different views
                        tab1, tab2 = st.tabs(["Markdown Preview", "PDF Preview"])
                        
                        with tab1:
                            st.markdown("### Markdown Preview")
                            if 'markdown_content' in blog_data:
                                st.markdown(blog_data['markdown_content'])
                            else:
                                st.warning("No markdown content available")
                        
                        with tab2:
                            st.markdown("### PDF Preview")
                            if 'pdf_base64' in blog_data and blog_data['pdf_base64']:
                                self.display_pdf_base64(blog_data['pdf_base64'])
                            else:
                                st.warning("PDF preview not available")
                        
                        # Download buttons
                        st.write("### Download Options")
                        col1, col2 = st.columns(2)
                        
                        if 'markdown_content' in blog_data:
                            with col1:
                                if st.download_button(
                                    label="Download Markdown",
                                    data=blog_data['markdown_content'],
                                    file_name=f"{title.lower().replace(' ', '_')}.md",
                                    mime="text/markdown"
                                ):
                                    st.success("Markdown file downloaded!")
                        
                        if 'pdf_base64' in blog_data and blog_data['pdf_base64']:
                            with col2:
                                try:
                                    pdf_bytes = base64.b64decode(blog_data['pdf_base64'])
                                    if st.download_button(
                                        label="Download PDF",
                                        data=pdf_bytes,
                                        file_name=f"{title.lower().replace(' ', '_')}.pdf",
                                        mime="application/pdf"
                                    ):
                                        st.success("PDF file downloaded!")
                                except Exception as e:
                                    st.error(f"Error preparing PDF download: {str(e)}")
                    else:
                        error_msg = blog_data.get('error', 'Unknown error')
                        st.error(f"Error generating blog: {error_msg}")
                
                except requests.exceptions.Timeout:
                    st.error("Request timed out. The server took too long to respond.")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error connecting to the server: {str(e)}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")

def main():
    st.set_page_config(
        page_title="AI Blog Generator",
        page_icon="📝",
        layout="wide"
    )
    
    st.title("🤖 AI Blog Generator")
    
    app = BlogGeneratorApp()
    app.generate_blog()

if __name__ == "__main__":
    main()