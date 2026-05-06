from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Notification


@login_required
def notification_list(request):
    notifications = request.user.notifications.select_related('ticket').all().order_by('-created_at')
    unread_count = request.user.notifications.filter(is_read=False).count()

    paginator = Paginator(notifications, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'notifications/list.html', {
        'notifications': page_obj,
        'unread_count': unread_count,
    })


@login_required
def mark_read(request, pk):
    notification = Notification.objects.get(pk=pk, user=request.user)
    notification.is_read = True
    notification.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'unread_count': request.user.notifications.filter(is_read=False).count()})
    return redirect('notification_list')


@login_required
def mark_all_read(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('notification_list')