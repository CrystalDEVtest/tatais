from django.db import models
from django.conf import settings


class Notification(models.Model):
    TYPE_CHOICES = (
        ('ticket_created', 'Заявка создана'),
        ('status_changed', 'Статус изменён'),
        ('assigned', 'Назначение на инженера'),
        ('comment_added', 'Новый комментарий'),
        ('ticket_completed', 'Заявка завершена'),
        ('system', 'Системное уведомление'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications', verbose_name='Пользователь')
    ticket = models.ForeignKey('tickets.Ticket', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications', verbose_name='Заявка')
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, verbose_name='Тип')
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    message = models.TextField(verbose_name='Сообщение')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class EmailLog(models.Model):
    recipient = models.EmailField(verbose_name='Получатель')
    subject = models.CharField(max_length=255, verbose_name='Тема')
    body = models.TextField(verbose_name='Тело письма')
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отправки')
    status = models.CharField(max_length=20, default='sent', verbose_name='Статус')
    
    class Meta:
        verbose_name = 'Лог email'
        verbose_name_plural = 'Логи email'
    
    def __str__(self):
        return f'{self.recipient} — {self.subject}'


class SMSLog(models.Model):
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    message = models.TextField(verbose_name='Сообщение')
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отправки')
    status = models.CharField(max_length=20, default='sent', verbose_name='Статус')
    
    class Meta:
        verbose_name = 'Лог SMS'
        verbose_name_plural = 'Логи SMS'
    
    def __str__(self):
        return f'{self.phone} — {self.sent_at}'
