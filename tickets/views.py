from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q, Avg, F, DurationField
from django.db.models.functions import TruncDate
from django.views.decorators.http import require_POST
from datetime import timedelta
import random
import string

from .models import Ticket, TicketComment, TicketAttachment, ServiceCategory, TicketHistory, Payment
from .forms import (
    TicketCreateForm, GuestTicketCreateForm,
    TicketCommentForm, TicketStatusForm, TicketRatingForm
)
from accounts.models import User
from .payment_utils import generate_sbp_qr_base64, generate_sbp_qr_phone_only, get_recipient_details


def generate_temp_password(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def create_ticket_view(request):
    if request.user.is_authenticated:
        form_class = TicketCreateForm
    else:
        form_class = GuestTicketCreateForm

    # ===== Защита от двойной отправки =====
    if request.method == 'POST':
        session_token = request.POST.get('form_token', '')
        if session_token:
            if request.session.get('last_form_token') == session_token:
                # Дубликат — перенаправляем без создания
                messages.warning(request, 'Заявка уже была отправлена.')
                return redirect('create_ticket')
            request.session['last_form_token'] = session_token
    # ===== Конец защиты =====

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)

            if request.user.is_authenticated:
                ticket.customer = request.user
                if request.user.city:
                    ticket.city = dict(User.CITY_CHOICES).get(request.user.city, request.user.city)

            ticket.status = 'new'

            # ===== Цена из формы =====
            price_val = request.POST.get('price', '')
            if price_val:
                try:
                    ticket.price = float(price_val)
                except (ValueError, TypeError):
                    pass

            # ===== Способ оплаты =====
            ticket.payment_method = request.POST.get('payment_method', 'none')

            ticket.save()

            # ===== ГЕОКОДИРОВАНИЕ АДРЕСА =====
            from .geocode import geocode_address, get_city_center
            coords = geocode_address(ticket.city, ticket.address)
            if coords:
                ticket.latitude = coords[0]
                ticket.longitude = coords[1]
                ticket.save(update_fields=['latitude', 'longitude'])
            else:
                fallback = get_city_center(ticket.city)
                ticket.latitude = fallback[0]
                ticket.longitude = fallback[1]
                ticket.save(update_fields=['latitude', 'longitude'])
            # ===== КОНЕЦ ГЕОКОДИРОВАНИЯ =====

            # Handle attachments
            files = request.FILES.getlist('attachments') if 'attachments' in request.FILES else []
            for f in files:
                TicketAttachment.objects.create(
                    ticket=ticket, file=f, filename=f.name,
                    uploaded_by=request.user if request.user.is_authenticated else None
                )

            # Create history entry
            TicketHistory.objects.create(
                ticket=ticket,
                user=request.user if request.user.is_authenticated else None,
                action='Заявка создана',
                new_value='Новая'
            )

            # Send notification
            from notifications.utils import create_notification
            create_notification(
                ticket=ticket,
                notification_type='ticket_created',
                message=f'Создана новая заявка #{ticket.ticket_number}'
            )

            temp_password = generate_temp_password() if not request.user.is_authenticated else None
            messages.success(request, f'Заявка #{ticket.ticket_number} успешно создана!')
            if temp_password:
                messages.info(request, f'Ваш временный пароль для отслеживания: {temp_password}')

            return redirect('ticket_detail', pk=ticket.pk)
    else:
        form = form_class()

    categories = ServiceCategory.objects.all()
    return render(request, 'tickets/create.html', {
        'form': form, 'categories': categories
    })


