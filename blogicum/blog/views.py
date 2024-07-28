from django.contrib.auth import get_user_model

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from blog.models import Category, Comment, Post

from .forms import CommentForm, PostForm
from .utils import CreateUpdateView

User = get_user_model()

# Имена URL
INDEX_URL = "blog:index"
PROFILE_URL = "blog:profile"
POST_DETAIL_URL = "blog:post_detail"

# Константы URL
INDEX = reverse_lazy(INDEX_URL)
PROFILE = reverse_lazy(PROFILE_URL)
POST_DETAIL = reverse_lazy(POST_DETAIL_URL)


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


class PostCreateEditView(
    LoginRequiredMixin, PostFieldsMixin, CreateUpdateView
):

    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        return reverse(PROFILE_URL, args=[self.request.user.username])

    def dispatch(self, request, *args, **kwargs):
        if "edit/" in self.request.path:
            post_to_edit = get_object_or_404(Post, id=kwargs["pk"])
            if request.user.id != post_to_edit.author.id:
                return redirect("blog:post_detail", pk=post_to_edit.pk)
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, PostFieldsMixin, DeleteView):

    def dispatch(self, request, *args, **kwargs):
        return self.check_if_user_is_author(request, *args, **kwargs)


class ListingMixin:

    model = Post
    ordering = "-pub_date"
    paginate_by = 10


class PostListView(ListingMixin, ListView):

    template_name = "blog/index.html"
    queryset = (
        Post.objects.select_related("location", "author", "category")
        .exclude(pub_date__gt=timezone.now())
        .filter(is_published=True, category__is_published=True)
        .annotate(comment_count=Count("comments"))
    )


class CategoryListView(ListingMixin, ListView):

    template_name = "blog/category.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        category = get_object_or_404(
            Category, slug=self.kwargs["category_slug"], is_published=True
        )
        return (
            queryset.select_related("category")
            .exclude(pub_date__gt=timezone.now())
            .filter(category=category, is_published=True)
            .annotate(comment_count=Count("comments"))
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = get_object_or_404(
            Category, slug=self.kwargs["category_slug"], is_published=True
        )
        return context


class UserProfileView(ListingMixin, ListView):

    template_name = "blog/profile.html"
    queryset = Post.objects.select_related("author").annotate(
        comment_count=Count("comments")
    )

    def get_queryset(self):
        author = get_object_or_404(User, username=self.kwargs["username"])
        queryset = super().get_queryset().filter(author=author)
        if author.id != self.request.user.id:
            queryset = queryset.filter(
                is_published=True, category__is_published=True
            ).exclude(pub_date__gt=timezone.now())
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        author_id = get_object_or_404(
            User, username=self.kwargs["username"]
        ).id
        context["profile"] = get_object_or_404(User, id=author_id)
        return context


class UserEditProfileView(LoginRequiredMixin, UpdateView):
    """Не смог самостоятельно решить проблему:
    при заход на страницу профиля выдает ошибку
    NoReverseMatch at....
    Но при по ссылке edit_profile/<pk> все работает
    """
    model = User
    template_name = "blog/user.html"
    fields = ["first_name", "last_name", "username", "email"]

    def get_queryset(self):
        return super().get_queryset().filter(id=self.kwargs["pk"])

    def get_success_url(self, *args, **kwargs):
        username = get_object_or_404(User, id=self.kwargs["pk"]).username
        return reverse_lazy(PROFILE_URL, args=[username])


class PostDetailView(DetailView):

    model = Post
    template_name = "blog/detail.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        author = get_object_or_404(Post, id=self.kwargs["pk"]).author
        if self.request.user.id != author.id:
            queryset = queryset.filter(
                is_published=True, category__is_published=True
            ).exclude(pub_date__gt=timezone.now())
        return queryset

    def dispatch(self, request, *args, **kwargs):
        if not self.get_object():
            raise Http404("Такого поста не существует.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["comments"] = self.object.comments.select_related("post")
        return context


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


class CommentCreateView(LoginRequiredMixin, CommentMixin, CreateView):
    def get_success_url(self):
        return reverse(INDEX_URL)


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView):

    def get_success_url(self):
        post = get_object_or_404(Post, id=self.kwargs["post_id"])
        return reverse(POST_DETAIL_URL, kwargs={"pk": post.pk})


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):

    def get_success_url(self):
        post = get_object_or_404(Post, id=self.kwargs["post_id"])
        return reverse(POST_DETAIL_URL, kwargs={"pk": post.pk})
