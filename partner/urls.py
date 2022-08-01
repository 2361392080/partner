from django.conf.urls import url
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home),
    path('register/', views.register),
    path('login/', views.login),
    path('home/', views.home),
    path('create/', views.create),
    path('logout/', views.logout),
    path('activities/', views.activities),
    path('friend_request/', views.send_friend_request, name="friend-request"),  #POST方法
    path('friend_remove/', views.remove_friend, name="remove-friend"),  #POST方法
    path('friend_request_cancel/', views.cancel_friend_request, name="friend-request-cancel"),   #POST方法
    path('accept_friend_request/<friend_request_id>', views.accept_friend_request, name='friend-request-accept'),  #GET方法
    path('decline_friend_request/<friend_request_id>', views.decline_friend_request, name='friend-request-decline'),#GET方法
    url(r'^details/(\d+)/$', views.details),
    url(r'^friendpage/(\d+)/$', views.friendpage),
    path('changeHeadimg/', views.changeHeadimg),
    path('changeDetails/', views.changeDetails),
    path('searchAccount/', views.searchAccount),
    path('homepage/', views.homepage),
]
