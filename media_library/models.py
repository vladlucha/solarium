from __future__ import unicode_literals
from django.db import models


class Album(models.Model):
    title = models.CharField(max_length=150, unique=False, default=None)
    description = models.TextField(unique=False, null=True, default=None)
    public_id = models.IntegerField(unique=False, default=None)
    thumb_id = models.IntegerField(unique=False, default=None)
    photos = models.ManyToManyField('media_library.Media', related_name='albums')


# Create your models here.
class Media(models.Model):
    public_id = models.CharField(max_length=150, unique=False, default=None)
    album_id = models.CharField(max_length=150, unique=False, default=None)
    secure_url = models.CharField(max_length=255, null=True, unique=False, default=None)
    signature = models.CharField(max_length=255, null=True, unique=False, default=None)
    src_url = models.CharField(max_length=255, null=True, unique=False, default=None)
    version = models.CharField(max_length=255, null=True, unique=False, default=None)
    resource_type = models.CharField(max_length=255, default='image')
    format = models.CharField(max_length=255, null=True, default=None)
    from_vk = models.BooleanField(default=False)
    photo_75 = models.CharField(max_length=255, null=True, unique=False, default=None)
    photo_130 = models.CharField(max_length=255, null=True, unique=False, default=None)
    photo_604 = models.CharField(max_length=255, null=True, unique=False, default=None)
    photo_807 = models.CharField(max_length=255, null=True, unique=False, default=None)
    photo_1280 = models.CharField(max_length=255, null=True, unique=False, default=None)
    photo_2560 = models.CharField(max_length=255, null=True, unique=False, default=None)
    description = models.TextField(unique=False, null=True, default=None)

    @staticmethod
    def save_uploaded_media(**kwargs):
        new_media = Media.objects.create(**kwargs)
        new_media.save()
        return new_media

    @staticmethod
    def get_media_by_property(**kwargs):
        return Media.objects.filter(**kwargs).first()

    @staticmethod
    def get_all_media():
        return Media.objects.all()

    @property
    def url(self):
        img_src = self.get_high_res_src
        return img_src

    @property
    def preview_html_tag(self):
        html = '<img src={0} name={1} data-album-id={2}></img>'
        return html.format(self.photo_130, self.pk, self.album_id)

    @property
    def get_high_res_src(self):
        resolutions = ['photo_2560', 'photo_1280', 'photo_807', 'photo_604', 'photo_130', 'photo_75', 'src_url']
        hi_res_src, i = None, 0

        while not hi_res_src:
            hi_res_src = self.__dict__.get(resolutions[i])
            i += 1
        return hi_res_src

    @property
    def html_tag(self):
        html = '<img src={0} name={1} data-album-id={2}></img>'
        hi_res_src = self.get_high_res_src

        return html.format(hi_res_src, self.pk, self.album_id)