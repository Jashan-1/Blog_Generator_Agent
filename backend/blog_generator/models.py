# blog_generator/models.py

from django.db import models

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    prompts = models.TextField()
    generated_content = models.TextField(blank=True)
    markdown_content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        app_label = 'blog_generator'