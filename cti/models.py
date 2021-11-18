from django.db import models
from django.db.models import Model
# Create your models here.
class ToDo(models.Model):
    email = models.EmailField(max_length=254)
    key = models.TextField(max_length=200)
    description = models.TextField()
    image1 = models.ImageField(upload_to = "img/%y")
    image2 = models.ImageField(upload_to = "img/%y")
   

    def __str__(self):
        return self.email

class decode(models.Model):
    key2 = models.TextField(max_length=200)
    snap = models.ImageField(upload_to = "img/%y")

    def __str__(self):
        return self.key2