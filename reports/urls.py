from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_dashboard, name='reports_dashboard'),
    path('export/excel/', views.export_excel, name='reports_export_excel'),
    path('export/csv/', views.export_csv, name='reports_export_csv'),
    path('export/word/', views.export_word, name='reports_export_word'),
]