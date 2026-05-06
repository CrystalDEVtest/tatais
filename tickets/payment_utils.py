"""
QR-код генерация для оплаты.

Основной вариант: QR-код с платёжной ссылкой Т-Банка.
При сканировании открывается платёжная форма.

Запасной вариант: QR-код с реквизитами счета (формат ST0001).

Получатель:
  - Морев Никита Алексеевич
  - Т-Банк
  - Счёт: 42301810000081106920
"""

import io
import base64
import qrcode
from qrcode.constants import ERROR_CORRECT_M


# ===== Платёжная ссылка Т-Банк =====
PAYMENT_URL = 'https://tbank.ru/cf/8S2MkaLirPr'

# ===== Реквизиты получателя =====
RECIPIENT_NAME = 'Морев Никита Алексеевич'
RECIPIENT_PHONE = '+79033449080'
RECIPIENT_BANK = 'АО "ТБанк"'
RECIPIENT_ACCOUNT = '42301810000081106920'
RECIPIENT_BIC = '044525974'
RECIPIENT_CORR_ACC = '30101810145250000974'
RECIPIENT_INN = '7710140679'
RECIPIENT_KPP = '771301001'
PAYMENT_CONTRACT = '8438313287'


def generate_sbp_qr_base64(amount=None, payment_id=None, description=''):
    """
    Генерирует QR-код с платёжной ссылкой Т-Банка.
    При сканировании открывается платёжная форма.
    """
    return generate_payment_qr()


def generate_payment_qr():
    """
    Генерирует QR-код с платёжной ссылкой Т-Банка.

    Returns:
        str — base64-encoded PNG изображение QR-кода
    """
    qr = qrcode.QRCode(
        version=4,
        error_correction=ERROR_CORRECT_M,
        box_size=8,
        border=4,
    )
    qr.add_data(PAYMENT_URL)
    qr.make(fit=True)

    img = qr.make_image(
        fill_color='#009846',
        back_color='white',
    ).convert('RGB')

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return b64


def generate_details_qr(amount=None):
    """
    Генерирует QR-код с реквизитами счета (формат ST0001).
    Работает в Сбере и Т-Банке при сканировании.

    Args:
        amount: Decimal — сумма в рублях (необязательно)

    Returns:
        str — base64-encoded PNG изображение QR-кода
    """
    # Назначение платежа
    purpose = f'Перевод средств по договору № {PAYMENT_CONTRACT} {RECIPIENT_NAME} НДС не облагается'

    # Формируем данные в формате ST0001 (российский стандарт)
    # Поля разделены символом |
    fields = [
        f'Name={RECIPIENT_NAME}',
        f'PersonalAcc={RECIPIENT_ACCOUNT}',
        f'BankName={RECIPIENT_BANK}',
        f'BIC={RECIPIENT_BIC}',
        f'CorrespAcc={RECIPIENT_CORR_ACC}',
        f'INN={RECIPIENT_INN}',
        f'KPP={RECIPIENT_KPP}',
        f'Purpose={purpose}',
    ]

    # Добавляем сумму если передана
    if amount:
        amount_kopecks = int(float(amount) * 100)
        fields.append(f'Sum={amount_kopecks}')

    payload = '|'.join(fields)

    # Формат: ST0001 + общая длина + данные
    total_length = len(payload)
    qr_data = f'ST0001{total_length}|{payload}'

    qr = qrcode.QRCode(
        version=6,
        error_correction=ERROR_CORRECT_M,
        box_size=6,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(
        fill_color='#009846',
        back_color='white',
    ).convert('RGB')

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return b64


def generate_sbp_qr_phone_only():
    """
    Запасной вариант: QR-код только с номером телефона.
    """
    qr = qrcode.QRCode(
        version=4,
        error_correction=ERROR_CORRECT_M,
        box_size=8,
        border=4,
    )
    qr.add_data(f'tel:{RECIPIENT_PHONE}')
    qr.make(fit=True)

    img = qr.make_image(
        fill_color='#009846',
        back_color='white',
    ).convert('RGB')

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return b64


def get_recipient_details():
    """
    Возвращает словарь с реквизитами получателя для отображения на странице.
    """
    return {
        'name': RECIPIENT_NAME,
        'phone': RECIPIENT_PHONE,
        'bank': RECIPIENT_BANK,
        'account': RECIPIENT_ACCOUNT,
        'bic': RECIPIENT_BIC,
        'corr_account': RECIPIENT_CORR_ACC,
        'inn': RECIPIENT_INN,
        'kpp': RECIPIENT_KPP,
        'payment_url': PAYMENT_URL,
        'contract': PAYMENT_CONTRACT,
    }