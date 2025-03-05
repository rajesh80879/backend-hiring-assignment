from django.urls import path
from .views import (
    ProjectDetailView,
    ProjectListView,
    TaskDetailView,
    TaskListView,
    client_list,
    client_create,
    project_delete,
    project_list,
    project_create,
    project_detail,
    task_delete,
    task_edit,
    task_list,
    task_create,
    CustomLoginView,
    CustomLogoutView,
)

urlpatterns = [
    # Authentication
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    # Client URLs (Company)
    path("clients/", client_list, name="client_list"),
    path("clients/create/", client_create, name="client_create"),
    # Project URLs
    path("projects/", project_list, name="project_list"),
    path("projects/create/", project_create, name="project_create"),
    path("projects/<uuid:project_id>/", project_detail, name="project_detail"),
    path("projects/delete/<uuid:project_id>/", project_delete, name="project_delete"),
    # Task URLs
    path("tasks/", task_list, name="task_list"),
    path("tasks/create/", task_create, name="task_create"),
    path("tasks/edit/<uuid:pk>/", task_edit, name="task_edit"),
    path("tasks/delete/<uuid:pk>/", task_delete, name="task_delete"),
    # API Endpoints
    path("api/projects/", ProjectListView.as_view(), name="project-list"),
    path("api/projects/<uuid:pk>/", ProjectDetailView.as_view(), name="project-detail"),
    path("api/tasks/", TaskListView.as_view(), name="task-list"),
    path("api/tasks/<uuid:pk>/", TaskDetailView.as_view(), name="task-detail"),
]
