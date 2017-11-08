import vk

from media_library.models import Media, Album
from salarium import settings


def sync_vk_album_photos(album_id):
    session = vk.Session(access_token=settings.VK_SECURE_TOKEN)
    vk_api = vk.API(session)
    photos = vk_api.photos.get(owner_id=-42000547, album_id=album_id, v=5.63)

    for photo in photos.get('items', []):
        new_ph = Media.objects.filter(public_id=photo['id'])

        if not new_ph.exists():
            new_ph = Media.save_uploaded_media(**{
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
        else:
            new_ph = new_ph.first()

        album = Album.objects.filter(public_id=photo['album_id']).first()
        if album and not album.photos.filter(public_id=new_ph.public_id).exists():
            album.photos.add(new_ph)
            album.save()

    Media.objects.filter(albums__public_id=album_id)\
        .exclude(public_id__in=[p['id'] for p in photos.get('items', [])]).delete()
