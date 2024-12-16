from django.db import models

# Create your models here.
class Category_maladie(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Patient(models.Model):
    name = models.CharField(max_length=100)
    name_maladie = models.TextField()
    category_maladie = models.ForeignKey(
        Category_maladie, related_name="patients", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name
    
class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    hospital = models.CharField(max_length=100)
