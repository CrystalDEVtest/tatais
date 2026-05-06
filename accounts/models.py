from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('subscriber', 'Абонент'),
        ('engineer', 'Инженер'),
        ('dispatcher', 'Диспетчер'),
        ('admin', 'Администратор'),
    )
    CITY_CHOICES = (
        ('Альметьевск', 'Альметьевск'),
        ('Бугульма', 'Бугульма'),
        ('Лениногорск', 'Лениногорск'),
        ('Чистополь', 'Чистополь'),
        ('Нурлат', 'Нурлат'),
        ('Азнакаево', 'Азнакаево'),
        ('Бавлы', 'Бавлы'),
        ('Заинск', 'Заинск'),
        ('Менделеевск', 'Менделеевск'),
        ('Джалиль', 'Джалиль'),
        ('Елабуга', 'Елабуга'),
        ('Нижнекамск', 'Нижнекамск'),
        ('Другой', 'Другой'),
    )

    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    patronymic = models.CharField(max_length=50, blank=True, verbose_name='Отчество')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='subscriber', verbose_name='Роль')
    city = models.CharField(max_length=50, choices=CITY_CHOICES, blank=True, verbose_name='Город')
    address = models.TextField(blank=True, verbose_name='Адрес')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.last_name} {self.first_name} ({self.get_role_display()})'

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name, self.patronymic]
        return ' '.join(p for p in parts if p)
