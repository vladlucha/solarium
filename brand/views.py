from salarium.enums import EntityStatus
from salarium.utils import staff_only
from django.shortcuts import redirect

from media_library.models import Media
from brand.models import Brand

# Create your views here.
from salarium.utils import page_render, set_request_session_alert, get_page_data


@staff_only
def all_brands(request):
    brand_page, brands, number_brand_pages = get_page_data(Brand.objects.order_by('-pk').all(),
                                                           request.POST.get('brand_page', 1), 12)
    context = {'brands': 'active', 'current_content_page': 'admin_panel/brands/all_brands.html', 'all_brands': brands,
               'brand_page': brand_page, 'number_brand_pages': range(1, number_brand_pages), 'different_views': True}
    return page_render(request, 'admin_panel/main_page_admin_panel.html', context)


@staff_only
def create_brand(request, brand_id):
    if request.method == 'GET':
        brand = Brand.get_brand_by_property(pk=brand_id) if brand_id is not None and brand_id != 'None' else None
        return page_render(request, 'admin_panel/main_page_admin_panel.html',
                           {'brands': 'active',
                            'current_content_page': 'admin_panel/brands/create_brand.html',
                            'brand': brand,
                            'statuses': EntityStatus.items()
                            })


@staff_only
def create_or_update_brand(request):
    if request.method == 'POST':
        if 'pk' not in request.POST:
            Brand.save_brand(**{
                'name': request.POST.get('name'),
                'description': request.POST.get('description'),
                'country': request.POST.get('country'),
                'thumbnail': Media.get_media_by_property(pk=request.POST.get('thumbnail')),
                'banner': Media.get_media_by_property(pk=request.POST.get('banner')),
                'status': request.POST.get('status')
            })
            alert_message = 'Брэнд успешно создан ' + (
                'и опубликован' if request.POST.get('status') == EntityStatus.Published.value else '')
            alert_type = 'notice'
        else:
            Brand.update_brand(pk=request.POST.get('pk'), **{
                'name': request.POST.get('name'),
                'description': request.POST.get('description'),
                'country': request.POST.get('country'),
                'thumbnail': Media.get_media_by_property(pk=request.POST.get('thumbnail')),
                'banner': Media.get_media_by_property(pk=request.POST.get('banner')),
                'status': request.POST.get('status')
            })
            alert_message = 'Бренд успешно обновлен ' + (
                'и опубликован' if request.POST.get('status') == EntityStatus.Published.value else '')
            alert_type = 'notice'
        set_request_session_alert(request, alert_message, alert_type)
    return redirect('brands')


@staff_only
def delete_brand(request, brand_id):
    brand = Brand.objects.filter(pk=brand_id).first()
    if brand:
        brand.delete()

    alert_message = 'Бренд успешно удален'
    set_request_session_alert(request, alert_message, 'notice')
    return redirect('brands')
