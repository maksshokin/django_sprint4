from django.shortcuts import get_object_or_404
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.edit import ModelFormMixin, ProcessFormView

from .models import Post


class CreateUpdateView(
    SingleObjectTemplateResponseMixin,
    ModelFormMixin,
    ProcessFormView
):


    def get_object(self, queryset=None):
        pk = self.kwargs.get("pk")
        if pk is not None:
            return get_object_or_404(Post, pk=pk)
        return None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(CreateUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(CreateUpdateView, self).post(request, *args, **kwargs)