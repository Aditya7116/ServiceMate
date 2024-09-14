from django.contrib import admin
from .models import Service

# Register your models here.
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image')
    search_fields = ('name', 'description')
    list_per_page = 10