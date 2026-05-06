from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tickets.models import Ticket
from django.db.models import Count


@login_required
def map_view(request):
    if request.user.role not in ('engineer', 'dispatcher', 'admin'):
        from django.contrib import messages
        messages.error(request, 'У вас нет доступа.')
        from django.shortcuts import redirect
        return redirect('home')
    
    # Показываем ВСЕ активные заявки (не только с координатами)
    tickets = Ticket.objects.exclude(status='completed').exclude(status='rejected')
    
    city_counts = dict(
        Ticket.objects.filter(status__in=('new', 'assigned', 'in_progress', 'parts_needed'))
        .values('city').annotate(count=Count('id')).values_list('city', 'count')
    )
    
    new_count = tickets.filter(status='new').count()
    progress_count = tickets.filter(status='in_progress').count()
    
    return render(request, 'maps/map.html', {
        'tickets': tickets,
        'city_counts': city_counts,
        'new_count': new_count,
        'progress_count': progress_count,
    })


@login_required
def offices_map_view(request):
    return render(request, 'maps/offices_map.html')