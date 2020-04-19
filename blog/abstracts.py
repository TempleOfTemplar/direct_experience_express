import datetime

from django.db import models

from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, InlinePanel, PageChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.core.fields import RichTextField
from modelcluster.contrib.taggit import ClusterTaggableManager

from colorful.fields import RGBColorField

from .utils import get_image_model_path


class BlogAbstract(models.Model):
    description = models.CharField(
        verbose_name='Описание',
        max_length=255,
        blank=True,
        help_text="Описание появится под заголовком."
    )
    header_image = models.ForeignKey(
        get_image_model_path(),
        verbose_name='Изображение в шапке',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    main_color = RGBColorField('Основной цвет', default="#4D6AE0")

    display_comments = models.BooleanField(default=False, verbose_name='Отображать комментарии')
    display_categories = models.BooleanField(default=True, verbose_name='Отображать категории')
    display_tags = models.BooleanField(default=True, verbose_name='Отображать теги')
    display_popular_entries = models.BooleanField(default=True, verbose_name='Отображать популярные статьи')
    display_last_entries = models.BooleanField(default=True, verbose_name='Отображать новые статьи')
    display_archive = models.BooleanField(default=True, verbose_name='Отображать архив')

    disqus_api_secret = models.TextField(blank=True)
    disqus_shortname = models.CharField(max_length=128, blank=True)

    num_entries_page = models.IntegerField(default=5, verbose_name='Статей на странице')
    num_last_entries = models.IntegerField(default=3, verbose_name='Новых статей на странице')
    num_popular_entries = models.IntegerField(default=3, verbose_name='Популярных статей на странице')
    num_tags_entry_header = models.IntegerField(default=5, verbose_name='Максимум тегов в заголовке')

    short_feed_description = models.BooleanField(default=True, verbose_name='Используйте короткое описание в лентах')

    content_panels = [
        FieldPanel('description', classname="full"),
        ImageChooserPanel('header_image'),
        FieldPanel('main_color')
    ]
    settings_panels = [
        MultiFieldPanel([
            FieldPanel('display_categories'),
            FieldPanel('display_tags'),
            FieldPanel('display_popular_entries'),
            FieldPanel('display_last_entries'),
            FieldPanel('display_archive'),
        ], heading="Виджеты"),
        MultiFieldPanel([
            FieldPanel('num_entries_page'),
            FieldPanel('num_last_entries'),
            FieldPanel('num_popular_entries'),
            FieldPanel('num_tags_entry_header'),
        ], heading="Параметры"),
        MultiFieldPanel([
            FieldPanel('display_comments'),
            FieldPanel('disqus_api_secret'),
            FieldPanel('disqus_shortname'),
        ], heading="Комментарии"),
        MultiFieldPanel([
            FieldPanel('short_feed_description'),
        ], heading="Рассылки"),
    ]

    class Meta:
        abstract = True


class EntryAbstract(models.Model):
    body = RichTextField(verbose_name='тело')
    tags = ClusterTaggableManager(through='blog.TagEntryPage', blank=True)
    date = models.DateTimeField(verbose_name="Дата добавления", default=datetime.datetime.today)
    header_image = models.ForeignKey(
        get_image_model_path(),
        verbose_name='Изображение в шапке',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    categories = models.ManyToManyField('blog.Category', through='blog.CategoryEntryPage', blank=True)
    excerpt = RichTextField(
        verbose_name='резюме',
        blank=True,
        help_text="Резюме отображается в списке статей. "
                    "Если это поле не заполнено, будет использован отрывок из текста статьи."
    )
    num_comments = models.IntegerField(default=0, editable=False)

    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel('title', classname="title"),
                ImageChooserPanel('header_image'),
                FieldPanel('body', classname="full"),
                FieldPanel('excerpt', classname="full"),
            ],
            heading="Контент"
        ),
        MultiFieldPanel(
            [
                FieldPanel('tags'),
                InlinePanel('entry_categories', label="Категории"),
                InlinePanel(
                    'related_entrypage_from',
                    label="Связанные статьи",
                    panels=[PageChooserPanel('entrypage_to')]
                ),
            ],
            heading="Метаданные"),
    ]

    class Meta:
        abstract = True
