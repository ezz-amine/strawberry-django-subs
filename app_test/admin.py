from django.contrib import admin
from .models import Category_maladie, Patient, Doctor
# Register your models here.


admin.site.register(Category_maladie)
admin.site.register(Patient)
admin.site.register(Doctor)