# -*- coding: utf-8 -*-
import json

import vk
import vk_api
from django.db.models import Q

from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from salarium import settings as app_settings
from salarium.utils import staff_only, get_page_number, get_page_data, VK_session
import cloudinary
import cloudinary.uploader
import cloudinary.api
from django.http import JsonResponse
from django.template.loader import render_to_string
from salarium.tasks import import_vk_album_photos

from media_library.models import Media, Album
from salarium.utils import page_render
from settings.models import Settings


def load_more_items(request, page_number):
    return JsonResponse({'images': load_all_media_files_thumbnails(page_number)})


def load_album_images(request, album_pk):
    album = Album.objects.filter(pk=album_pk).first()
    images = []
    if album:
        images = [i.preview_html_tag for i in album.photos.order_by('-pk').all()]
    return JsonResponse({'images': images})


def load_all_media_files_thumbnails(page_number=None):
    page_number = get_page_number(page_number)
    post_page, media, number_post_pages = get_page_data(Media.objects.filter(Q(from_vk=False) | Q(albums__isnull=True)).order_by('-pk').all(), page_number, 40)

    images = []
    for media_file in media:
        if not media_file.from_vk:
            images.append(cloudinary.CloudinaryImage(media_file.public_id + '.' + media_file.format).
                          image(width=130, height=130, crop='fill', name=media_file.public_id))
        else:
            images.append(media_file.preview_html_tag)

    if number_post_pages > page_number:
        return images
    return []


@staff_only
def media_library(request):
    return page_render(request, 'admin_panel/main_page_admin_panel.html',
                       {'media': 'active',
                        'current_content_page': 'admin_panel/mediaLibrary/media_library.html',
                        'images': load_all_media_files_thumbnails(),
                        'albums': Album.objects.all()
                        })


@staff_only
def media_library_images(request):
    return page_render(request, 'admin_panel/main_page_admin_panel.html',
                       {'media': 'active',
                        'current_content_page': 'admin_panel/mediaLibrary/media_library.html',
                        })


@staff_only
def media_library_video(request):
    return page_render(request, 'admin_panel/main_page_admin_panel.html',
                       {'media': 'active',
                        'current_content_page': 'admin_panel/mediaLibrary/media_library.html',
                        })


@staff_only
def get_modal_media_library(request):
    return JsonResponse({'data': render_to_string('admin_panel/mediaLibrary/modal_media_library.html',
                        {'images': load_all_media_files_thumbnails(), 'albums': Album.objects.all()}, request=request)})


@staff_only
def get_image_custom_size(request):
    media = Media.get_media_by_property(pk=request.GET.get('public_id'))

    if not media.from_vk:
        if request.GET.get('width') == 'NaN':
            image = cloudinary.CloudinaryImage(media.public_id + '.' + media.format). \
                image(name=media.public_id)
        else:
            image = cloudinary.CloudinaryImage(media.public_id + '.' + media.format). \
                image(width=request.GET.get('width'), height=request.GET.get('height'), crop='fill',
                      name=media.public_id)
    else:
        image = media.html_tag
    return JsonResponse({'image': image})


@staff_only
def upload_media_to_cloudinary(request):
    cloudinary_response = cloudinary.uploader.upload(request.FILES['file'], **{'proxy': 'http://proxy.server:3128'})
    if 'url' in cloudinary_response:
        Media.save_uploaded_media(**{'public_id': cloudinary_response['public_id'],
                                     'secure_url': cloudinary_response['secure_url'],
                                     'signature': cloudinary_response['signature'],
                                     'url': cloudinary_response['url'],
                                     'version': cloudinary_response['version'],
                                     'resource_type': cloudinary_response['resource_type'],
                                     'format': cloudinary_response['format']})
        image_thumbnail = cloudinary.CloudinaryImage(
            cloudinary_response['public_id'] + '.' + cloudinary_response['format']). \
            image(width=100, height=100, crop='fill', name=cloudinary_response['public_id'])
        return JsonResponse({'status_code': 200, 'image': image_thumbnail})
    return JsonResponse({'status_code': 500})


@csrf_exempt
def upload_media(request):
    vk_session = VK_session()

    upload = vk_api.VkUpload(vk_session)

    file = request.FILES['file']

    photo = upload.photo(file, album_id=app_settings.VK_ALBUM_ID)

    if len(photo) > 0:
        photo = photo[0]
        uploaded_photo = Media.save_uploaded_media(**{
            'public_id': photo['id'],
            'album_id': photo['album_id'],
            'from_vk': True,
            'photo_75': photo.get('photo_75'),
            'photo_130': photo.get('photo_130'),
            'photo_604': photo.get('photo_604'),
            'photo_807': photo.get('photo_807'),
            'photo_1280': photo.get('photo_1280'),
            'photo_2560': photo.get('photo_2560')
        })

        return JsonResponse({'status_code': 200, 'image': uploaded_photo.html_tag})
    return JsonResponse({'status_code': 500})


@staff_only
def delete_media_from_cloudinary(request):
    public_ids = json.loads(request.POST.get('public_ids'))
    cloudinary_response = cloudinary.api.delete_resources(public_ids)
    deleted_items_key = [public_id for public_id in cloudinary_response['deleted'].keys() if cloudinary_response['deleted'][public_id] in ['not_found', 'deleted']]
    for public_id in deleted_items_key:
        Media.objects.filter(pk=public_id, from_vk=False).delete()
    return JsonResponse({'status_code': 200, 'deleted': deleted_items_key})


@staff_only
def delete_media(request):
    public_ids = json.loads(request.POST.get('public_ids'))
    deleted_items_key = []
    for photo_id in public_ids:
        vk_session = VK_session()
        api = vk_session.get_api()
        api.photos.delete(photo_id=photo_id)

        deleted_items_key.append(photo_id)

    Media.objects.filter(public_id__in=deleted_items_key, from_vk=True).delete()

    return JsonResponse({'status_code': 200, 'deleted': deleted_items_key})


@staff_only
def synchronize_media(request):
    session = vk.Session(access_token=app_settings.VK_SECURE_TOKEN)
    vk_api = vk.API(session)
    albums = vk_api.photos.getAlbums(owner_id=-42000547, v=5.63)

    existing_albums_ids = list(Album.objects.values_list('public_id', flat=True).all())
    albums = albums.get('items', [])

    settings = Settings.objects.first()
    if settings:
        settings.count_of_jobs = len(albums)
    else:
        settings = Settings(count_of_jobs=len(albums))
    settings.save()

    for album in albums:
        if album['id'] not in existing_albums_ids:
            new_album = Album(**{
                'title': album['title'],
                'description': album['description'],
                'public_id': album['id'],
                'thumb_id': album['thumb_id']
            })
            new_album.save()
            existing_albums_ids.append(new_album.public_id)

        import_vk_album_photos.delay(album['id'])

    return redirect('shop_view_settings')

