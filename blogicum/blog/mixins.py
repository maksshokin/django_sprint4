from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect

from blog.models import Comment, Post
from .forms import CommentForm
from .constants import INDEX, POST_DETAIL_URL

from django.core.exceptions import PermissionDenied


class PostFieldsMixin:

    model = Post
    template_name = "blog/create.html"
    success_url = INDEX

    def check_if_user_is_author(self, request, *args, **kwargs):
        """Проверяет, является ли текущий пользователь автором
        поста.
        """
        post_to_delete = get_object_or_404(Post, id=kwargs["pk"])
        if request.user.id != post_to_delete.author.id:
            return redirect(POST_DETAIL_URL, pk=post_to_delete.pk)
        else:
            return super().dispatch(request, *args, **kwargs)


class CommentMixin:
    model = Comment
    template_name = "blog/comment.html"
    form_class = CommentForm

    def form_valid(self, form):
        if "delete/" not in self.request.path:
            post = get_object_or_404(
                Post, id=self.kwargs.get("post_id") or self.kwargs["pk"]
            )
            form.instance.author = self.request.user
            form.instance.post = post
        return super().form_valid(form)

    def form_invalid(self, form):
        return HttpResponseRedirect(self.get_success_url())

    def dispatch(self, request, *args, **kwargs):
        if "/comment/" not in self.request.path:
            comment_to_change = get_object_or_404(
                Comment, id=self.kwargs["pk"]
            )
            if request.user.id != comment_to_change.author.id:
                raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
