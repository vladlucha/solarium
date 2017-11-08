from categories.models import Category
from salarium.enums import EntityStatus
from salarium.utils import staff_only, get_page_number

from posts.models import Post
from django.shortcuts import redirect
from media_library.models import Media

# Create your views here.
from salarium.utils import page_render, set_request_session_alert, get_page_data


@staff_only
def all_posts(request, page_number):
    page_number = get_page_number(page_number)
    post_page, posts, number_post_pages = get_page_data(Post.objects.order_by('-pk').all(), page_number, 12)
    context = {'posts_is_active': 'active',
               'current_content_page': 'admin_panel/posts/all_posts.html',
               'posts': posts, 'post_page': post_page, 'number_post_pages': range(1, number_post_pages),
               'different_views': True}
    return page_render(request, 'admin_panel/main_page_admin_panel.html', context)


@staff_only
def create_post(request, post_id):
    post = Post.get_post_by_property(pk=post_id) if post_id is not None and post_id != 'None' else None
    return page_render(request, 'admin_panel/main_page_admin_panel.html',
                       {'posts_is_active': 'active',
                        'current_content_page': 'admin_panel/posts/create_post.html',
                        'post': post,
                        'statuses': EntityStatus.items(),
                        'categories': Category.objects.all()
                        })


@staff_only
def delete_post(request, post_id):
    post = Post.get_post_by_property(pk=post_id)
    if post:
        post.delete()

    alert_message = 'Статья успешно удалена'
    set_request_session_alert(request, alert_message, 'notice')
    return redirect('all_posts')


@staff_only
def create_or_update_post(request):
    if request.method == 'POST':
        if 'pk' not in request.POST:
            Post.save_post(**{'title': request.POST.get('title'),
                              'excerpt': request.POST.get('excerpt'),
                              'body': request.POST.get('body'),
                              'formatted_body': request.POST.get('formatted_body'),
                              'thumbnail': Media.get_media_by_property(pk=request.POST.get('thumbnail')),
                              'tags': request.POST.get('tags'),
                              'status': request.POST.get('status'),
                              'author': request.user})
            alert_message = 'Статья успешно создана ' + ('и опубликована' if request.POST.get('status') == 'Published' else '')
        else:
            Post.update_post(pk=request.POST.get('pk'), **{
                'title': request.POST.get('title'),
                'excerpt': request.POST.get('excerpt'),
                'body': request.POST.get('body'),
                'formatted_body': request.POST.get('formatted_body'),
                'thumbnail': Media.get_media_by_property(pk=request.POST.get('thumbnail')),
                'tags': request.POST.get('tags'),
                'status': request.POST.get('status'),
                'author': request.user
            })
            alert_message = 'Статья успешно обновлена ' + ('и опубликована' if request.POST.get('status') == 'Published' else '')
        set_request_session_alert(request, alert_message, 'notice')
    return redirect('all_posts')
