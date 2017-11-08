from django.db.models import Q

from brand.models import Brand
from categories.models import Category
from item.models import Item, ItemSizeCountMap, ItemType
from salarium.utils import get_page_data, page_render, get_page_number, parse_int
from settings.models import Settings

filters = {
    'selected_brands': Item.filter_by_brands,
    'selected_categories': Item.filter_by_categories,
    'selected_max_price': Item.filter_by_max_price,
    'selected_min_price': Item.filter_by_min_price,
    'selected_sizes': Item.filter_by_sizes,
    'selected_types': Item.filter_by_types
}


def shop(request, page_number):
    context = _precess_request_params(request)
    page_number = get_page_number(page_number)
    items_query = _get_items_query(context)

    shop_page, items, number_shop_pages = get_page_data(items_query.order_by('-pk'), page_number, 12)
    context.update({
        'shop_page': shop_page,
        'number_shop_pages': range(1, number_shop_pages),
        'items': items
    })

    context['categories'] = set(Category.objects.exclude(items__isnull=True).all())
    context['brands'] = set(Brand.objects.exclude(items__isnull=True).all())
    context['item_types'] = set(ItemType.objects.exclude(items__isnull=True).all())

    context['header_data'] = select_header_data(context)

    context['sizes'] = _get_actual_sizes()

    return page_render(request, 'site/shop.html', context)


def _get_items_query(context):
    query = Item.objects
    for key, value in context.items():
        q_filter = filters.get(key, None)
        if q_filter:
            query = q_filter(query, value)
    return query


def select_header_data(context):
    settings = Settings.objects.first()
    if len(context.get('selected_brands', [])) == 1:
        brand = Brand.objects.filter(pk=context['selected_brands'][0]).first()
        return {'thumbnail': brand.thumbnail, 'title': brand.name, 'description': brand.description}
    elif len(context.get('selected_categories', [])) == 1:
        category = Category.objects.filter(pk=context['selected_categories'][0]).first()
        return {'thumbnail': category.thumbnail, 'title': category.name, 'description': category.description}
    elif settings and (settings.title or settings.description):
        return {'thumbnail': settings.thumbnail, 'title': settings.title, 'description': settings.description}
    return None


def _precess_request_params(request):
    prices = Item.objects.exclude(price__isnull=True).values_list('price', flat=True).order_by('-price').all()

    context = {
        'max_price': int(prices.first() if len(prices) else 0),
        'min_price': int(prices.last() if len(prices) else 0)
    }

    for key in request.GET.keys():
        value = request.GET.getlist(key)
        if key == 'price_range':
            value = value[0].split(',')
            context['selected_min_price'] = parse_int(value[0], context['min_price'])
            context['selected_max_price'] = parse_int(value[1], context['max_price'])
        else:
            context['selected_' + key] = [parse_int(v) for v in value]
    return context


def _get_actual_sizes():
    sizes_count = ItemSizeCountMap.objects.exclude(items__isnull=True).exclude(count__lte=0).all()
    sizes = []
    for size_count in sizes_count:
        size = next((s for s in sizes if s['pk'] == size_count.size.pk), None)
        if not size:
            sizes.append({
                'pk': size_count.size.pk,
                'name': size_count.size.name,
                'items_count': size_count.items.count(),
            })
        else:
            size['items_count'] += size_count.items.count()
    return sizes


def get_item(request, item_slug):
    item = Item.objects.filter(slug=item_slug).first()

    recent = request.session.get('recently_viewed', [])
    if 'recently_viewed' in request.session:
        if len(request.session['recently_viewed']) >= 3:
            request.session['recently_viewed'] = request.session['recently_viewed'][-2:]
        request.session['recently_viewed'] += [item.pk]
    else:
        request.session['recently_viewed'] = [item.pk]

    same_items = Item.objects.filter(Q(tags__tag_text__in=[t.tag_text for t in item.tags.all()]) |
                                     Q(categories__name__in=[c.name for c in item.categories.all()]) |
                                     Q(brand=item.brand)).exclude(pk=item.pk).all()[:4]
    return page_render(request, 'site/shop_single_item.html',
                       {'item': item,
                        'same_items': set(same_items),
                        'sizes': ItemSizeCountMap.objects.filter(items__in=[item], count__gt=0),
                        'referrer_url': request.META.get('HTTP_REFERER'),
                        'recent': Item.objects.filter(pk__in=recent).exclude(pk=item.pk).all().reverse(),
                        'new_items': Item.objects.order_by('-id').all()[:6]})
