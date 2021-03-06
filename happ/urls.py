"""happ URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from django.conf.urls import include, url

from .auth.urls import urlpatterns as auth_urlpatterns
from .api.regular.urls import urlpatterns as api_urlpatterns
from .api.admin.urls import urlpatterns as api_admin_urlpatterns
from .admin.urls import urlpatterns as admin_urlpatterns

urlpatterns = [
    url(r'^api/v1/admin/', include(api_admin_urlpatterns)),
    url(r'^api/v1/auth/', include(auth_urlpatterns)),
    url(r'^api/v1/', include(api_urlpatterns)),
    url(r'^', include(admin_urlpatterns)),
]
