from django.urls import path
from . import views


urlpatterns = [
    path('create/', views.create_ticket_view, name='ticket_create'),
    path('<int:pk>/', views.ticket_detail_view, name='ticket_detail'),
    path('<int:pk>/update-status/', views.ticket_update_status, name='ticket_update_status'),
    path('<int:pk>/add-comment/', views.ticket_detail_view, name='add_comment'),
    path('<int:pk>/rate/', views.ticket_detail_view, name='rate_ticket'),
    path('engineer/dashboard/', views.engineer_dashboard, name='engineer_dashboard'),
    path('dispatcher/kanban/', views.dispatcher_kanban, name='dispatcher_kanban'),
    path('<int:pk>/assign/', views.assign_engineer, name='assign_engineer'),
    # Оплата (СБП QR-код)
    path('<int:pk>/pay/', views.payment_create_view, name='payment_create'),
    path('payment/<str:payment_id>/', views.payment_detail_view, name='payment_detail'),
    path('payment/<str:payment_id>/confirm/', views.payment_confirm_view, name='payment_confirm'),
    path('payment/<str:payment_id>/on-site/', views.payment_on_site_view, name='payment_on_site'),
    path('payment/<str:payment_id>/success/', views.payment_success_view, name='payment_success'),
]