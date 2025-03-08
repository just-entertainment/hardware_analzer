from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CPU, RAM

admin.site.register(CPU)
admin.site.register(RAM)