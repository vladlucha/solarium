from django.shortcuts import render

from posts.models import Post
# Create your views here.
from salarium.enums import EntityStatus
from salarium.utils import page_render, get_page_data


def posts(request, page=0):
    posts = Post.objects.filter(status=EntityStatus.Published.value)

    blog_page, posts, number_blog_pages = get_page_data(posts.order_by('-pk'), page, 5)

    return page_render(request, 'site/posts.html',
                  {'posts': posts,
                   'blog_page': blog_page,
                   'number_blog_pages': number_blog_pages})


def get_posts_by_page(request, page):
    return posts(request, page=page)


def get_posts_by_category(request, category):
    return posts(request, category=category)


def get_posts_by_tag(request, tag):
    return posts(request, tag=tag)


def get_post(request, post_slug):
    if post_slug is not None:
        post = Post.objects.filter(slug=post_slug).first()
        return page_render(request, 'site/post.html', {'post': post})
