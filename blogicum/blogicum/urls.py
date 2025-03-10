from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.urls import include, path, reverse_lazy
from django.views.generic import CreateView

urlpatterns: list = [
    path(
        "auth/registration/",
        CreateView.as_view(
            form_class=UserCreationForm,
            success_url=reverse_lazy("auth:login"),
            template_name="registration/registration_form.html",
        ),
        name="registration",
    ),
    path("auth/", include("django.contrib.auth.urls")),
    path("pages/", include("pages.urls", namespace="pages")),
    path("admin/", admin.site.urls),
    path("", include("blog.urls", namespace="blog")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

handler403 = 'pages.views.csrf_failure'
handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'
