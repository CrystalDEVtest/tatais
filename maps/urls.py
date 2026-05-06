from django.urls import path
from . import views

urlpatterns = [
    path('', views.map_view, name='map_view'),
    path('offices/', views.offices_map_view, name='offices_map'),
]