import uuid
from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Client(BaseModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Project(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="projects"
    )
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Task(BaseModel):
    STATUS_CHOICES = [
        ("TODO", "To Do"),
        ("WIP", "Work in Progress"),
        ("ONHOLD", "On Hold"),
        ("DONE", "Done"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="TODO")

    def __str__(self):
        return self.name
