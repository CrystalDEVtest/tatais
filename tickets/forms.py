from django import forms
from django.conf import settings
from .models import Ticket, TicketComment, TicketAttachment, ServiceCategory
from accounts.models import User


class TicketCreateForm(forms.ModelForm):
    SERVICE_TYPE_CHOICES = (
        ('', 'Выберите тип услуги'),
        ('internet', 'Интернет'),
        ('tv', 'Телевидение'),
        ('phone', 'Телефония'),
        ('iptv', 'Интернет + ТВ'),
        ('internet_phone', 'Интернет + Телефон'),
        ('triple', 'Интернет + ТВ + Телефон'),
        ('other', 'Другое'),
    )
    
    service_type = forms.ChoiceField(choices=SERVICE_TYPE_CHOICES, widget=forms.Select(attrs={
        'class': 'form-select'
    }))
    city = forms.ChoiceField(choices=[('', 'Выберите город')] + list(User.CITY_CHOICES), widget=forms.Select(attrs={
        'class': 'form-select'
    }))
    
    class Meta:
        model = Ticket
        fields = ('service_category', 'service_type', 'description', 'address', 'city', 'price')
        widgets = {
            'service_category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Опишите проблему подробно...'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Улица, дом, квартира'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'min': '0', 'readonly': 'readonly'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service_category'].required = False
        self.fields['service_category'].empty_label = 'Выберите категорию'


class GuestTicketCreateForm(forms.ModelForm):
    SERVICE_TYPE_CHOICES = (
        ('', 'Выберите тип услуги'),
        ('internet', 'Интернет'),
        ('tv', 'Телевидение'),
        ('phone', 'Телефония'),
        ('iptv', 'Интернет + ТВ'),
        ('internet_phone', 'Интернет + Телефон'),
        ('triple', 'Интернет + ТВ + Телефон'),
        ('other', 'Другое'),
    )
    
    guest_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ФИО'}))
    guest_phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (___) ___-__-__'}))
    guest_email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    service_type = forms.ChoiceField(choices=SERVICE_TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    city = forms.ChoiceField(choices=[('', 'Выберите город')] + list(User.CITY_CHOICES), widget=forms.Select(attrs={'class': 'form-select'}))
    
    class Meta:
        model = Ticket
        fields = ('service_category', 'service_type', 'description', 'address', 'city', 'price')
        widgets = {
            'service_category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Опишите проблему подробно...'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Улица, дом, квартира'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'min': '0', 'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service_category'].required = False
        self.fields['service_category'].empty_label = 'Выберите категорию'


class TicketCommentForm(forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Написать комментарий...'}),
        }


class TicketStatusForm(forms.ModelForm):
    price = forms.DecimalField(
        max_digits=10, decimal_places=2, required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00',
            'min': '0',
            'step': '0.01',
        }),
        label='Стоимость услуги (руб.)'
    )

    class Meta:
        model = Ticket
        fields = ('status', 'assigned_engineer', 'priority', 'estimated_time', 'price')
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_engineer': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'estimated_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class TicketRatingForm(forms.ModelForm):
    customer_rating = forms.ChoiceField(
        choices=[('', 'Выберите оценку')] + [(i, f'{i} звезд') for i in range(1, 6)],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Ticket
        fields = ('customer_rating', 'customer_feedback')
        widgets = {
            'customer_feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ваш отзыв о качестве обслуживания...'}),
        }
