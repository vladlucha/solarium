"""salarium URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url, include
from django.contrib import admin

import admin_panel.urls
import authentication.views as auth_views
import customer.views as customer_views
import authentication.urls
import basket.urls
import blog.urls
import brand.urls
import categories.urls
import comments.urls
import customer.urls
import emails.urls
import item.urls
import media_library.urls
import news.views
import posts.urls
import shop.urls
import slider.urls
import settings.urls

urlpatterns = [
    url(r'^default_admin_panel/', admin.site.urls),
    url(r'^convert/', include('lazysignup.urls')),
    url(r'^auth/', include(authentication.urls), name='authentication'),
    url(r'^sign_up/', auth_views.sign_up, name='sign_up'),
    url(r'^sign_in/', auth_views.sign_in, name='sign_in'),
    url(r'^logout/', auth_views.sign_out, name='logout'),
    url(r'^$', news.views.index, name='news'),
    url(r'^admin_panel/', include(admin_panel.urls), name='admin_panel'),
    url(r'^categories/', include(categories.urls), name='categories'),
    url(r'^blog/', include(blog.urls), name='blog'),
    url(r'^shop/', include(shop.urls), name='shop'),
    url(r'^posts/', include(posts.urls), name='posts'),
    url(r'^media_library/', include(media_library.urls), name='media_library'),
    url(r'^brands/', include(brand.urls), name='brands'),
    url(r'^items/', include(item.urls), name='items'),
    url(r'^slider/', include(slider.urls), name='slider'),
    url(r'^basket/', include(basket.urls), name='basket'),
    url(r'^comment/', include(comments.urls), name='comment'),
    url(r'^profile/', include(customer.urls), name='customer'),
    url(r'^emails/', include(emails.urls), name='emails'),
    url(r'^toggle_view/(?P<view_type>\w+)/$', customer_views.toggle_view, name='toggle_view'),
    url(r'^add_to_rss/', customer_views.add_to_rss, name='add_to_rss'),
    url(r'^settings/', include(settings.urls), name='settings'),
]
