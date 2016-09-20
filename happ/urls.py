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
from .api.regular.urls import router as regular_router
from .api.admin.urls import router as admin_router
from .admin.urls import urlpatterns as admin_urlpatterns

urlpatterns = [
    url(r'^api/v1/admin/', include(admin_router.urls)),
    url(r'^api/v1/auth/', include(auth_urlpatterns)),
    url(r'^api/v1/', include(regular_router.urls)),
    url(r'^', include(admin_urlpatterns)),
]
