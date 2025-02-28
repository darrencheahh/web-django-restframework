from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Module, Professor

admin.site.register(Module)
admin.site.register(Professor)