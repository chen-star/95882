from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, re_path

from coolcars import views

urlpatterns = [
                  url(r'^$', views.home, name='home'),
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
                  url(r'^addPost$', views.add_post, name='add_post'),
                  url(r'^myprofile$', views.myprofile, name='myprofile'),
                  url(r'^profile/', views.profile, name="profile"),
                  path('followerstream/', views.followerstream, name='followerstream'),
                  path('follow', views.follow, name='follow'),
                  path('unfollow', views.unfollow, name='unfollow'),
                  path('add_comment', views.add_comment, name='add_comment'),
                  url(r'^searchUser', views.search_user, name='search_user'),
                  url(r'^notification', views.notification, name='notification'),
                  url(r'^vote', views.vote, name='vote'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
