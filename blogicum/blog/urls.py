from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:id>/', views.post_detail, name='post_detail'),
    path('category/<slug:slug>/',
         views.category_posts,
         name='category_posts'
         ),
    path('post/create/', views.post_create, name ='create_post'),
    path(
        'post/<int:id>/edit/',
        views.EditPostView.as_view(),
        name='edit_post',
    ),
    path(
        'post/<int:id>/delete/',
        views.DeletePostView.as_view(),
        name='delete_post',
    ),
    
]
