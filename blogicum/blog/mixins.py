from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

from blog.constants import INDEX, PAGINATE, POST_DETAIL_URL
from blog.forms import CommentForm
from blog.models import Comment, Post


class PostFieldsMixin:

    model = Post
    template_name = "blog/create.html"
    success_url = INDEX


class PostEditDispatchMixin:

    def dispatch(self, request, *args, **kwargs):
        if "edit/" or "delete/" in self.request.path:
            return self.check_if_user_is_author(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def check_if_user_is_author(self, request, *args, **kwargs):
        post = self.get_object()
        if post is not None:
            if request.user.id != post.author.id:
                return redirect(POST_DETAIL_URL, pk=post.pk)
        return super().dispatch(request, *args, **kwargs)


class CommentMixin:
    model = Comment
    template_name = "blog/comment.html"
    form_class = CommentForm

    def form_invalid(self, form):
        return HttpResponseRedirect(self.get_success_url())

    def dispatch(self, request, *args, **kwargs):
        if "/comment/" not in self.request.path:
            comment_to_change = self.get_object()
            if request.user.id != comment_to_change.author.id:
                raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class ListingMixin:

    model = Post
    ordering = "-pub_date"
    paginate_by = PAGINATE
