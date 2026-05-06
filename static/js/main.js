/* ============================================
   ТатАИСнефть — Система управления заявками
   Основные скрипты
   ============================================ */

// ---- Loading Overlay ----
document.addEventListener('DOMContentLoaded', function() {
    const loader = document.querySelector('.loading-overlay');
    if (loader) {
        setTimeout(() => {
            loader.classList.add('hidden');
        }, 500);
    }
});

// ---- Scroll Animations ----
function initScrollAnimations() {
    const elements = document.querySelectorAll('.fade-in, .slide-up, .slide-left, .scale-in');
    
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.classList.add('visible');
                    }, index * 100);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
        
        elements.forEach(el => observer.observe(el));
    } else {
        elements.forEach(el => el.classList.add('visible'));
    }
}

// ---- Navbar Scroll Effect ----
function initNavbarScroll() {
    const navbar = document.querySelector('.navbar-custom');
    if (!navbar) return;
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

// ---- Animated Counters ----
function animateCounters() {
    const counters = document.querySelectorAll('.counter-value');
    
    if (!counters.length) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const target = parseInt(el.getAttribute('data-target'));
                const suffix = el.getAttribute('data-suffix') || '';
                const duration = 2000;
                const step = target / (duration / 16);
                let current = 0;
                
                const timer = setInterval(() => {
                    current += step;
                    if (current >= target) {
                        current = target;
                        clearInterval(timer);
                    }
                    el.textContent = Math.floor(current) + suffix;
                }, 16);
                
                observer.unobserve(el);
            }
        });
    }, { threshold: 0.5 });
    
    counters.forEach(counter => observer.observe(counter));
}

// ---- Smooth Scroll ----
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            e.preventDefault();
            const target = document.querySelector(targetId);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// ---- AJAX Notification Mark Read ----
function markNotificationRead(notifId, element) {
    fetch(`/notifications/mark-read/${notifId}/`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && element) {
            element.classList.remove('unread');
            // Update badge count
            const badge = document.querySelector('.notification-badge');
            if (badge) {
                let count = parseInt(badge.textContent);
                count = Math.max(0, count - 1);
                badge.textContent = count;
                if (count === 0) {
                    badge.style.display = 'none';
                }
            }
        }
    })
    .catch(err => console.error('Error:', err));
}

// ---- Assign Engineer (AJAX) ----
function assignEngineer(ticketId, engineerId, buttonEl) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (!csrfToken) {
        alert('CSRF token not found');
        return;
    }
    
    fetch(`/tickets/${ticketId}/assign/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `engineer_id=${engineerId}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (buttonEl) {
                buttonEl.textContent = data.engineer_name;
                buttonEl.classList.remove('btn-outline-warning');
                buttonEl.classList.add('btn-success');
            }
            // Show success message
            showToast('Инженер назначен: ' + data.engineer_name, 'success');
        } else {
            showToast('Ошибка при назначении инженера', 'error');
        }
    })
    .catch(err => {
        console.error('Error:', err);
        showToast('Ошибка сети', 'error');
    });
}

