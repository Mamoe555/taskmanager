from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .models import Project, Task
from .forms import ProjectForm, TaskForm

def get_user_flags(user):
    """
    Return simple boolean flags for templates.
    Treat superusers and staff as admins automatically.
    """
    if not user or not user.is_authenticated:
        return {'is_admin': False, 'is_manager': False}

    is_admin = user.is_superuser or user.is_staff or user.groups.filter(name='Admin').exists()
    is_manager = user.groups.filter(name='Manager').exists()

    return {'is_admin': is_admin, 'is_manager': is_manager}


def user_login(request):
    """
    Single page login view with two submit buttons:
      - name="action" value="login"    -> normal login
      - name="action" value="admin"    -> login as admin (requires staff or Admin group)
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        action = request.POST.get('action', 'login')  # 'login' or 'admin'
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is None:
                messages.error(request, "Invalid username or password.")
                return render(request, 'login.html', {'form': form})
            # If the user clicked the Admin button, enforce admin/staff check
            if action == 'admin':
                is_admin = user.is_staff or user.is_superuser or user.groups.filter(name='Admin').exists()
                if not is_admin:
                    messages.error(request, "You are not allowed to login as admin.")
                    return render(request, 'login.html', {'form': form})
            # All good: log the user in
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            # invalid form (missing fields, etc.)
            messages.error(request, "Please correct the errors below.")
            return render(request, 'login.html', {'form': form})
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def register(request):
    """
    Basic registration using Django's UserCreationForm.
    Automatically logs new users in. (You can add group assignment here if desired.)
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Optionally add user to default 'User' group:
            # g, created = Group.objects.get_or_create(name='User')
            # g.user_set.add(user)
            auth_login(request, user)
            messages.success(request, "Account created and logged in.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please fix the errors in the form.")
    else:
        form = UserCreationForm()

    ctx = get_user_flags(request.user)
    ctx.update({'form': form})
    return render(request, 'register.html', ctx)


@login_required
def dashboard(request):
    """
    Show projects depending on role:
     - Admin: all projects
     - Manager: projects they manage
     - User: projects that have tasks assigned to them
    Also build a mapping project.id -> tasks (for template convenience)
    """
    flags = get_user_flags(request.user)
    is_admin = flags['is_admin']
    is_manager = flags['is_manager']
    user = request.user

    if is_admin:
        projects = Project.objects.all().order_by('-created_at')
    elif is_manager:
        # Use manager FK (works whether or not related_name is set)
        projects = Project.objects.filter(manager=user).order_by('-created_at')
    else:
        projects = Project.objects.filter(tasks__assigned_to=user).distinct().order_by('-created_at')

    # Build a simple mapping of project.id -> task queryset for quick lookup in template
    project_tasks = {project.id: project.tasks.all() for project in projects}

    ctx = {
        'projects': projects,
        'project_tasks': project_tasks,
        **flags,
    }
    return render(request, 'dashboard.html', ctx)


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    tasks = project.tasks.all()
    ctx = get_user_flags(request.user)
    ctx.update({'project': project, 'tasks': tasks})
    return render(request, 'project_detail.html', ctx)


@login_required
def create_project(request):
    """
    Only Admins or Managers can create projects.
    """
    flags = get_user_flags(request.user)
    if not (flags['is_admin'] or flags['is_manager']):
        messages.error(request, "You don't have permission to create a project.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, "Project created.")
            return redirect('project_detail', pk=project.pk)
        else:
            messages.error(request, "Please fix the errors in the form.")
    else:
        # If manager creates a project, it's convenient to prefill manager
        initial = {'manager': request.user} if flags['is_manager'] else None
        form = ProjectForm(initial=initial)

    ctx = {'form': form, **flags}
    return render(request, 'create_project.html', ctx)


@login_required
def create_task(request, pk):
    """
    Add a task to a project. Only Admins or Managers allowed.
    """
    project = get_object_or_404(Project, pk=pk)
    flags = get_user_flags(request.user)
    if not (flags['is_admin'] or flags['is_manager']):
        messages.error(request, "You don't have permission to add a task.")
        return redirect('project_detail', pk=project.pk)

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            messages.success(request, "Task created.")
            return redirect('project_detail', pk=project.pk)
        else:
            messages.error(request, "Please fix the errors in the form.")
    else:
        form = TaskForm()

    ctx = {'form': form, 'project': project, **flags}
    return render(request, 'create_task.html', ctx)
