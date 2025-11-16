from django import forms
from .models import Project, Task

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        # keep fields minimal to avoid unknown-field errors
        fields = ['name', 'description', 'manager']  # manager should be FK to User

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        # include safe/common fields only
        fields = ['title', 'description', 'assigned_to']
