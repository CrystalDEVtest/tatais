# ============================================
# Система управления сервисными заявками
# ООО «ТатАИСнефть»
# ============================================

## Быстрый старт

### 1. Создайте базу данных в SQL Server

Откройте SQL Server Management Studio (SSMS) и выполните:

```sql
CREATE DATABASE ServiceSystemDB;
GO
```

### 2. Установите Python зависимости

```bash
pip install -r requirements.txt
```

### 3. Установите ODBC Driver 17 для SQL Server

Скачайте с: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

Windows: установите .msi файл
Linux (Ubuntu): `sudo apt install unixodbc-dev mssql-tools18`

### 4. Выполните миграции

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Создайте суперпользователя

```bash
python manage.py createsuperuser
```

Рекомендуется создать пользователей с разными ролями:
- admin (Администратор) — полный доступ
- dispatcher (Диспетчер) — управление заявками
- engineer (Инженер) — выполнение работ
- subscriber (Абонент) — подача заявок

### 6. Создайте начальные данные

```bash
python manage.py create_initial_data
```

### 7. Запустите сервер разработки

```bash
python manage.py runserver
```

Откройте http://127.0.0.1:8000/

---

## Структура проекта

```
service_system/
├── service_system/         # Основные настройки проекта
│   ├── settings.py         # Конфигурация (БД, приложения, стили)
│   ├── urls.py             # Корневые URL-маршруты
│   └── wsgi.py             # WSGI конфигурация
│
├── accounts/               # Модуль пользователей
│   ├── models.py           # Модель User с ролями
│   ├── views.py            # Регистрация, авторизация, профиль
│   ├── forms.py            # Формы регистрации и профиля
│   └── urls.py             # URL-маршруты
│
├── tickets/                # Модуль заявок
│   ├── models.py           # Ticket, TicketComment, TicketHistory, ServiceCategory
│   ├── views.py            # Создание, детальная страница, инженер/диспетчер панели
│   ├── forms.py            # Формы заявок, комментариев, изменения статуса
│   └── urls.py             # URL-маршруты
│
├── notifications/          # Модуль уведомлений
│   ├── models.py           # Notification, EmailLog, SMSLog
│   ├── utils.py            # Отправка email/SMS, создание уведомлений
│   ├── views.py            # Список уведомлений
│   └── context_processors.py  # Счётчик непрочитанных
│
├── reports/                # Модуль отчётности
│   └── views.py            # Дашборд с Chart.js графиками
│
├── knowledgebase/          # Модуль базы знаний
│   ├── models.py           # Article, Category, ArticleFile
│   ├── views.py            # Список статей, детальная страница
│   └── urls.py             # URL-маршруты
│
├── maps/                   # Модуль карт
│   └── views.py            # Карта заявок (Яндекс.Карты)
│
├── templates/              # HTML-шаблоны
│   ├── base.html           # Базовый шаблон
│   ├── home.html           # Главная страница
│   ├── accounts/           # Шаблоны аккаунта
│   ├── tickets/            # Шаблоны заявок
│   ├── notifications/      # Шаблоны уведомлений
│   ├── reports/            # Шаблоны отчётов
│   ├── knowledgebase/      # Шаблоны базы знаний
│   └── maps/               # Шаблоны карт
│
├── static/                 # Статические файлы
│   ├── css/style.css       # Основные стили
│   ├── js/main.js          # Основные скрипты
│   └── img/                # Изображения (логотип, баннер)
│
└── media/                  # Загруженные файлы
    ├── photos/             # Фотографии
    └── documents/          # Документы
```

---

## Роли пользователей

| Роль | Функционал |
|------|-----------|
| **Абонент** | Подача заявок, отслеживание статуса, личный кабинет |
| **Инженер** | Дашборд заявок, изменение статусов, комментарии, календарь |
| **Диспетчер** | Канбан-доска, назначение инженеров, контроль сроков |
| **Администратор** | Полный доступ: пользователи, настройки, отчёты, логи |

---

## Статусы заявок

1. Новая
2. Назначена инженеру
3. В работе
4. Требуется запчасть
5. Ожидает подтверждения от клиента
6. Завершена
7. Отклонена

---

## Настройка для production

1. Установите `DEBUG = False` в settings.py
2. Настройте `ALLOWED_HOSTS`
3. Настройте SMTP для email-уведомлений
4. Настройте SMS-шлюз в `notifications/utils.py`
5. Получите API-ключ для Яндекс.Карт
6. Запустите через Gunicorn: `gunicorn service_system.wsgi:application`

---

## Контакты ООО «ТатАИСнефть»

- Телефон: 8(8553)305-000
- Сайт: https://tatais.ru/
- VK: https://vk.com/tataisneft
- Адрес: г. Альметьевск, ул. Ленина, д.33
