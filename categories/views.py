from django.template.loader import render_to_string

from media_library.models import Media
from salarium.utils import staff_only
from django.http import JsonResponse
from django.shortcuts import redirect
from categories.models import Category
from salarium.utils import set_request_session_alert, page_render


# Create your views here.
@staff_only
def categories(request):
    return page_render(request, 'admin_panel/main_page_admin_panel.html',
                       {'categories': Category.get_all_categories(), 'categories_is_active': 'active',
                        'current_content_page': 'admin_panel/categories/categories.html'})


@staff_only
def create(request):
    if request.method == 'POST' and request.POST.get('category_name') != '':
        category_name = request.POST.get('category_name')
        if Category.get_category_by_name(name=category_name).exists():
            set_request_session_alert(request, 'Категория с таким именем уже существует', 'warning')
        else:
            Category.create_category(name=category_name)
            set_request_session_alert(request, 'Категория успешно создана!', 'notice')

    return redirect('/categories/')


@staff_only
def create_category_view(request, category_pk):
    context = {}
    if category_pk != 'None':
        context['category'] = Category.objects.get(pk=category_pk)

    if request.is_ajax():
        return JsonResponse(
            {'data': render_to_string('admin_panel/categories/create_category_modal.html', context, request=request)})
    return page_render(request, 'admin_panel/main_page_admin_panel.html',
                       {'sliders_page': 'active', 'current_content_page': 'admin_panel/sliders/sliders_list.html'})


@staff_only
def update_category(request, category_pk):
    data, category = {}, None
    alert_message, alert_type = 'Произошла ошибка', 'warning'
    category = Category.objects.filter(pk=category_pk)

    if request.method == 'POST':
        for key, value in request.POST.items():
            if key not in ['csrfmiddlewaretoken', 'pk']:
                data[key] = value
        if 'thumbnail' in request.POST.keys():
            data['thumbnail'] = Media.get_media_by_property(pk=data['thumbnail'])

        if category.exists():
            category.update(**data)
            category = category.first()
            alert_message, alert_type = 'Категория успешно обновлена', 'notice'

        if category:
            category.save()
    elif request.method == 'GET' and request.GET.get('action') == 'delete' and category.exists():
        category = category.first()
        category.delete()
        Category.objects.filter(pk=category_pk).delete()
        alert_message, alert_type = 'Категория успешно удалена', 'notice'

    set_request_session_alert(request, alert_message, alert_type)
    return redirect('categories')
