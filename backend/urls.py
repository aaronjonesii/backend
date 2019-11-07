"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework import routers

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from blog import views

blog_list = views.PostViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

blog_detail = views.PostViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

related_post = views.PostViewSet.as_view({
    'get': 'related_posts'
})

post_byline = views.PostViewSet.as_view({
    'get': 'byline'
})

post_tags = views.PostViewSet.as_view({
    'get': 'tags'
})

newsletter_subscribe = views.NewsletterSubscription.as_view({
    'post': 'create',
})

router = routers.DefaultRouter()
router.register(r'tags', views.TagViewSet)
router.register(r'cats', views.CategoryViewSet)

ipv4pattern = '(?:(?:0|1[\d]{0,2}|2(?:[0-4]\d?|5[0-5]?|[6-9])?|[3-9]\d?)\.){3}(?:0|1[\d]{0,2}|2(?:[0-4]\d?|5[0-5]?|[6-9])?|[3-9]\d?'
ipv6pattern = '(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))'


urlpatterns = [
    path('admin/', admin.site.urls),

    path('blog/', blog_list, name='post_list'),
    path('blog/<int:pk>/', blog_detail, name='post_detail'),
    path('blog/<int:pk>/related_posts/', related_post, name='related_post'),
    path('blog/<int:pk>/byline/', post_byline, name='post_byline'),
    path('blog/<int:pk>/tags/', post_tags, name='post_tags'),

    path('weather/', views.weatherView, name='weather'),  # Get Current Weather Conditions from requester
    path('weather/forecast/', views.forecastWeatherView, name='forecast'),  # Get 5 day forecast from requester

    path('newsletter/subscribe/', newsletter_subscribe, name='newsletter_subscribe'),  # Newsletter subscription
    path('newsletter/unsubscribe/', views.NewsletterUnsubscription.as_view(), name='newsletter_unsubscribe'),  # Newsletter unsubscription

    path('ip/', views.ipView, name='ip'),  # Get IP info from requester
    re_path(rf'^ip/(?P<query_ip>{ipv4pattern}))/$', views.searchIP, name='search_ip'),  # Get IPv4 info from query_ip
    re_path(rf'^ip/(?P<query_ip>{ipv6pattern})/$', views.searchIP, name='search_ip'),  # Get IPv6 info from query_ip

    path('jwt-login/', views.CustomLoginJWTAuthToken.as_view(), name='login'),
    path('jwt-logout/', views.LogOutView.as_view(), name='logout'),
    path('user-signup/', views.CustomSignUpJWTAuthToken.as_view(), name='signup'),
    path('jwt-refresh/', views.CustomRefreshJWTAuthToken.as_view(), name='token_refresh'),

    path('', include(router.urls)),
]

# https://www.django-rest-framework.org/tutorial/6-viewsets-and-routers/
