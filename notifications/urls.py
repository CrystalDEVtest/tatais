from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('mark-read/<int:pk>/', views.mark_read, name='notification_mark_read'),
    path('mark-all-read/', views.mark_all_read, name='notification_mark_all_read'),
]
