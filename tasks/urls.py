from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Custom login view (single page with both buttons)
    path('login/', views.user_login, name='login'),

    # Keep built-in logout
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),

    path('projects/create/', views.create_project, name='create_project'),
    path('project/<int:pk>/', views.project_detail, name='project_detail'),
    path('project/<int:pk>/tasks/create/', views.create_task, name='create_task'),
]
