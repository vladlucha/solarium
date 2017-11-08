from django.shortcuts import redirect

from media_library.models import Media
from settings.models import Settings
from salarium.utils import page_render, set_request_session_alert


def shop_view_settings(request):
    context = {'settings': Settings.objects.first(), 'shop_view_settings': 'active',
               'current_content_page': 'admin_panel/settings/shop_view_settings.html'}
    return page_render(request, 'admin_panel/main_page_admin_panel.html', context)


def update_shop_view_settings(request):
    data, settings = {}, None
    alert_message, alert_type = 'Произошла ошибка', 'warning'
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key not in ['csrfmiddlewaretoken', 'pk']:
                data[key] = value
        if 'thumbnail' in request.POST.keys():
            data['thumbnail'] = Media.get_media_by_property(pk=data['thumbnail'])

        settings = Settings.objects.first()
        if settings:
            Settings.objects.filter(pk=settings.pk).update(**data)
        else:
            settings = Settings(**data)
            settings.save()

        alert_message, alert_type = 'Настройки успешно обновлены', 'notice'

    set_request_session_alert(request, alert_message, alert_type)
    return redirect('shop_view_settings')
