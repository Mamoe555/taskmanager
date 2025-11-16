# tasks/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects'
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

STATUS_CHOICES = [
    ('todo', 'To Do'),
    ('in_progress', 'In Progress'),
    ('done', 'Done'),
]

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
