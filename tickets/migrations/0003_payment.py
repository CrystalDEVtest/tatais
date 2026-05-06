from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0002_ticket_payment_method_ticket_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_id', models.CharField(max_length=50, unique=True, verbose_name='ID платежа')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Сумма')),
                ('description', models.CharField(max_length=255, verbose_name='Назначение платежа')),
                ('status', models.CharField(choices=[
                    ('pending', 'Ожидает оплаты'),
                    ('completed', 'Оплачено'),
                    ('cancelled', 'Отменено'),
                    ('on_site', 'Оплата на месте'),
                    ('expired', 'Истёк'),
                ], default='pending', max_length=20, verbose_name='Статус')),
                ('payer_name', models.CharField(blank=True, max_length=255, verbose_name='Имя плательщика')),
                ('payer_email', models.EmailField(blank=True, verbose_name='Email плательщика')),
                ('payer_phone', models.CharField(blank=True, max_length=20, verbose_name='Телефон плательщика')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('paid_at', models.DateTimeField(null=True, blank=True, verbose_name='Дата оплаты')),
                ('expires_at', models.DateTimeField(null=True, blank=True, verbose_name='Срок действия')),
                ('email_sent', models.BooleanField(default=False, verbose_name='Чек отправлен')),
                ('ticket', models.ForeignKey(on_delete=models.CASCADE, related_name='payments', to='tickets.ticket', verbose_name='Заявка')),
            ],
            options={
                'verbose_name': 'Платёж',
                'verbose_name_plural': 'Платежи',
                'ordering': ['-created_at'],
            },
        ),
    ]