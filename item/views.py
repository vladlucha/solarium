# -*- coding: utf-8 -*-

import datetime

import math

from basket.models import PromoCode
from brand.models import Brand
from categories.models import Category
from salarium.utils import staff_only, get_page_number, parse_int
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from item.models import SizeGroup, Size, Material, Sale, Item, ItemType
from salarium.utils import page_render, set_request_session_alert, get_page_data
from media_library.models import Media

from tags.models import Tag

templates_by_types = {
    'size_group': 'admin_panel/items/items_settings/size_group.html',
    'size': 'admin_panel/items/items_settings/size.html'
}

models_by_types = {
    'size_group': SizeGroup,
    'size': Size
}

items_per_page = 2


@staff_only
def all_items(request, page_number):
    page_number = get_page_number(page_number)
    item_page, items, number_item_pages = get_page_data(Item.objects.order_by('-pk').all(), page_number, 12)

    return page_render(request, 'admin_panel/main_page_admin_panel.html',
                       {'items_page': 'active', 'items_is_active': 'active',
                        'items': items, 'item_page': item_page, 'number_item_pages': range(1, number_item_pages),
                        'current_content_page': 'admin_panel/items/items_page.html',
                        'current_items_page': 'admin_panel/items/items_list.html', 'different_views': True})


@staff_only
def create_item(request, item_id):
    context = {
        'size_groups': SizeGroup.objects.order_by('-pk').all(),
        'sales': Sale.objects.all(),
        'materials': Material.objects.all(),
        'tags': Tag.objects.all(),
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
        'items_types': ItemType.objects.all()
    }
    if item_id != 'None':
        context['item'] = Item.objects.get(pk=item_id)
        context['sizes_count_map'] = {}
        for item_count in context['item'].items_count.all():
            context['sizes_count_map'][item_count.size.pk] = item_count.count

    if request.is_ajax():
        return JsonResponse(
            {'data': render_to_string('admin_panel/items/create_item_modal.html', context, request=request)})
    return page_render(request, 'admin_panel/main_page_admin_panel.html',
                       {'items_page': 'active', 'items_is_active': 'active',
                        'current_content_page': 'admin_panel/items/create_item.html'})


@staff_only
def items_settings(request):
    size_groups = SizeGroup.objects.order_by('-pk').all()
    materials = Material.objects.order_by('-pk').all()

    return page_render(request, 'admin_panel/main_page_admin_panel.html',
                       {'items_settings_page': 'active', 'items_is_active': 'active',
                        'current_content_page': 'admin_panel/items/items_page.html',
                        'current_items_page': 'admin_panel/items/items_settings.html',
                        'size_groups': size_groups, 'materials': materials})


@staff_only
def append_basic_context(request, context):
    context.update({'items_is_active': 'active',
                    'current_content_page': 'admin_panel/items/items_page.html',
                    'materials': Material.objects.all()[:items_per_page],
                    'sales': {'objects': Sale.objects.all()[:items_per_page],
                              'pages_count': range(1, int(math.ceil(len(Sale.objects.all()) / items_per_page)) + 2)}
                    })
    if 'alert_message' in request.session:
        context['alert_message'] = request.session.pop('alert_message')
        context['alert_type'] = request.session.pop('alert_type')

    if 'alert_message' in request.session:
        context['alert_message'] = request.session.pop('alert_message')
        context['alert_type'] = request.session.pop('alert_type')
        context['items_settings_page'] = request.session.pop('items_settings_page')
    return context


@staff_only
def create_size_group(request):
    name = request.POST.get('name', None)
    size_group = SizeGroup.objects.filter(name=name)
    if name is None or len(name) == 0:
        set_request_session_alert(request, 'Название обязательное поле', 'error')
    elif size_group.exists():
        set_request_session_alert(request, 'Такой тип размера уже существует', 'error')
    else:
        SizeGroup.objects.create(name=name)
        set_request_session_alert(request, 'Тип размера успешно создан', 'notice')
    return items_settings(request)


@staff_only
def delete_size_group(request):
    return delete_object(request, SizeGroup, 'items_settings')


@staff_only
def update_size_group(request):
    return update_object(request, SizeGroup)


@staff_only
def create_size(request, size_group_id):
    size_group = SizeGroup.objects.get(pk=size_group_id)
    name = request.POST.get('name', None)
    size = Size.objects.filter(name=name)
    if name is None or len(name) == 0:
        return JsonResponse({'alert_type': 'error', 'message': 'Название обязательное поле'})
    else:
        additional = ''
        if not size.exists():
            size = Size.objects.create(name=name)
            additional = 'создан и'
        else:
            size = size.first()
        if size not in size_group.sizes.all():
            size_group.sizes.add(size)
        else:
            return JsonResponse({'alert_type': 'error', 'message': 'Материал уже добавлен в группу'})
        size_group.save()
        return JsonResponse(
            {'data': render_to_string('admin_panel/items/items_settings/size.html',
                                      {"size": size, "size_group": size_group}, request=request),
             'alert_type': 'notice',
             'message': 'Размер успешно {0} добавлен в группу'.format(additional)})


