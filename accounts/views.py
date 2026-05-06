from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileForm
from .models import User
from tickets.models import Ticket


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.first_name}!')
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('home')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'subscriber'
            user.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    user_tickets = Ticket.objects.filter(customer=request.user).order_by('-created_at')[:10]
    return render(request, 'accounts/profile.html', {'form': form, 'tickets': user_tickets})


@login_required
def change_password_view(request):
    from .forms import ChangePasswordForm
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password'])
            request.user.save()
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Пароль успешно изменён.')
            return redirect('profile')
    else:
        form = ChangePasswordForm()
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def subscriber_dashboard(request):
    if request.user.role not in ('subscriber', 'admin'):
        messages.error(request, 'У вас нет доступа к этой странице.')
        return redirect('home')
    tickets = Ticket.objects.filter(customer=request.user).order_by('-created_at')
    active_tickets = tickets.filter(status__in=('new', 'assigned', 'in_progress', 'parts_needed', 'awaiting_confirmation'))
    completed_tickets = tickets.filter(status='completed')
    return render(request, 'accounts/subscriber_dashboard.html', {
        'tickets': tickets,
        'active_tickets': active_tickets,
        'completed_tickets': completed_tickets,
        'completed_count': completed_tickets.count(),
        'total_count': tickets.count(),
    })
