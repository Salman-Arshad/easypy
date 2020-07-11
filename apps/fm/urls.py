"""easypy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from .views import IndexView, ContentView, UploadView, RMView, CreateFileView, WebHookAPIView, WebHook, SocketIndexView
from django.urls import path

app_name = 'fm'
urlpatterns = [
    # path('webhook/', WebHook.as_view(), name='webhook'),
    path('webhook/', WebHookAPIView.as_view(), name='webhook'),
    path('rm/', RMView.as_view(), name='rm'),
    path('content/', ContentView.as_view(), name='content'),
    path('upload/', UploadView.as_view(), name='content'),
    path('create/', CreateFileView.as_view(), name='create'),
    path('', IndexView.as_view(), name='index'),
    path('socket/', SocketIndexView.as_view(), name='socket')
]