@staff_only
def delete_size(request):
    return delete_object(request, Size, 'items_settings')


@staff_only
def item_types(request):
    items_types = ItemType.objects.all()
    return page_render(request, 'admin_panel/main_page_admin_panel.html',
                       {'items_types_page': 'active', 'items_is_active': 'active',
                        'current_content_page': 'admin_panel/items/items_page.html',
                        'current_items_page': 'admin_panel/items/items_types.html',
                        'items_types': items_types})


@staff_only
def create_item_type(request):
    name = request.POST.get('name', None)
    item_type = ItemType.objects.filter(name=name)
    if name is None or len(name) == 0:
        set_request_session_alert(request, 'Название типа товара обязательное поле', 'error')
    elif item_type.exists():
        set_request_session_alert(request, 'Такой тип товара уже существует', 'error')
    else:
        ItemType.objects.create(name=name)
        set_request_session_alert(request, 'Тип товара успешно добавлен', 'notice')
    return redirect('item_types')


@staff_only
def delete_item_type(request):
    return delete_object(request, ItemType, 'item_types')


@staff_only
def update_item_type(request):
    return update_object(request, ItemType)


@staff_only
def create_material(request):
    name = request.POST.get('name', None)
    material = Material.objects.filter(name=name)
    if name is None or len(name) == 0:
        set_request_session_alert(request, 'Название материала обязательное поле', 'error')
    elif material.exists():
        set_request_session_alert(request, 'Такой материал уже существует', 'error')
    else:
        Material.objects.create(name=name)
        set_request_session_alert(request, 'Материал успешно добавлен', 'notice')
    return redirect('items_settings')


@staff_only
def delete_material(request):
    return delete_object(request, Material, 'items_settings')


@staff_only
def update_material(request):
    return update_object(request, Material)


@staff_only
def update_object(request, model):
    if request.method == "POST":
        object_pk = int(request.POST.get('pk'))
        instance = model.objects.filter(pk=object_pk)
        if instance.exists():
            update_data = {request.POST.get('name'): request.POST.get('value')}
            instance.update(**update_data)
            response = {'message': model.__name__ + ' успешно обновлен', 'alert_type': 'notice'}
        else:
            response = {'message': model.__name__ + ' не существует', 'alert_type': 'error'}
        return JsonResponse(response)


@staff_only
def delete_object(request, model, route):
    if request.method == 'POST':
        instance = model.objects.filter(pk=request.POST.get('pk'))
        if instance.exists():
            instance.delete()
            set_request_session_alert(request, model.__name__ + ' успешно удален', 'notice')
        else:
            set_request_session_alert(request, model.__name__ + ' не существует', 'error')
    return redirect(route)


# <-------- SALES ------->


@staff_only
def sales(request, page_number=1):
    sale_page = get_page_number(page_number)
    sale_page, sales, number_sale_pages = get_page_data(Sale.objects.order_by('-pk').all(), sale_page)
    return page_render(request, 'admin_panel/main_page_admin_panel.html',
                       {'sales_page': 'active', 'items_is_active': 'active',
                        'current_content_page': 'admin_panel/items/items_page.html',
                        'current_items_page': 'admin_panel/items/sales.html',
                        'sale_page': sale_page, 'sales': sales, 'number_sale_pages': range(1, number_sale_pages),
                        'errors': request.session.pop('sale_errors', {}),
                        'sale_data': request.session.pop('sale_data', {})})


@staff_only
def create_sale(request):
    if request.method == 'POST':
        sale_data = {
            'name': request.POST.get('name'),
            'date_of_start': request.POST.get('date_of_start'),
            'date_of_end': request.POST.get('date_of_end'),
            'rate': request.POST.get('rate'),
        }
        errors = validate_new_sale(**sale_data)
        if len(errors) == 0:
            Sale.objects.create(**sale_data)
            set_request_session_alert(request, 'Скидка успешно создана', 'notice')
            return redirect('sales')
        set_request_session_alert(request, 'Ошибка валидации', 'error')
        request.session['sale_data'] = sale_data
        request.session['sale_errors'] = errors
        return redirect('sales', 1)
    return redirect('sales')


@staff_only
def delete_sale(request):
    return delete_object(request, Sale, 'sales')


def validate_new_sale(**kwargs):
    errors = {}
    date_start = None
    date_end = None
    for key in kwargs.keys():
        if len(kwargs[key]) == 0:
            errors[key] = 'Поле обязательно'
        else:
            if key == 'rate':
                try:
                    kwargs[key] = int(kwargs[key])
                    if kwargs[key] > 100 or kwargs[key] < 0:
                        errors[key] = 'Invalid value'
                except ValueError as e:
                    errors[key] = 'Rate is not int'
            elif key == 'date_of_start':
                date_start = datetime.datetime.strptime(kwargs[key], '%Y-%m-%d %H:%M')
            elif key == 'date_of_end':
                date_end = datetime.datetime.strptime(kwargs[key], '%Y-%m-%d %H:%M')
            elif key == 'name' and Sale.objects.filter(name=kwargs[key]).exists():
                errors[key] = 'Sale with this name already exists'
    if date_end < date_start:
        errors['date_of_start'] = errors['date_of_end'] = 'Дата окончания должна быть раньше даты начала'
    return errors


