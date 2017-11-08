from item.models import Item
from posts.models import Post

# Create your views here.
from salarium.enums import EntityStatus
from salarium.utils import page_render
from slider.models import Slide


def index(request):
    context = {
        'slides': Slide.objects.filter(is_active=True).all()[:5],
        'items': Item.objects.order_by('?').all()[:3],
        'posts': Post.objects.filter(status=EntityStatus.Published.value).order_by('?').all()[:3],
        'additional_menu': True
    }
    return page_render(request, 'site/index.html', context)
