from django.db import models

# Create your models here.
class ImageFile(models.Model):
    original_name = models.CharField(max_length=2048)
    real_path = models.CharField(max_length=2048)
    parsed = models.CharField(max_length=2048)
