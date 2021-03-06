from django.conf import settings
from django.conf.urls import url
from django.urls import include, reverse
from django.urls import path
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from blog.feeds import BlogPageFeed
from blog.utils import strip_prefix_and_ending_slash
from blog.views import EntryPageUpdateCommentsView, EntryPageServe
from search import views as search_views

urlpatterns = [
    # url(r'^django-admin/', admin.site.urls),
    # path('admin/', admin.site.urls),
    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),

    url(r'^search/$', search_views.search, name='search'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls))
    ]
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# blog urls
urlpatterns = urlpatterns + [
    path(
        route='entry_page/<entry_page_id>/update_comments/',
        view=EntryPageUpdateCommentsView.as_view(),
        name='entry_page_update_comments'
    ),
    path(
        route='<path:blog_path>/<int:year>/<int:month>/<int:day>/<str:slug>/',
        view=EntryPageServe.as_view(),
        name='entry_page_serve_slug'
    ),
    path(
        route='<int:year>/<int:month>/<int:day>/<str:slug>/',
        view=EntryPageServe.as_view(),
        name='entry_page_serve'
    ),
    path(
        route='<path:blog_path>/feed/',
        view=BlogPageFeed(),
        name='blog_page_feed_slug'
    ),
    path(
        route='feed/',
        view=BlogPageFeed(),
        name='blog_page_feed'
    )
]

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    url(r'', include(wagtail_urls)),

    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    url(r"^pages/", include(wagtail_urls)),
]


def get_entry_url(entry, blog_page, root_page):
    """
    Get the entry url given and entry page a blog page instances.
    It will use an url or another depending if blog_page is the root page.
    """
    if root_page == blog_page:
        return reverse('entry_page_serve', kwargs={
            'year': entry.date.strftime('%Y'),
            'month': entry.date.strftime('%m'),
            'day': entry.date.strftime('%d'),
            'slug': entry.slug
        })
    else:
        # The method get_url_parts provides a tuple with a custom URL routing
        # scheme. In the last position it finds the subdomain of the blog, which
        # it is used to construct the entry url.
        # Using the stripped subdomain it allows Puput to generate the urls for
        # every sitemap level
        blog_path = strip_prefix_and_ending_slash(blog_page.specific.last_url_part)
        return reverse('entry_page_serve_slug', kwargs={
            'blog_path': blog_path,
            'year': entry.date.strftime('%Y'),
            'month': entry.date.strftime('%m'),
            'day': entry.date.strftime('%d'),
            'slug': entry.slug
        })


def get_feeds_url(blog_page, root_page):
    """
    Get the feeds urls a blog page instance.
    It will use an url or another depending if blog_page is the root page.
    """
    if root_page == blog_page:
        return reverse('blog_page_feed')
    else:
        blog_path = strip_prefix_and_ending_slash(blog_page.specific.last_url_part)
        return reverse('blog_page_feed_slug', kwargs={'blog_path': blog_path})
