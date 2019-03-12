"""know URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from app import views
from django.views.static import serve
from know import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index),
    url(r'^login/', views.login),
    url(r'^register/', views.register),
    url(r'^check_name/', views.check_name),
    url(r'^index/', views.index),
    url(r'^logout/$', views.logout),
    url(r'^diggit/$', views.diggit),
    url(r'^commit_content/$', views.commit_content),
    url(r'^backend', views.backend),
    url(r'^add_article', views.add_article),
    url(r'^update_article/(?P<pk>\d+)', views.update_article),
    url(r'^blogself', views.add_article),
    url(r'^upload_img', views.upload_img),
    url(r'^get_article/(?P<pk>\d+)', views.get_article),
    url(r'^update_head', views.update_head),
    url(r'^media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^(?P<username>[\w]+)/(?P<condition>category|tag|archive)/(?P<param>.*)', views.user_blog),
    url(r'^(?P<username>[\w]+)/article/(?P<id>\d+)', views.article_detail),
    url(r'^(?P<username>[\w]+)/$', views.user_blog),


    url(r'', views.error),

]