// ---- Toast Notifications ----
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container') || createToastContainer();
    
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    const colors = {
        success: '#2e7d32',
        error: '#c62828',
        warning: '#e65100',
        info: '#1565c0'
    };
    
    const toast = document.createElement('div');
    toast.style.cssText = `
        display: flex; align-items: center; gap: 0.75rem;
        padding: 1rem 1.5rem; border-radius: 12px;
        background: white; box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        border-left: 4px solid ${colors[type]};
        transform: translateX(120%); transition: transform 0.3s ease;
        margin-bottom: 0.5rem; max-width: 400px;
    `;
    toast.innerHTML = `
        <i class="${icons[type]}" style="color: ${colors[type]}; font-size: 1.2rem;"></i>
        <span style="font-size: 0.9rem; color: #333;">${message}</span>
    `;
    
    container.appendChild(toast);
    
    requestAnimationFrame(() => {
        toast.style.transform = 'translateX(0)';
    });
    
    setTimeout(() => {
        toast.style.transform = 'translateX(120%)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = `
        position: fixed; top: 80px; right: 20px; z-index: 99999;
        display: flex; flex-direction: column;
    `;
    document.body.appendChild(container);
    return container;
}

// ---- Phone Mask ----
function initPhoneMask() {
    const phoneInputs = document.querySelectorAll('input[name="phone"], input[name="guest_phone"]');
    
    phoneInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 0) {
                if (value[0] === '8') value = '7' + value.slice(1);
                if (value[0] !== '7') value = '7' + value;
                
                let formatted = '+7';
                if (value.length > 1) formatted += ' (' + value.slice(1, 4);
                if (value.length >= 4) formatted += ') ' + value.slice(4, 7);
                if (value.length >= 7) formatted += '-' + value.slice(7, 9);
                if (value.length >= 9) formatted += '-' + value.slice(9, 11);
                
                e.target.value = formatted;
            }
        });
    });
}

// ---- File Upload Preview ----
function initFilePreview() {
    const fileInput = document.getElementById('file-upload');
    const previewContainer = document.getElementById('file-preview');
    
    if (!fileInput || !previewContainer) return;
    
    fileInput.addEventListener('change', function() {
        previewContainer.innerHTML = '';
        Array.from(this.files).forEach(file => {
            const item = document.createElement('div');
            item.className = 'file-preview-item d-flex align-items-center gap-2 p-2 mb-2 bg-light rounded';
            
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    item.innerHTML = `
                        <img src="${e.target.result}" class="rounded" style="width:50px;height:50px;object-fit:cover;">
                        <span class="small">${file.name}</span>
                    `;
                };
                reader.readAsDataURL(file);
            } else {
                item.innerHTML = `
                    <i class="fas fa-file text-muted"></i>
                    <span class="small">${file.name}</span>
                `;
            }
            
            previewContainer.appendChild(item);
        });
    });
}

// ---- Chart.js Initialization ----
function initCharts() {
    // Daily Tickets Chart
    const dailyCtx = document.getElementById('dailyChart')?.getContext('2d');
    if (dailyCtx && typeof dailyLabels !== 'undefined' && typeof dailyValues !== 'undefined') {
        new Chart(dailyCtx, {
            type: 'line',
            data: {
                labels: dailyLabels,
                datasets: [{
                    label: 'Заявки по дням',
                    data: dailyValues,
                    borderColor: '#009846',
                    backgroundColor: 'rgba(0, 152, 70, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2,
                    pointRadius: 4,
                    pointBackgroundColor: '#009846',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true, ticks: { stepSize: 1 } }
                }
            }
        });
    }
    
    // Status Chart
    const statusCtx = document.getElementById('statusChart')?.getContext('2d');
    if (statusCtx && typeof statusData !== 'undefined') {
        const statusLabels = {
            'new': 'Новая', 'assigned': 'Назначена', 'in_progress': 'В работе',
            'parts_needed': 'Запчасть', 'awaiting_confirmation': 'Ожидание',
            'completed': 'Завершена', 'rejected': 'Отклонена'
        };
        const statusColors = ['#1565c0', '#00838f', '#e65100', '#7b1fa2', '#283593', '#2e7d32', '#c62828'];
        
        new Chart(statusCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(statusData).map(k => statusLabels[k] || k),
                datasets: [{
                    data: Object.values(statusData),
                    backgroundColor: statusColors,
                    borderWidth: 0,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { padding: 15, font: { size: 11 } } }
                }
            }
        });
    }
    
    // Service Chart
    const serviceCtx = document.getElementById('serviceChart')?.getContext('2d');
    if (serviceCtx && typeof serviceData !== 'undefined') {
        const serviceLabels = {
            'internet': 'Интернет', 'tv': 'ТВ', 'phone': 'Телефония',
            'iptv': 'Интернет+ТВ', 'internet_phone': 'Интернет+Тел',
            'triple': 'Комплекс', 'other': 'Другое'
        };
        
        new Chart(serviceCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(serviceData).map(k => serviceLabels[k] || k),
                datasets: [{
                    label: 'Количество заявок',
                    data: Object.values(serviceData),
                    backgroundColor: '#009846',
                    borderRadius: 8,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true, ticks: { stepSize: 1 } }
                }
            }
        });
    }
}

// ---- Back to Top ----
function initBackToTop() {
    const btn = document.getElementById('backToTop');
    if (!btn) return;
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            btn.style.display = 'flex';
            btn.style.opacity = '1';
        } else {
            btn.style.opacity = '0';
            setTimeout(() => { btn.style.display = 'none'; }, 300);
        }
    });
    
    btn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// ---- Initialize Everything ----
document.addEventListener('DOMContentLoaded', function() {
    initScrollAnimations();
    initNavbarScroll();
    animateCounters();
    initSmoothScroll();
    initPhoneMask();
    initFilePreview();
    initCharts();
    initBackToTop();
});