@staff_only
def create_or_update_item(request):
    if request.method == 'POST':
        size_group = SizeGroup.objects.get(pk=request.POST.get('size-group'))
        sizes_count = []
        for size in size_group.sizes.all():
            key = str(size_group.pk) + '-' + str(size.pk)
            if key in request.POST:
                sizes_count.append({'size': size, 'count': request.POST.get(key + '-value')})

        try:
            brand = Brand.objects.get(pk=request.POST.get('brand'))
        except Brand.DoesNotExist:
            brand = None

        if 'pk' not in request.POST:
            Item.save_item(**{'name': request.POST.get('name'),
                              'description': request.POST.get('description'),
                              'manufacturer_country': request.POST.get('country'),
                              'thumbnail': Media.get_media_by_property(pk=request.POST.get('thumbnail')),
                              'gallery': [Media.get_media_by_property(pk=public_id) for public_id in
                                          request.POST.get('gallery').split(',')],
                              'tags': request.POST.get('tags'),
                              'materials': [Material.objects.get(pk=material_pk) for material_pk in
                                            request.POST.getlist('materials', [])],
                              'sales': [Sale.objects.get(pk=sale_pk) for sale_pk in request.POST.getlist('sales', [])],
                              'categories': [Category.objects.get(pk=category_pk) for category_pk in
                                             request.POST.getlist('categories', [])],
                              'types': [ItemType.objects.get(pk=type_pk) for type_pk in
                                        request.POST.getlist('item_types', [])],
                              'sizes_count': sizes_count,
                              'brand': brand,
                              'price': request.POST.get('price'),
                              'us_price': 0})
            alert_message = 'Товар успешно создан ' + (
                'и опубликован' if request.POST.get('status') == 'Published' else '')
        else:
            Item.update_item(pk=request.POST.get('pk'), **{
                'name': request.POST.get('name'),
                'description': request.POST.get('description'),
                'manufacturer_country': request.POST.get('country'),
                'thumbnail': Media.get_media_by_property(pk=request.POST.get('thumbnail')),
                'gallery': [Media.get_media_by_property(pk=public_id) for public_id in request.POST.get('gallery').split(',') if public_id != ''],
                'tags': request.POST.get('tags'),
                'materials': [Material.objects.get(pk=material_pk) for material_pk in request.POST.getlist('materials', [])],
                'sales': [Sale.objects.get(pk=sale_pk) for sale_pk in request.POST.getlist('sales', [])],
                'categories': [Category.objects.get(pk=category_pk) for category_pk in request.POST.getlist('categories', [])],
                'types': [ItemType.objects.get(pk=type_pk) for type_pk in request.POST.getlist('item_types', [])],
                'sizes_count': sizes_count,
                'brand': brand,
                'price': request.POST.get('price'),
                'us_price': 0
            })
            alert_message = 'Товар успешно обновлен ' + (
                'и опубликован' if request.POST.get('status') == 'Published' else '')
        set_request_session_alert(request, alert_message, 'notice')
    return redirect('items')


@staff_only
def promocodes(request):
    promocodes = PromoCode.objects.all()
    return page_render(request, 'admin_panel/main_page_admin_panel.html',
                       {'promocodes_page': 'active', 'items_is_active': 'active',
                        'current_content_page': 'admin_panel/items/items_page.html',
                        'current_items_page': 'admin_panel/items/promocodes.html',
                        'promocodes': promocodes})


@staff_only
def create_promocode(request):
    alert_message = 'Произошла ошибка'
    if request.method == "POST":
        promocode = PromoCode(**{
            'value': parse_int(request.POST.get('value', 0), 0),
            'code': request.POST.get('code', '')
        })
        promocode.save()
        alert_message = 'Промокод успешно добавлен'
    set_request_session_alert(request, alert_message, 'notice')
    return redirect('promocodes')


@staff_only
def update_promocode(request, promocode_id):
    alert_message = 'Произошла ошибка'
    if request.method == "POST":
        promocode = PromoCode.objects.filter(pk=promocode_id)
        if promocode.exists():
            promocode.update(code=request.POST.get('code', promocode.first().code),
                             value=request.POST.get('pr_value', promocode.first().value))
            alert_message = 'Промокод успешно обновлен'
    return JsonResponse({'alert_type': 'notice', 'message': alert_message})


@staff_only
def delete_promocode(request, promocode_id):
    alert_message = 'Произошла ошибка'
    if request.method == "POST":
        promocode = PromoCode.objects.filter(pk=promocode_id)
        if promocode.exists():
            promocode.delete()
            alert_message = 'Промокод успешно удален'
    set_request_session_alert(request, alert_message, 'notice')
    return redirect('promocodes')
