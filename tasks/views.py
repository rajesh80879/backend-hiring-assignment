import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.db.models import Prefetch

from .models import Project, Task, Client
from .forms import ClientForm, ProjectForm, TaskForm
from .serializers import ProjectSerializer, TaskSerializer

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

# Configure loggers
error_logger = logging.getLogger("error_logger")
success_logger = logging.getLogger("success_logger")


# ---------------- Authentication Views ----------------
class CustomLoginView(LoginView):
    template_name = "tasks/login.html"


class CustomLogoutView(LogoutView):
    next_page = "/login/"


# ---------------- Redirect to Login ----------------
def redirect_to_login(request):
    return redirect("login")


# ---------------- Client Views ----------------
@login_required
def client_list(request):
    try:
        clients = Client.objects.all()
        return render(request, "tasks/client_list.html", {"clients": clients})
    except Exception as e:
        error_logger.error(f"Error fetching client list: {str(e)}")
        messages.error(request, "Error fetching clients.")
        return redirect("client_list")


@login_required
def client_create(request):
    if request.method == "POST":
        try:
            form = ClientForm(request.POST)
            if form.is_valid():
                form.save()
                success_logger.info("Client added successfully!")
                messages.success(request, "Client added successfully!")
            else:
                messages.error(request, "Failed to add client. Please check the form.")
        except Exception as e:
            error_logger.error(f"Error creating client: {str(e)}")
            messages.error(request, "An error occurred while adding the client.")
    return redirect("client_list")


# ---------------- Project Views ----------------
@login_required
def project_list(request):
    try:
        projects = Project.objects.filter(
            completed=False, is_deleted=False
        ).prefetch_related(
            Prefetch("tasks", queryset=Task.objects.filter(is_deleted=False))
        )
        clients = Client.objects.all()
        return render(
            request,
            "tasks/project_list.html",
            {"projects": projects, "clients": clients},
        )
    except Exception as e:
        error_logger.error(f"Error fetching project list: {str(e)}")
        messages.error(request, "Error fetching projects.")
        return redirect("project_list")


@login_required
def project_create(request):
    """Add a Project"""
    if request.method == "POST":
        try:
            form = ProjectForm(request.POST)
            if form.is_valid():
                form.save()
                success_logger.info("Project added successfully!")
                messages.success(request, "Project added successfully!")
            else:
                messages.error(request, "Failed to add Project. Please check the form.")
        except Exception as e:
            error_logger.error(f"Error creating project: {str(e)}")
            messages.error(request, "An error occurred while adding the project.")
    return redirect("project_list")


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = project.tasks.all()
    return render(
        request, "tasks/project_detail.html", {"project": project, "tasks": tasks}
    )


@login_required
def project_delete(request, project_id):
    """Soft delete a Project"""
    if request.method == "POST":
        try:
            project = get_object_or_404(Project, id=project_id, is_deleted=False)
            related_tasks = Task.objects.filter(project=project)
            if related_tasks.exists():
                related_tasks.update(is_deleted=True)
            project.is_deleted = True
            project.save()
            success_logger.info("Project and associated tasks deleted successfully!")
            messages.success(request, "Project deleted successfully!")
        except Exception as e:
            error_logger.error(f"Error deleting project: {str(e)}")
            messages.error(request, "Failed to delete Project.")
    return redirect("project_list")


# ---------------- Task Views ----------------
def task_list(request):
    """View to display all tasks"""
    tasks = Task.objects.filter(is_deleted=False)  # Only show non-deleted tasks
    projects = Project.objects.filter(
        is_deleted=False,
        completed=False,
    )
    return render(request, "task_list.html", {"tasks": tasks, "projects": projects})


def task_create(request):
    if request.method == "POST":
        try:
            print("Received POST request:", request.POST)
            form = TaskForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Task Created successfully!")
                return redirect("task_list")
            else:
                messages.error(request, "Failed to add Project. Please check the form.")
                return redirect("task_list")
        except Exception as e:
            messages.error(request, f"{e=}")
            return redirect("task_list")
    return redirect("task_list")


def task_edit(request, pk):
    """View to edit a task via modal"""
    task = get_object_or_404(Task, id=pk)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task Updated successfully!")
            return redirect("task_list")
    else:
        messages.error(request, "Failed to update Project. Please check the form.")
        return redirect("task_list")


def task_delete(request, pk):
    """Soft delete a task"""
    task = get_object_or_404(Task, id=pk)
    task.is_deleted = True
    task.save()
    messages.success(request, "Task deleted successfully!")
    return redirect("task_list")


# ---------------- REST API Views ----------------


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = "page_size"
    max_page_size = 100


class ProjectListView(APIView):
    def get(self, request):
        try:
            projects = Project.objects.filter(is_deleted=False)
            paginator = StandardResultsSetPagination()
            result_page = paginator.paginate_queryset(projects, request)
            serializer = ProjectSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProjectDetailView(APIView):
    def get(self, request, pk):
        try:
            project = get_object_or_404(Project, pk=pk, is_deleted=False)
            serializer = ProjectSerializer(project)
            tasks = Task.objects.filter(project=project, is_deleted=False)
            task_serializer = TaskSerializer(tasks, many=True)
            return Response({"project": serializer.data, "tasks": task_serializer.data})
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, pk):
        try:
            project = get_object_or_404(Project, pk=pk, is_deleted=False)
            tasks = Task.objects.filter(project=project)
            tasks.update(is_deleted=True)
            project.is_deleted = True
            project.save()
            return Response(
                {"message": "Project deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TaskListView(APIView):
    def get(self, request):
        try:
            tasks = Task.objects.filter(is_deleted=False)
            paginator = StandardResultsSetPagination()
            result_page = paginator.paginate_queryset(tasks, request)
            serializer = TaskSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TaskDetailView(APIView):
    def get(self, request, pk):
        try:
            task = get_object_or_404(Task, pk=pk, is_deleted=False)
            serializer = TaskSerializer(task)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, pk):
        try:
            task = get_object_or_404(Task, pk=pk, is_deleted=False)
            task.is_deleted = True
            task.save()
            return Response(
                {"message": "Task deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
