# -*- coding: utf-8 -*-
from salarium.utils import staff_only
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.template.loader import render_to_string

from media_library.models import Media
from salarium.utils import page_render, set_request_session_alert, get_page_data
from slider.models import Slide


@staff_only
def all_sliders(request):
    slides = Slide.objects.order_by('order').all()
    return page_render(request, 'admin_panel/main_page_admin_panel.html',
                       {'sliders_page': 'active', 'slides': slides,
                        'current_content_page': 'admin_panel/sliders/sliders_list.html', 'different_views': True})


@staff_only
def create_slider(request, slider_id):
    context = {}
    if slider_id != 'None':
        context['slide'] = Slide.objects.get(pk=slider_id)
        context['slides'] = Slide.objects.all()

    if request.is_ajax():
        return JsonResponse(
            {'data': render_to_string('admin_panel/sliders/create_slider_modal.html', context, request=request)})
    return page_render(request, 'admin_panel/main_page_admin_panel.html',
                       {'sliders_page': 'active', 'current_content_page': 'admin_panel/sliders/sliders_list.html'})


@staff_only
def create_or_update_slide(request):
    data, slide = {}, None
    alert_message, alert_type = 'Произошла ошибка', 'warning'
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key not in ['csrfmiddlewaretoken', 'pk']:
                data[key] = value
        data['is_active'] = data.get('is_active', False)
        data['is_active'] = True if data['is_active'] == 'on' else False
        if 'thumbnail' in request.POST.keys():
            data['thumbnail'] = Media.get_media_by_property(pk=data['thumbnail'])

        if 'pk' not in request.POST:
            slide = Slide(**data)
            alert_message, alert_type = 'Слайд успешно добавлен', 'notice'
        else:
            slide = Slide.objects.filter(pk=request.POST.get('pk', None))
            if slide.exists():
                slide.update(**data)
                slide = slide.first()
                alert_message, alert_type = 'Слайд успешно обновлен', 'notice'\

        if slide:
            slide.save()
            slide.reorder_slides()

    set_request_session_alert(request, alert_message, alert_type)
    return redirect('sliders')