def ticket_detail_view(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    comments = ticket.comments.filter(is_system=False).select_related('author')
    attachments = ticket.attachments.all()
    history = ticket.history.all()
    
    can_view = (
        request.user.is_authenticated and (
            request.user == ticket.customer or
            request.user.role in ('engineer', 'dispatcher', 'admin') or
            ticket.assigned_engineer == request.user
        )
    )
    
    if not can_view:
        # Allow guest access with ticket number
        messages.warning(request, 'Войдите в систему для просмотра заявки.')
        return redirect('login')
    
    comment_form = TicketCommentForm()
    rating_form = TicketRatingForm(instance=ticket) if ticket.status == 'completed' and ticket.customer == request.user else None
    
    if request.method == 'POST':
        if 'comment' in request.POST:
            comment_form = TicketCommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.ticket = ticket
                comment.author = request.user
                comment.save()
                messages.success(request, 'Комментарий добавлен.')
                return redirect('ticket_detail', pk=pk)
        
        elif 'rating' in request.POST and ticket.customer == request.user:
            rating_form = TicketRatingForm(request.POST, instance=ticket)
            if rating_form.is_valid():
                rating_form.save()
                messages.success(request, 'Спасибо за оценку!')
                return redirect('ticket_detail', pk=pk)
    
    is_customer = request.user.is_authenticated and request.user == ticket.customer

    return render(request, 'tickets/detail.html', {
        'ticket': ticket,
        'comments': comments,
        'attachments': attachments,
        'history': history,
        'comment_form': comment_form,
        'rating_form': rating_form,
        'is_customer': is_customer,
    })


@login_required
def engineer_dashboard(request):
    if request.user.role not in ('engineer', 'admin', 'dispatcher'):
        messages.error(request, 'У вас нет доступа.')
        return redirect('home')
    
    if request.user.role == 'admin' or request.user.role == 'dispatcher':
        tickets = Ticket.objects.filter(status__in=('assigned', 'in_progress', 'parts_needed'))
    else:
        # Инженеры видят свои заявки И новые неназначенные
        tickets = Ticket.objects.filter(
            Q(assigned_engineer=request.user) | Q(status='new', assigned_engineer__isnull=True)
        ).distinct()
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    search = request.GET.get('search', '')
    if search:
        tickets = tickets.filter(Q(ticket_number__icontains=search) | Q(description__icontains=search) | Q(address__icontains=search))
    
    # Calendar data
    calendar_tickets = Ticket.objects.filter(
        assigned_engineer=request.user,
        estimated_time__isnull=False
    ).order_by('estimated_time')[:30]
    
    scheduled_tickets = calendar_tickets
    
    return render(request, 'tickets/engineer_dashboard.html', {
        'tickets': tickets,
        'status_filter': status_filter,
        'search': search,
        'calendar_tickets': calendar_tickets,
        'scheduled_tickets': scheduled_tickets,
        'total_assigned': tickets.count(),
        'in_progress_count': tickets.filter(status='in_progress').count(),
        'completed_today': tickets.filter(status='completed', completed_at__date=timezone.now().date()).count(),
        'status_choices': Ticket.STATUS_CHOICES,
    })


@login_required
def ticket_update_status(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.user.role not in ('engineer', 'dispatcher', 'admin'):
        messages.error(request, 'У вас нет прав.')
        return redirect('home')
    
    if request.method == 'POST':
        old_status = ticket.status
        form = TicketStatusForm(request.POST, instance=ticket)
        if form.is_valid():
            updated_ticket = form.save()
            
            if old_status != updated_ticket.status:
                TicketHistory.objects.create(
                    ticket=updated_ticket,
                    user=request.user,
                    action='Статус изменён',
                    old_value=dict(Ticket.STATUS_CHOICES).get(old_status, old_status),
                    new_value=dict(Ticket.STATUS_CHOICES).get(updated_ticket.status, updated_ticket.status)
                )
                
                from notifications.utils import create_notification
                create_notification(
                    ticket=updated_ticket,
                    notification_type='status_changed',
                    message=f'Статус заявки #{updated_ticket.ticket_number} изменён на «{updated_ticket.get_status_display()}»'
                )
            
            messages.success(request, f'Заявка #{updated_ticket.ticket_number} обновлена.')
            return redirect('ticket_detail', pk=pk)
    else:
        form = TicketStatusForm(instance=ticket)
        form.fields['assigned_engineer'].queryset = User.objects.filter(role='engineer')
    
    return render(request, 'tickets/update_status.html', {
        'ticket': ticket, 'form': form
    })


@login_required
def dispatcher_kanban(request):
    if request.user.role not in ('dispatcher', 'admin'):
        messages.error(request, 'У вас нет доступа.')
        return redirect('home')
    
    engineers = User.objects.filter(role='engineer')
    all_tickets = Ticket.objects.all().select_related('assigned_engineer', 'customer')
    
    new_tickets = all_tickets.filter(status='new')
    assigned_tickets = all_tickets.filter(status='assigned')
    in_progress_tickets = all_tickets.filter(status='in_progress')
    parts_tickets = all_tickets.filter(status='parts_needed')
    awaiting_tickets = all_tickets.filter(status='awaiting_confirmation')
    completed_tickets = all_tickets.filter(status='completed')
    rejected_tickets = all_tickets.filter(status='rejected')
    
    return render(request, 'tickets/kanban.html', {
        'new_tickets': new_tickets,
        'assigned_tickets': assigned_tickets,
        'in_progress_tickets': in_progress_tickets,
        'parts_tickets': parts_tickets,
        'awaiting_tickets': awaiting_tickets,
        'completed_tickets': completed_tickets,
        'rejected_tickets': rejected_tickets,
        'engineers': engineers,
        'status_choices': Ticket.STATUS_CHOICES,
    })


@login_required
@require_POST
def assign_engineer(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.user.role not in ('dispatcher', 'admin'):
        return JsonResponse({'error': 'Forbidden'}, status=403)
    
    engineer_id = request.POST.get('engineer_id')
    if engineer_id:
        engineer = get_object_or_404(User, pk=engineer_id, role='engineer')
        old_engineer = ticket.assigned_engineer
        ticket.assigned_engineer = engineer
        ticket.status = 'assigned'
        ticket.save()
        
        TicketHistory.objects.create(
            ticket=ticket,
            user=request.user,
            action='Назначен инженер',
            old_value=str(old_engineer) if old_engineer else 'Не назначен',
            new_value=str(engineer)
        )
        
        from notifications.utils import create_notification
        create_notification(
            ticket=ticket,
            notification_type='assigned',
            message=f'Заявка #{ticket.ticket_number} назначена на {engineer.full_name}'
        )
        
        return JsonResponse({'success': True, 'engineer_name': engineer.full_name})
    return JsonResponse({'error': 'No engineer_id'}, status=400)

@login_required
@require_POST
def ticket_change_status_ajax(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.user.role not in ('dispatcher', 'admin'):
        return JsonResponse({'error': 'Forbidden'}, status=403)
    
    new_status = request.POST.get('status', '')
    valid_statuses = [s[0] for s in Ticket.STATUS_CHOICES]
    
    if new_status not in valid_statuses:
        return JsonResponse({'error': 'Invalid status'}, status=400)
    
    old_status = ticket.status
    ticket.status = new_status
    
    # Если назначен инженер при смене на "assigned"
    if new_status == 'assigned' and not ticket.assigned_engineer:
        engineer_id = request.POST.get('engineer_id')
        if engineer_id:
            ticket.assigned_engineer = get_object_or_404(User, pk=engineer_id, role='engineer')
    
    # Установка даты завершения
    if new_status == 'completed' and not ticket.completed_at:
        ticket.completed_at = timezone.now()
    
    ticket.save()
    
    # Запись в историю
    TicketHistory.objects.create(
        ticket=ticket,
        user=request.user,
        action='Статус изменён (канбан)',
        old_value=dict(Ticket.STATUS_CHOICES).get(old_status, old_status),
        new_value=dict(Ticket.STATUS_CHOICES).get(new_status, new_status)
    )
    
    from notifications.utils import create_notification
    create_notification(
        ticket=ticket,
        notification_type='status_changed',
        message=f'Статус заявки #{ticket.ticket_number} изменён на «{ticket.get_status_display()}»'
    )
    
    return JsonResponse({'success': True, 'new_status': new_status, 'ticket_id': pk})

@login_required
def ticket_delete_view(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Только диспетчер, админ или владелец заявки
    if request.user.role not in ('dispatcher', 'admin') and request.user != ticket.customer:
        messages.error(request, 'У вас нет прав для удаления этой заявки.')
        return redirect('ticket_detail', pk=pk)
    
    # Можно удалить только завершённые или отклонённые заявки
    if ticket.status not in ('completed', 'rejected'):
        messages.error(request, 'Удалять можно только заявки со статусом "Завершена" или "Отклонена".')
        return redirect('ticket_detail', pk=pk)
    
    if request.method == 'POST':
        ticket_number = ticket.ticket_number
        ticket.delete()
        messages.success(request, f'Заявка #{ticket_number} успешно удалена.')
        return redirect('home')
    
    return render(request, 'tickets/delete_confirm.html', {'ticket': ticket})

# ===== PAYMENT VIEWS (СБП QR-код) =====

def payment_create_view(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)

    if request.user.is_authenticated:
        is_customer = request.user == ticket.customer
        is_staff = request.user.role in ('dispatcher', 'admin')
        if not (is_customer or is_staff):
            messages.error(request, 'У вас нет доступа к оплате этой заявки.')
            return redirect('home')
    else:
        messages.error(request, 'Войдите в систему для оплаты.')
        return redirect('login')

    if not ticket.price or ticket.price <= 0:
        messages.error(request, 'Для этой заявки не указана стоимость. Обратитесь к диспетчеру.')
        return redirect('ticket_detail', pk=pk)

    existing = Payment.objects.filter(
        ticket=ticket, status='pending'
    ).order_by('-created_at').first()

    if existing:
        return redirect('payment_detail', payment_id=existing.payment_id)

    description = f'Оплата заявки #{ticket.ticket_number}'
    if ticket.service_category:
        description += f' ({ticket.service_category.name})'

    payment = Payment.objects.create(
        ticket=ticket,
        amount=ticket.price,
        description=description,
        payer_name=request.user.get_full_name() if request.user.is_authenticated else (ticket.guest_name or ''),
        payer_email=request.user.email if request.user.is_authenticated else (ticket.guest_email or ''),
        payer_phone=request.user.phone if request.user.is_authenticated else (ticket.guest_phone or ''),
    )

    return redirect('payment_detail', payment_id=payment.payment_id)


def payment_detail_view(request, payment_id):
    payment = get_object_or_404(Payment, payment_id=payment_id)

    if payment.status == 'pending' and payment.expires_at and timezone.now() > payment.expires_at:
        payment.status = 'expired'
        payment.save()

    if payment.status == 'expired':
        messages.warning(request, 'Срок действия этого платежа истёк. Создайте новый.')
    elif payment.status == 'cancelled':
        messages.warning(request, 'Этот платёж был отменён.')
    elif payment.status == 'completed':
        messages.info(request, 'Этот платёж уже оплачен.')
    elif payment.status == 'on_site':
        messages.info(request, 'Выбрана оплата на месте.')

    is_active = payment.status == 'pending'
    if is_active:
        qr_base64 = generate_sbp_qr_base64(
            amount=payment.amount,
            payment_id=payment.payment_id,
            description=payment.description
        )
    else:
        qr_base64 = generate_sbp_qr_phone_only()
        qr_details = None

    recipient = get_recipient_details()

    return render(request, 'tickets/payment.html', {
        'payment': payment,
        'ticket': payment.ticket,
        'qr_base64': qr_base64,
        'is_active': is_active,
        'recipient': recipient,
    })


def payment_confirm_view(request, payment_id):
    payment = get_object_or_404(Payment, payment_id=payment_id)

    if payment.status != 'pending':
        messages.warning(request, 'Этот платёж уже обработан.')
        return redirect('payment_detail', payment_id=payment.payment_id)

    if request.user.is_authenticated:
        if payment.payer_email and request.user.email != payment.payer_email:
            if request.user != payment.ticket.customer and request.user.role not in ('dispatcher', 'admin'):
                messages.error(request, 'У вас нет доступа.')
                return redirect('home')

    if request.method == 'POST':
        payment.status = 'completed'
        payment.save()

        TicketHistory.objects.create(
            ticket=payment.ticket,
            user=request.user if request.user.is_authenticated else None,
            action='Оплата получена',
            old_value='Ожидает',
            new_value=f'{payment.amount} ₽'
        )

        try:
            _send_payment_receipt(payment)
        except Exception:
            pass

        from notifications.utils import create_notification
        create_notification(
            ticket=payment.ticket,
            notification_type='status_changed',
            message=f'Получена оплата {payment.amount} ₽ по заявке #{payment.ticket.ticket_number}'
        )

        messages.success(request, f'Оплата {payment.amount} ₽ подтверждена! Чек отправлен на email.')
        return redirect('payment_success', payment_id=payment.payment_id)

    return redirect('payment_detail', payment_id=payment.payment_id)


def payment_on_site_view(request, payment_id):
    payment = get_object_or_404(Payment, payment_id=payment_id)

    if payment.status != 'pending':
        messages.warning(request, 'Этот платёж уже обработан.')
        return redirect('payment_detail', payment_id=payment.payment_id)

    payment.status = 'on_site'
    payment.save()

    TicketHistory.objects.create(
        ticket=payment.ticket,
        user=request.user if request.user.is_authenticated else None,
        action='Способ оплаты',
        old_value='Онлайн (СБП)',
        new_value='На месте'
    )

    messages.info(request, 'Выбрана оплата на месте. Оплата наличными или картой при визите мастера.')
    return redirect('payment_detail', payment_id=payment.payment_id)


def payment_success_view(request, payment_id):
    payment = get_object_or_404(Payment, payment_id=payment_id)

    if payment.status != 'completed':
        messages.warning(request, 'Этот платёж ещё не оплачен.')
        return redirect('payment_detail', payment_id=payment.payment_id)

    return render(request, 'tickets/payment_success.html', {
        'payment': payment,
        'ticket': payment.ticket,
    })


def _send_payment_receipt(payment):
    if not payment.payer_email and payment.ticket:
        if payment.ticket.customer and payment.ticket.customer.email:
            payment.payer_email = payment.ticket.customer.email
        elif payment.ticket.guest_email:
            payment.payer_email = payment.ticket.guest_email

    if not payment.payer_email:
        return

    from django.conf import settings
    from django.core.mail import send_mail
    from notifications.models import EmailLog

    subject = f'Квитанция об оплате — {payment.payment_id}'
    sep = '=' * 40
    paid_date = payment.paid_at.strftime("%d.%m.%Y %H:%M") if payment.paid_at else timezone.now().strftime("%d.%m.%Y %H:%M")
    body = (
        'Здравствуйте!\n\n'
        f'Подтверждена оплата по заявке #{payment.ticket.ticket_number}\n\n'
        f'{sep}\n'
        'КВИТАНЦИЯ\n'
        f'{sep}\n\n'
        f'ID платежа: {payment.payment_id}\n'
        f'Заявка: #{payment.ticket.ticket_number}\n'
        f'Сумма: {payment.amount} руб.\n'
        f'Назначение: {payment.description}\n'
        f'Дата оплаты: {paid_date}\n\n'
        f'Получатель:\n'
        f'  {Payment.RECIPIENT_NAME}\n'
        f'  Телефон: {Payment.RECIPIENT_PHONE}\n'
        f'  Банк: {Payment.RECIPIENT_BANK}\n'
        '  Способ оплаты: СБП (Система Быстрых Платежей)\n\n'
        f'{sep}\n\n'
        'Спасибо за оплату!\n\n'
        'С уважением,\n'
        'ООО "ТатАИСнефть"\n'
        'Тел: +7 (8553) 30-50-00\n'
        'https://tatais.ru'
    )

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[payment.payer_email],
            fail_silently=False,
        )
        payment.email_sent = True
        payment.save(update_fields=['email_sent'])
        EmailLog.objects.create(
            recipient=payment.payer_email, subject=subject,
            body=body, status='sent'
        )
    except Exception as e:
        EmailLog.objects.create(
            recipient=payment.payer_email, subject=subject,
            body=body, status=f'failed: {str(e)[:200]}'
        )