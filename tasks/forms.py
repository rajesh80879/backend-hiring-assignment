from django import forms
from .models import Project, Task, Client


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["name"]


class ProjectForm(forms.ModelForm):
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), required=False
    )

    class Meta:
        model = Project
        fields = ["name", "description", "client", "end_date"]


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["name", "description", "project", "status"]
