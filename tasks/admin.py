# tasks/admin.py
from django.contrib import admin
from .models import Project, Task

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager', 'created_at')
    list_filter = ('manager',)
    search_fields = ('name', 'manager__username')
    ordering = ('-created_at',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assigned_to', 'status', 'due_date', 'created_at')
    list_filter = ('status', 'project', 'assigned_to')
    search_fields = ('title', 'project__name', 'assigned_to__username')
    ordering = ('-created_at',)
