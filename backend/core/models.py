from django.db import models


class CMSPage(models.Model):
    slug = models.SlugField(max_length=120, unique=True)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_cmspage"
        ordering = ["slug"]

    def __str__(self):
        return self.slug
