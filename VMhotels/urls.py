"""VMhotels URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
	url(r'^$', views.main_page, name='main_page'),
	url(r'^results/$', views.search_results, name='search_results'),
	url(r'^portal/', include('portal.urls', namespace = "portal")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^reservation/', include('reservation.urls', namespace='reservation')),
	url(r'^hotels/', include('hotels.urls', namespace = "hotels")),
	url(r'^review/', include('review.urls', namespace = "review")),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
