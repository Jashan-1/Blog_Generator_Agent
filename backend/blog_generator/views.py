# backend/blog_generator/views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import BlogPost
from .serializers import BlogPostSerializer
from .agents.blog_agents import BlogCrewAgent
from .utils.markdown_utils import MarkdownConverter
import os
from django.conf import settings
import tempfile
import json

class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer

    @action(detail=False, methods=['post'])
    def generate_blog(self, request):
        title = request.data.get('title')
        prompts = request.data.get('prompts')

        if not title or not prompts:
            return Response(
                {"error": "Title and prompts are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Initialize CrewAI agent and generate content first
            agent = BlogCrewAgent()
            generated_content = agent.generate_blog(title, prompts)

            if not generated_content:
                return Response(
                    {"error": "Failed to generate content"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Create blog post only after successful content generation
            blog_post = BlogPost.objects.create(
                title=title,
                prompts=prompts,
                generated_content=generated_content,
                markdown_content=generated_content
            )

            # Convert to PDF
            try:
                pdf_path, html_content = MarkdownConverter.create_pdf(generated_content)
                response_data = BlogPostSerializer(blog_post).data
                response_data['pdf_path'] = pdf_path
                
                return Response(
                    response_data,
                    status=status.HTTP_201_CREATED
                )
            except Exception as pdf_error:
                # If PDF conversion fails, still return the blog post without PDF
                return Response(
                    BlogPostSerializer(blog_post).data,
                    status=status.HTTP_201_CREATED
                )

        except Exception as e:
            # Log the error for debugging
            print(f"Error generating blog: {str(e)}")
            # Return a proper error response
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        # Generate new PDF if needed
        if instance.markdown_content:
            try:
                pdf_path, _ = MarkdownConverter.create_pdf(instance.markdown_content)
                data['pdf_path'] = pdf_path
            except Exception as e:
                print(f"Error generating PDF: {str(e)}")

        return Response(data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        # Generate PDFs for each blog post
        for item in data:
            blog_post = queryset.get(id=item['id'])
            if blog_post.markdown_content:
                try:
                    pdf_path, _ = MarkdownConverter.create_pdf(blog_post.markdown_content)
                    item['pdf_path'] = pdf_path
                except Exception as e:
                    print(f"Error generating PDF for blog {blog_post.id}: {str(e)}")

        return Response(data)

    def perform_destroy(self, instance):
        # Clean up PDF file if it exists
        if hasattr(instance, 'pdf_path') and instance.pdf_path:
            MarkdownConverter.cleanup_pdf(instance.pdf_path)
        instance.delete()