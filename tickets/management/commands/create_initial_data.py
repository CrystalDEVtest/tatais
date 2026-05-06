"""
Скрипт создания начальных данных для системы.
Создаёт категории услуг, тестовых пользователей и статьи базы знаний.

Запуск: python manage.py create_initial_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tickets.models import ServiceCategory, Ticket, TicketHistory
from notifications.models import Notification
from knowledgebase.models import Category, Article
from datetime import timedelta
from django.utils import timezone
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Создание начальных данных для системы'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Создание начальных данных ==='))
        
        self.create_categories()
        self.create_users()
        self.create_knowledge_base()
        self.create_sample_tickets()
        
        self.stdout.write(self.style.SUCCESS('=== Готово! ==='))
    
    def create_categories(self):
        self.stdout.write('Создание категорий услуг...')
        
        categories = [
            ('Интернет', 'Проблемы с подключением к интернету, скорость, настройка роутера'),
            ('Телевидение', 'Проблемы с IPTV, настройка приставки, каналы'),
            ('Телефония', 'Проблемы с домашним телефоном, качество связи'),
            ('Оборудование', 'Замена, настройка и ремонт оборудования'),
            ('Подключение', 'Новое подключение услуг, переезд, перенос точки'),
            ('Другое', 'Прочие вопросы и обращения'),
        ]
        
        for name, desc in categories:
            ServiceCategory.objects.get_or_create(
                name=name,
                defaults={'description': desc}
            )
        
        self.stdout.write(self.style.SUCCESS(f'  Создано {len(categories)} категорий'))
    
    def create_users(self):
        self.stdout.write('Создание тестовых пользователей...')
        
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@tataisneft.ru',
                'password': 'admin123456',
                'first_name': 'Иван',
                'last_name': 'Петров',
                'patronymic': 'Сергеевич',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'city': 'Альметьевск',
                'phone': '+7 (917) 900-00-01',
            },
            {
                'username': 'dispatcher1',
                'email': 'dispatcher@tataisneft.ru',
                'password': 'disp123456',
                'first_name': 'Елена',
                'last_name': 'Сидорова',
                'patronymic': 'Алексеевна',
                'role': 'dispatcher',
                'is_staff': True,
                'city': 'Альметьевск',
                'phone': '+7 (917) 900-00-02',
            },
            {
                'username': 'engineer1',
                'email': 'engineer@tataisneft.ru',
                'password': 'eng123456',
                'first_name': 'Рустам',
                'last_name': 'Хасанов',
                'patronymic': 'Маратович',
                'role': 'engineer',
                'city': 'Альметьевск',
                'phone': '+7 (917) 900-00-03',
            },
            {
                'username': 'engineer2',
                'email': 'engineer2@tataisneft.ru',
                'password': 'eng123456',
                'first_name': 'Дмитрий',
                'last_name': 'Волков',
                'patronymic': 'Андреевич',
                'role': 'engineer',
                'city': 'Лениногорск',
                'phone': '+7 (917) 900-00-04',
            },
            {
                'username': 'engineer3',
                'email': 'engineer3@tataisneft.ru',
                'password': 'eng123456',
                'first_name': 'Анвар',
                'last_name': 'Нуриманов',
                'patronymic': 'Ринатович',
                'role': 'engineer',
                'city': 'Бугульма',
                'phone': '+7 (917) 900-00-05',
            },
            {
                'username': 'subscriber1',
                'email': 'subscriber@gmail.com',
                'password': 'sub123456',
                'first_name': 'Максим',
                'last_name': 'Иванов',
                'patronymic': 'Олегович',
                'role': 'subscriber',
                'city': 'Альметьевск',
                'phone': '+7 (917) 900-00-06',
                'address': 'ул. Ленина, д. 15, кв. 42',
            },
            {
                'username': 'subscriber2',
                'email': 'subscriber2@gmail.com',
                'password': 'sub123456',
                'first_name': 'Ольга',
                'last_name': 'Николаева',
                'patronymic': 'Владимировна',
                'role': 'subscriber',
                'city': 'Бугульма',
                'phone': '+7 (917) 900-00-07',
                'address': 'ул. Советская, д. 8, кв. 15',
            },
        ]
        
        created = 0
        for udata in users_data:
            user, is_created = User.objects.get_or_create(
                username=udata['username'],
                defaults={
                    'email': udata['email'],
                    'first_name': udata['first_name'],
                    'last_name': udata['last_name'],
                    'patronymic': udata['patronymic'],
                    'role': udata['role'],
                    'is_staff': udata.get('is_staff', False),
                    'is_superuser': udata.get('is_superuser', False),
                    'city': udata['city'],
                    'phone': udata['phone'],
                    'address': udata.get('address', ''),
                }
            )
            if is_created:
                user.set_password(udata['password'])
                user.save()
                created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  Создано {created} пользователей'))
        self.stdout.write('  Логин / пароль:')
        self.stdout.write('    admin / admin123456 (Администратор)')
        self.stdout.write('    dispatcher1 / disp123456 (Диспетчер)')
        self.stdout.write('    engineer1 / eng123456 (Инженер)')
        self.stdout.write('    engineer2 / eng123456 (Инженер)')
        self.stdout.write('    engineer3 / eng123456 (Инженер)')
        self.stdout.write('    subscriber1 / sub123456 (Абонент)')
        self.stdout.write('    subscriber2 / sub123456 (Абонент)')
    
    def create_knowledge_base(self):
        self.stdout.write('Создание базы знаний...')
        
        categories = [
            'Типовые неисправности интернета',
            'Настройка оборудования',
            'Работа с IPTV',
            'Телефония',
            'Инструкции для абонентов',
        ]
        
        created_cats = []
        for cat_name in categories:
            cat, _ = Category.objects.get_or_create(name=cat_name)
            created_cats.append(cat)
        
        articles = [
            {
                'category': created_cats[0],
                'title': 'Нет доступа к интернету — диагностика',
                'content': '''Если у вас нет доступа к интернету, выполните следующие шаги:

1. Проверьте индикаторы на роутере
   - Индикатор Power должен гореть постоянно
   - Индикатор Internet/WAN должен гореть или мигать
   - Индикаторы LAN должны гореть для подключённых устройств

2. Перезагрузите роутер
   - Отключите питание роутера на 30 секунд
   - Подключите обратно и подождите 2-3 минуты

3. Проверьте кабель
   - Убедитесь, что сетевой кабель надёжно подключён к роутеру и стене
   - Попробуйте заменить кабель на другой

4. Проверьте настройки сети
   - Перезагрузите компьютер/телефон
   - Забудьте Wi-Fi сеть и подключитесь заново
   - Проверьте, включён ли Wi-Fi

5. Обратитесь в техподдержку
   - Тел: 8(8553)305-000
   - Оставьте заявку через личный кабинет

Если проблема не решена, инженер выедет на объект в течение рабочего дня.''',
                'author': User.objects.filter(role='engineer').first(),
            },
            {
                'category': created_cats[0],
                'title': 'Низкая скорость интернета',
                'content': '''Если скорость интернета ниже ожидаемой:

1. Проверьте тарифный план — убедитесь, что ваш тариф соответствует ожидаемой скорости

2. Тест скорости
   - Используйте speedtest.net
   - Тестируйте по проводному подключению (LAN), не по Wi-Fi
   - Выполняйте тест несколько раз

3. Проверьте загрузку канала
   - Закройте все программы, использующие интернет (торренты, обновления)
   - Отключите другие устройства от сети

4. Wi-Fi проблемы
   - 2.4 ГГц — дальше, но медленнее
   - 5 ГГц — быстрее, но короче расстояние
   - Помехи от соседних сетей — смените канал

5. Оборудование
   - Роутер может не поддерживать высокую скорость (100+ Мбит/с)
   - Рекомендуем роутеры с поддержкой Gigabit Ethernet

Если скорость значительно ниже тарифа — обратитесь в техподдержку.''',
                'author': User.objects.filter(role='engineer').first(),
            },
            {
                'category': created_cats[1],
                'title': 'Настройка роутера TP-Link для ТатАИСнефть',
                'content': '''Инструкция по настройке роутера TP-Link:

1. Подключение
   - WAN порт — кабель провайдера (от стены)
   - LAN порт — кабель к компьютеру

2. Вход в настройки
   - Откройте 192.168.0.1 или tplinkwifi.net
   - Логин/пароль: admin/admin

3. Настройка WAN
   - Тип подключения: DHCP (автоматический)
   - Или задайте статический IP (если предоставлен)
   - DNS: можно оставить автоматически

4. Настройка Wi-Fi
   - Имя сети (SSID): придумайте любое
   - Пароль Wi-Fi: минимум 8 символов, WPA2-PSK
   - Рекомендуем 5 ГГц для устройств, поддерживающих его

5. Сохраните и перезагрузите

Проверьте подключение: откройте любой сайт.''',
                'author': User.objects.filter(role='engineer').first(),
            },
            {
                'category': created_cats[2],
                'title': 'Настройка IPTV приставки',
                'content': '''Инструкция по настройке IPTV:

1. Подключение
   - HDMI кабель от приставки к телевизору
   - Сетевой кабель от приставки к роутеру
   - Подключите питание

2. Первый запуск
   - Приставка загрузится автоматически (2-3 минуты)
   - Следуйте инструкциям на экране
   - Выберите язык: Русский

3. Активация
   - Введите номер договора или логин абонента
   - Приставка автоматически загрузит список каналов

4. Управление
   - Пульт ДУ: каналы, громкость, меню
   - Кнопка Menu — настройки изображения и звука
   - Кнопка EPG — программа передач

5. Проблемы
   - Нет картинки — проверьте HDMI кабель
   - Зависает — перезагрузите приставку
   - Нет каналов — проверьте интернет-подключение

Техподдержка: 8(8553)305-000''',
                'author': User.objects.filter(role='engineer').first(),
            },
            {
                'category': created_cats[4],
                'title': 'Как подать заявку на ремонт',
                'content': '''Подача заявки на ремонт через личный кабинет:

1. Войдите в личный кабинет на сайте tatais.ru

2. Перейдите в раздел «Подать заявку»

3. Заполните форму:
   - Выберите тип услуги (интернет, ТВ, телефония)
   - Опишите проблему максимально подробно
   - Укажите адрес объекта
   - Прикрепите фото (если применимо)

4. Отправьте заявку
   - Вы получите номер заявки (формат: TA-ГГГГММДД-XXXX)
   - Статус заявки отображается в личном кабинете

5. Отслеживание
   - В личном кабинете вы увидите все статусы
   - Email и SMS уведомления при смене статуса
   - Можно добавить комментарий к заявке

Без регистрации: вы можете подать гостевую заявку, указав ФИО и телефон.

Телефон: 8(8553)305-000 (круглосуточно)''',
                'author': User.objects.filter(role='dispatcher').first(),
            },
        ]
        
        created = 0
        for adata in articles:
            article, is_created = Article.objects.get_or_create(
                title=adata['title'],
                defaults={
                    'category': adata['category'],
                    'content': adata['content'],
                    'author': adata['author'],
                    'is_published': True,
                }
            )
            if is_created:
                created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  Создано {created} статей'))
    
    def create_sample_tickets(self):
        self.stdout.write('Создание тестовых заявок...')
        
        customer = User.objects.filter(username='subscriber1').first()
        engineer = User.objects.filter(username='engineer1').first()
        engineer2 = User.objects.filter(username='engineer2').first()
        categories = list(ServiceCategory.objects.all())
        
        if not customer or not engineer:
            self.stdout.write(self.style.WARNING('  Пропущено: нет пользователей'))
            return
        
        sample_tickets = [
            {
                'customer': customer,
                'service_type': 'internet',
                'description': 'Не работает интернет с утра. Роутер перезагружал — не помогает. Индикатор Internet не горит.',
                'address': 'ул. Ленина, д. 15, кв. 42',
                'city': 'Альметьевск',
                'status': 'completed',
                'priority': 'high',
                'assigned_engineer': engineer,
                'service_category': categories[0] if len(categories) > 0 else None,
                'customer_rating': 5,
                'customer_feedback': 'Отличный сервис! Инженер приехал через час, всё быстро починил.',
                'days_ago': 7,
            },
            {
                'customer': customer,
                'service_type': 'tv',
                'description': 'Некоторые каналы показывают с помехами, особенно HD каналы. Проблема началась 3 дня назад.',
                'address': 'ул. Ленина, д. 15, кв. 42',
                'city': 'Альметьевск',
                'status': 'in_progress',
                'priority': 'medium',
                'assigned_engineer': engineer,
                'service_category': categories[2] if len(categories) > 2 else None,
                'days_ago': 2,
            },
            {
                'customer': User.objects.filter(username='subscriber2').first(),
                'service_type': 'internet',
                'description': 'Очень низкая скорость интернета — всего 5 Мбит/с при тарифе 100 Мбит/с. Проверял по кабелю.',
                'address': 'ул. Советская, д. 8, кв. 15',
                'city': 'Бугульма',
                'status': 'assigned',
                'priority': 'high',
                'assigned_engineer': engineer2,
                'service_category': categories[0] if len(categories) > 0 else None,
                'days_ago': 1,
            },
            {
                'customer': customer,
                'service_type': 'internet',
                'description': 'Хочу подключить интернет в новой квартире. Нужно провести кабель и настроить роутер.',
                'address': 'пр. Строителей, д. 22, кв. 88',
                'city': 'Альметьевск',
                'status': 'new',
                'priority': 'low',
                'service_category': categories[4] if len(categories) > 4 else None,
                'days_ago': 0,
            },
            {
                'customer': customer,
                'service_type': 'phone',
                'description': 'Телефон не работает — нет сигнала линии. Слышны помехи и щелчки.',
                'address': 'ул. Ленина, д. 15, кв. 42',
                'city': 'Альметьевск',
                'status': 'parts_needed',
                'priority': 'medium',
                'assigned_engineer': engineer,
                'service_category': categories[3] if len(categories) > 3 else None,
                'days_ago': 3,
            },
        ]
        
        created = 0
        for tdata in sample_tickets:
            if not tdata['customer']:
                continue
            
            created_date = timezone.now() - timedelta(days=tdata['days_ago'])
            count = Ticket.objects.count() + 1
            ticket_num = f'TA-{created_date.strftime("%Y%m%d")}-{count:04d}'
            
            completed_at = None
            if tdata['status'] == 'completed':
                completed_at = created_date + timedelta(days=1)
            
            ticket, is_created = Ticket.objects.get_or_create(
                ticket_number=ticket_num,
                defaults={
                    'customer': tdata['customer'],
                    'service_type': tdata['service_type'],
                    'description': tdata['description'],
                    'address': tdata['address'],
                    'city': tdata['city'],
                    'status': tdata['status'],
                    'priority': tdata['priority'],
                    'assigned_engineer': tdata.get('assigned_engineer'),
                    'service_category': tdata.get('service_category'),
                    'customer_rating': tdata.get('customer_rating'),
                    'customer_feedback': tdata.get('customer_feedback', ''),
                    'created_at': created_date,
                    'completed_at': completed_at,
                }
            )
            if is_created:
                created += 1
                
                # Create history records
                TicketHistory.objects.create(
                    ticket=ticket, action='Заявка создана',
                    new_value='Новая', created_at=created_date
                )
                if tdata['status'] in ('assigned', 'in_progress', 'completed', 'parts_needed'):
                    TicketHistory.objects.create(
                        ticket=ticket, action='Назначен инженер',
                        new_value=str(tdata['assigned_engineer']) if tdata['assigned_engineer'] else '',
                        created_at=created_date + timedelta(hours=1)
                    )
                if tdata['status'] in ('in_progress', 'completed', 'parts_needed'):
                    TicketHistory.objects.create(
                        ticket=ticket, action='Статус изменён',
                        old_value='Назначена инженеру',
                        new_value='В работе',
                        created_at=created_date + timedelta(hours=3)
                    )
                if tdata['status'] == 'completed':
                    TicketHistory.objects.create(
                        ticket=ticket, action='Статус изменён',
                        old_value='В работе',
                        new_value='Завершена',
                        created_at=completed_at
                    )
        
        self.stdout.write(self.style.SUCCESS(f'  Создано {created} тестовых заявок'))
