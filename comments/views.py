from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.template.loader import render_to_string
from django.http import JsonResponse

from comments.models import Comment
from notifications.models import Notification
from salarium.enums import NotificationsType, NotificationsStatus
from salarium.utils import get_page_data, page_render, staff_only


def create_comment(request):
    if request.method == 'POST' and len(request.POST.get('comment_body', '')) > 0:
        if 'pk' not in request.POST:
            new_comment = Comment.save_comment(request.POST.get('post_pk'), **{
                'body': request.POST.get('comment_body', ''),
                'author': request.user,
                'status': 'Pending',
                'name': request.POST.get('name', request.user.username if request.user.is_authenticated else ''),
                'email': request.POST.get('email', request.user.email if request.user.is_authenticated else ''),
            })
            Notification.create_notification(**{'type': NotificationsType.CommentAdded.value,
                                                'entity_pk': new_comment.pk})
        else:
            Comment.update_comment(request.POST.get('pk'), **{
                'body': request.POST.get('comment_body', ''),
                'author': request.user,
                'status': 'Pending'
            })
            notification = Notification.objects.filter(entity_pk=int(request.POST.get('pk')),
                                                       type=NotificationsType.CommentAdded.value).first()
            if notification is None:
                Notification.create_notification(**{'type': NotificationsType.CommentUpdated.value,
                                                    'entity_pk': int(request.POST.get('pk'))})
            else:
                notification.update_notification(**{'type': NotificationsType.CommentUpdated.value})
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# --------- ADMIN PANEL FUNCTIONALITY
@staff_only
def get_all_comments(request, active_type=None):
    request.session['admin_new_comments_page'] = 0
    request.session['admin_viewed_comments_page'] = 0
    request.session['admin_updated_comments_page'] = 0

    active_types = {}
    if active_type is None:
        active_types['new'] = 'active'
    else:
        active_types[active_type] = 'active'

    updated_comments, has_more_updated = get_updated_comments(request)
    viewed_comments, has_more_viewed = get_viewed_comments(request)
    new_comments, has_more_new = get_new_comments(request)
    return page_render(request, 'admin_panel/main_page_admin_panel.html',
                        {'comments_page': 'active',
                         'current_content_page': 'admin_panel/comments/all_comments.html',
                         'updated_comments': updated_comments,
                         'has_more_updated': has_more_updated,
                         'viewed_comments': viewed_comments,
                         'has_more_viewed': has_more_viewed,
                         'new_comments': new_comments,
                         'has_more_new': has_more_new,
                         'active_types': active_types})


@staff_only
def get_comments(request, comments_ids=None, comments_type='new'):
    if comments_ids is None:
        comments_ids = []

    request.session['admin_' + comments_type + '_comments_page'] += 1

    comments_page, comments, number_comment_pages = get_page_data(
        Comment.objects.filter(pk__in=comments_ids).order_by('-date_of_creation'),
        request.session['admin_'+comments_type+'_comments_page'])
    return comments, number_comment_pages > comments_page + 1


@staff_only
def get_new_comments(request):
    new_comments_ids = [int(item) for item in Notification.objects.filter(type=NotificationsType.CommentAdded.value, status=NotificationsStatus.Actual.value).values_list('entity_pk', flat=True)]
    return get_comments(request, new_comments_ids, 'new')


@staff_only
def get_viewed_comments(request):
    viewed_comments_ids = [int(item) for item in Notification.objects.filter(type__in=[NotificationsType.CommentAdded.value, NotificationsType.CommentUpdated.value], status=NotificationsStatus.Viewed.value).values_list('entity_pk', flat=True)]
    return get_comments(request, viewed_comments_ids, 'viewed')


@staff_only
def get_updated_comments(request):
    updated_comments_ids = [int(item) for item in Notification.objects.filter(type=NotificationsType.CommentUpdated.value, status=NotificationsStatus.Actual.value).values_list('entity_pk', flat=True)]
    return get_comments(request, updated_comments_ids, 'updated')


comments_handler_map = {
    'new': get_new_comments,
    'updated': get_updated_comments,
    'viewed': get_viewed_comments
}


@staff_only
def get_more_comments(request, comments_type):
    comments, has_more = comments_handler_map[comments_type](request)
    return JsonResponse({'data': render_to_string('admin_panel/comments/rendered_comments.html', {'comments': comments}, request=request),
                         'last': not has_more})

@staff_only
def mark_as_moderated(request, pk):
    notification = Notification.objects.filter(status=NotificationsStatus.Actual.value, entity_pk=pk).first()
    notification.update_notification(**{'status': NotificationsStatus.Viewed.value})
    return JsonResponse({'message': 'done'})


@staff_only
def moderate_comment(request, pk):
    Comment.objects.filter(pk=pk).update(**{'body': request.POST.get('comment_body')})

    notification = Notification.objects.filter(status=NotificationsStatus.Actual.value, entity_pk=pk).first()
    if notification:
        notification.update_notification(**{'status': NotificationsStatus.Viewed.value})

    return JsonResponse({'message': 'done'})


@staff_only
def delete_comment(request, pk):
    Comment.objects.filter(pk=pk).delete()
    Notification.objects.filter(status=NotificationsStatus.Actual.value, entity_pk=pk).delete()
    return JsonResponse({'message': 'done'})


