from django.template.response import TemplateResponse
from sse.events.models import Task


def home(request, *args, **kwargs):
    return TemplateResponse(request, "home.html", {"tasks": Task.objects.all()})
