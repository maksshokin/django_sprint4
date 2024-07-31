from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect

from blog.models import Comment, Post
from blog.forms import CommentForm
from blog.constants import INDEX, PAGINATE, POST_DETAIL_URL

from django.core.exceptions import PermissionDenied


class PostFieldsMixin:

    model = Post
    template_name = "blog/create.html"
    success_url = INDEX


class PostEditDispatchMixin:

    def dispatch(self, request, *args, **kwargs):
        if "edit/" in self.request.path:
            post_to_edit = get_object_or_404(Post, id=kwargs["pk"])
            if request.user.id != post_to_edit.author.id:
                return redirect(POST_DETAIL_URL, pk=post_to_edit.pk)
        if "delete/" in self.request.path:
            return self.check_if_user_is_author(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def check_if_user_is_author(self, request, *args, **kwargs):
        post_to_delete = get_object_or_404(Post, id=kwargs["pk"])
        if request.user.id != post_to_delete.author.id:
            return redirect(POST_DETAIL_URL, pk=post_to_delete.pk)
        return super().dispatch(request, *args, **kwargs)


class CommentMixin:
    model = Comment
    template_name = "blog/comment.html"
    form_class = CommentForm

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


class ListingMixin:

    model = Post
    ordering = "-pub_date"
    paginate_by = PAGINATE
