"""Tournaments URL Configuration

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
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from Tourn import views

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$', views.post_list, name='home'),
    path('signup/', views.signup, name="signup"),
    path('accounts/', include('django.contrib.auth.urls')), # new
    path('tournament/<int:id>/', views.tournament_info, name='tournament'),
    path('tournament/<int:id>/join/', views.join_tournament, name='tournament_join'),
    path('tournament/<int:id>/edit/', views.edit_tournament, name='tournament_edit'),
    path('tournament/<int:id>/add_logo/', views.add_logo, name='tournament_logo'),
    path('addtourn/', views.add_tournament, name='add_tournament'),
    path('mytourns/', views.my_tourns, name='my_tourns'),
    path('mygames/', views.my_games, name='my_games'),
    path('myorgtourns/', views.my_tourns_org, name='my_orgtourns'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('tournament/add/<int:score>', views.submit_score, name='add_score')
]