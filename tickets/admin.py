from django.contrib import admin
from .models import Ticket, TicketComment, TicketAttachment, TicketHistory, ServiceCategory


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'customer', 'guest_name', 'service_type', 'status', 'priority', 'assigned_engineer', 'city', 'created_at')
    list_filter = ('status', 'priority', 'service_type', 'city', 'created_at')
    search_fields = ('ticket_number', 'description', 'address', 'guest_name', 'guest_phone')
    date_hierarchy = 'created_at'


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'author', 'created_at', 'is_system')
    list_filter = ('is_system', 'created_at')


@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'filename', 'uploaded_at', 'uploaded_by')


@admin.register(TicketHistory)
class TicketHistoryAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'user', 'action', 'old_value', 'new_value', 'created_at')
