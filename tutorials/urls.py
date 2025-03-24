from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tutorials/', views.tutorial_list, name='tutorial_list'),
    path('tutorial/<slug:slug>/', views.tutorial_detail, name='tutorial_detail'),
    path('learning-paths/', views.learning_path_list, name='learning_path_list'),
    path('learning-path/<slug:slug>/', views.learning_path_detail, name='learning_path_detail'),
    path('learning-path/<slug:path_slug>/complete/<slug:tutorial_slug>/', views.mark_tutorial_complete, name='mark_tutorial_complete'),
    path('learning-path/<slug:path_slug>/incomplete/<slug:tutorial_slug>/', views.mark_tutorial_incomplete, name='mark_tutorial_incomplete'),
]

