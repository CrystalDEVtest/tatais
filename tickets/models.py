from django.db import models
from django.conf import settings
from django.utils import timezone


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='Категория')
    description = models.TextField(blank=True, verbose_name='Описание')
    
    class Meta:
        verbose_name = 'Категория услуги'
        verbose_name_plural = 'Категории услуг'
    
    def __str__(self):
        return self.name


class Ticket(models.Model):
    STATUS_CHOICES = (
        ('new', 'Новая'),
        ('assigned', 'Назначена инженеру'),
        ('in_progress', 'В работе'),
        ('parts_needed', 'Требуется запчасть'),
        ('awaiting_confirmation', 'Ожидает подтверждения от клиента'),
        ('completed', 'Завершена'),
        ('rejected', 'Отклонена'),
    )
    PRIORITY_CHOICES = (
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
        ('critical', 'Критический'),
    )
    
    ticket_number = models.CharField(max_length=20, unique=True, verbose_name='Номер заявки')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets', verbose_name='Абонент')
    
    # Guest fields (for unregistered users)
    guest_name = models.CharField(max_length=100, blank=True, verbose_name='Имя (гостевая)')
    guest_phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон (гостевая)')
    guest_email = models.EmailField(blank=True, verbose_name='Email (гостевая)')
    
    # Ticket details
    service_category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, verbose_name='Категория услуги')
    service_type = models.CharField(max_length=100, verbose_name='Тип услуги')
    description = models.TextField(verbose_name='Описание проблемы')
    address = models.TextField(verbose_name='Адрес объекта')
    city = models.CharField(max_length=50, verbose_name='Город')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name='Приоритет')
    
    # Engineer
    assigned_engineer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets', verbose_name='Назначенный инженер')
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата завершения')
    estimated_time = models.DateTimeField(null=True, blank=True, verbose_name='Плановое время выполнения')
    time_spent = models.DurationField(null=True, blank=True, verbose_name='Затраченное время')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Стоимость услуги (руб.)')
    # Payment method
    payment_method = models.CharField(
        max_length=20, default='none',
        choices=(
            ('none', 'Не указан'),
            ('online', 'Онлайн (СБП)'),
            ('onsite', 'На месте'),
        ),
        verbose_name='Способ оплаты'
    )
    
    # Location
    latitude = models.FloatField(null=True, blank=True, verbose_name='Широта')
    longitude = models.FloatField(null=True, blank=True, verbose_name='Долгота')
    
        # Price
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Стоимость услуги (₽)')
    
    # Rating
    customer_rating = models.IntegerField(null=True, blank=True, verbose_name='Оценка клиента (1-5)')
    customer_feedback = models.TextField(blank=True, verbose_name='Отзыв клиента')
    
    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Заявка #{self.ticket_number}'
    
    def save(self, *args, **kwargs):
        if not self.ticket_number:
            from datetime import datetime
            today = timezone.now()
            prefix = today.strftime("%%Y%%m%%d")  # will be formatted below
            prefix = today.strftime("%Y%m%d")
            for attempt in range(5):
                last = Ticket.objects.filter(
                    ticket_number__startswith=f'TA-{prefix}'
                ).order_by('-ticket_number').first()
                if last:
                    try:
                        num = int(last.ticket_number.split('-')[-1]) + 1
                    except (ValueError, IndexError):
                        num = Ticket.objects.filter(
                            created_at__date=today.date()
                        ).count() + 1
                else:
                    num = 1
                self.ticket_number = f'TA-{prefix}-{num:04d}'
                try:
                    super().save(*args, **kwargs)
                    return
                except Exception:
                    if attempt == 4:
                        raise
                    continue
        else:
            super().save(*args, **kwargs)
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
            Ticket.objects.filter(pk=self.pk).update(completed_at=self.completed_at)


class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments', verbose_name='Заявка')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Автор')
    text = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_system = models.BooleanField(default=False, verbose_name='Системное сообщение')
    
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']
    
    def __str__(self):
        return f'Комментарий к #{self.ticket.ticket_number}'


class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments', verbose_name='Заявка')
    file = models.FileField(upload_to='ticket_attachments/%Y/%m/', verbose_name='Файл')
    filename = models.CharField(max_length=255, verbose_name='Имя файла')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Загрузил')
    
    class Meta:
        verbose_name = 'Вложение'
        verbose_name_plural = 'Вложения'
    
    def __str__(self):
        return self.filename


class TicketHistory(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='history', verbose_name='Заявка')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Пользователь')
    action = models.CharField(max_length=255, verbose_name='Действие')
    old_value = models.CharField(max_length=255, blank=True, verbose_name='Старое значение')
    new_value = models.CharField(max_length=255, blank=True, verbose_name='Новое значение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата изменения')
    
    class Meta:
        verbose_name = 'Запись истории'
        verbose_name_plural = 'История изменений'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.action} — #{self.ticket.ticket_number}'

class Payment(models.Model):
    """Платёж за услугу через СБП (QR-код)."""
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Ожидает оплаты'),
        ('completed', 'Оплачено'),
        ('cancelled', 'Отменено'),
        ('on_site', 'Оплата на месте'),
        ('expired', 'Истёк'),
    )

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='payments', verbose_name='Заявка')
    payment_id = models.CharField(max_length=50, unique=True, verbose_name='ID платежа')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма (₽)')
    description = models.CharField(max_length=255, verbose_name='Назначение платежа')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name='Статус')
    payer_name = models.CharField(max_length=255, blank=True, verbose_name='Имя плательщика')
    payer_email = models.EmailField(blank=True, verbose_name='Email плательщика')
    payer_phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон плательщика')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата оплаты')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='Срок действия')
    email_sent = models.BooleanField(default=False, verbose_name='Чек отправлен')

    RECIPIENT_PHONE = '+79033449080'
    RECIPIENT_NAME = 'Морев Никита Алексеевич'
    RECIPIENT_BANK = 'Т-Банк'

    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.payment_id} — {self.amount} ₽'

    def save(self, *args, **kwargs):
        if not self.payment_id:
            import uuid
            self.payment_id = f'PAY-{uuid.uuid4().hex[:12].upper()}'
        if not self.expires_at and self.status == 'pending':
            from datetime import timedelta
            self.expires_at = timezone.now() + timedelta(hours=24)
        if self.status == 'completed' and not self.paid_at:
            self.paid_at = timezone.now()
        super().save(*args, **kwargs)