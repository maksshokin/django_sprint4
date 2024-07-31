from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from blog.models import Category, Post, User
from blog.mixins import (
    CommentMixin,
    ListingMixin,
    PostEditDispatchMixin,
    PostFieldsMixin
)
from blog.forms import CommentForm, PostForm, UserEditForm
from blog.utils import CreateUpdateView
from blog.constants import (
    POST_DETAIL_URL,
    PROFILE_URL
)


class PostCreateEditView(
    LoginRequiredMixin,
    PostFieldsMixin,
    PostEditDispatchMixin,
    CreateUpdateView
):
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        return reverse(PROFILE_URL, args=[self.request.user.username])


class PostDeleteView(
    LoginRequiredMixin,
    PostFieldsMixin,
    PostEditDispatchMixin,
    DeleteView
):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostForm(instance=self.object)
        return context


class PostListView(ListingMixin, ListView):

    template_name = "blog/index.html"
    queryset = (
        Post.objects.select_related("location", "author", "category")
        .filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        ).annotate(comment_count=Count("comments"))
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
            .filter(
                pub_date__lte=timezone.now(),
                category=category,
                is_published=True
            )
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

    def get_queryset(self):
        author = get_object_or_404(User, username=self.kwargs["username"])
        queryset = super().get_queryset().filter(author=author).annotate(
            comment_count=Count('comments')
        )
        if author.id != self.request.user.id:
            queryset = queryset.filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            )
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = get_object_or_404(
            User,
            username=self.kwargs["username"]
        )
        return context


class UserEditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "blog/user.html"
    form_class = UserEditForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username})


class PostDetailView(DetailView):

    model = Post
    template_name = "blog/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm(instance=self.object)
        context['comments'] = (
            self.object.comments.all().select_related('author')
        )
        return context

    def get_object(self, queryset=None):
        post = super().get_object(queryset=queryset)
        if (
            post.author != self.request.user
            and (
                not post.is_published
                or not post.category.is_published
                or post.pub_date > timezone.now()
            )
        ):
            raise Http404()
        return post


class CommentCreateView(LoginRequiredMixin, CommentMixin, CreateView):
    def form_valid(self, form):
        post = get_object_or_404(
            Post, id=self.kwargs.get("post_id") or self.kwargs["pk"]
        )
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(POST_DETAIL_URL, kwargs=self.kwargs)


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView):
    def get_success_url(self):
        post = get_object_or_404(Post, id=self.kwargs["post_id"])
        return reverse(POST_DETAIL_URL, kwargs={"pk": post.pk})


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):
    def get_success_url(self):
        post = get_object_or_404(Post, id=self.kwargs["post_id"])
        return reverse(POST_DETAIL_URL, kwargs={"pk": post.pk})
