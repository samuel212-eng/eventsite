# Register our models with the admin panel
# Visit /admin to manage everything through a GUI

from django.contrib import admin
from .models import Event, Category, Registration

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display  = ['title', 'organizer', 'date', 'location', 'capacity', 'is_published']
    list_filter   = ['is_published', 'category', 'date']
    search_fields = ['title', 'description', 'location']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'registered_at']
