from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path

from coolcars import views

urlpatterns = [
                  url(r'^userlogin$', views.user_login, name='user_login'),
                  url(r'^userlogout$', views.user_logout, name='user_logout'),
                  url(r'^carStream$', views.car_stream, name="car_stream"),
                  url(r'^registration/$', views.registration, name='registration'),
                  url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                      views.activate, name='activate'),
                  url(r'^resetPw/$', views.resetPw, name='resetPw'),
                  path('pw', views.pw, name="pw"),
                  url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                      views.password_reset_confirm, name='password_reset_confirm'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
