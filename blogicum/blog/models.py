from django.db import models


from django.contrib.auth import get_user_model
from django.urls import reverse

from .constants import RESTRICTION

User = get_user_model()



class PublishedModel(models.Model):
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text=(
            'Снимите галочку, чтобы скрыть публикацию.'
        )
    )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True
    )

    class Meta:
        abstract = True


class Category(PublishedModel):
    title = models.CharField('Заголовок', max_length=256)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text=(
            'Идентификатор страницы для URL; разрешены '
            'символы латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta(PublishedModel.Meta):
        verbose_name_plural = 'Категории'
        verbose_name = 'категория'

    def __str__(self):
        return self.title[:RESTRICTION]


class Location(PublishedModel):
    name = models.CharField('Название места', max_length=256)

    def __str__(self):
        return self.name[:RESTRICTION]

    class Meta(PublishedModel.Meta):
        verbose_name_plural = 'Местоположения'
        verbose_name = 'местоположение'


class Post(PublishedModel):
    title = models.CharField('Заголовок', max_length=256)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем '
            '— можно делать отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    image = models.ImageField(verbose_name='Картинка у публикации', blank=True)
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )

    class Meta(PublishedModel.Meta):
        verbose_name_plural = 'Публикации'
        verbose_name = 'публикация'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=(self.pk,))


class Comment(PublishedModel):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
        related_name='comments',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Комментируемый пост',
        related_name='comments',
    )
    text = models.TextField(verbose_name='Текст комментария')

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарий'
        ordering = ('created_at',)

    def __str__(self):
        return self.text[:RESTRICTION]
