import json
import urllib.request
import urllib.parse
import logging

logger = logging.getLogger(__name__)

# API-ключ Яндекс.Геокодера
YANDEX_GEOCODER_KEY = '8b93a78b-1899-49d5-9cf5-901993e56da8'

# Координаты центров городов Татарстана (широта, долгота) — fallback
CITY_CENTERS = {
    'Альметьевск': (54.9167, 52.3167),
    'Бугульма': (54.5389, 52.8174),
    'Нижнекамск': (55.6289, 51.8161),
    'Елабуга': (55.7833, 52.0372),
    'Чистополь': (55.3569, 50.6332),
    'Лениногорск': (54.6044, 52.3997),
    'Нурлат': (54.9292, 50.8083),
    'Менделеевск': (55.7108, 52.4084),
    'Заинск': (55.3121, 52.0107),
    'Азнакаево': (54.5615, 53.0859),
    'Бавлы': (54.3881, 53.3897),
    'Тетюши': (54.9289, 49.6903),
    'Буинск': (54.9556, 48.3483),
    'Лаишевка': (55.8611, 49.2083),
    'Черемшан': (54.6814, 52.3614),
    'Акташ': (54.8569, 52.4978),
    'Джалиль': (54.6447, 53.0561),
    'Карабаш': (54.5844, 51.8567),
    'Уруссу': (54.5417, 53.3289),
    'Кукмор': (56.0814, 50.8406),
    'Саба': (56.1725, 51.0186),
    'Арск': (56.0883, 49.8792),
    'Мамадыш': (55.7067, 51.4131),
    'Болгар': (54.9861, 49.0697),
    'Туймазы': (54.0844, 53.6889),
}


def geocode_address(city, address):
    """
    Превращает город + адрес в координаты (lat, lng).
    Возвращает (latitude, longitude) или None, если не удалось определить.
    """
    if not city and not address:
        return None

    # Формируем строку для поиска
    query_parts = []
    if city:
        query_parts.append(city.strip())
    if address:
        query_parts.append(address.strip())
    
    query = ', '.join(query_parts)

    # Если есть координаты центра города — подставляем как base
    # чтобы геокодер искал именно в этом регионе
    base_coords = ''
    if city:
        for city_name, coords in CITY_CENTERS.items():
            if city_name.lower() in city.lower() or city.lower() in city_name.lower():
                base_coords = f"&ll={coords[1]},{coords[0]}&spn=0.5,0.5"
                break

    url = (
        'https://geocode-maps.yandex.ru/1.x/?'
        'apikey=' + YANDEX_GEOCODER_KEY +
        '&format=json'
        '&geocode=' + urllib.parse.quote(query.encode('utf-8')) +
        '&results=1'
        '&kind=house' +
        base_coords
    )

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))

        members = data.get('response', {}).get('GeoObjectCollection', {}).get('featureMember', [])
        if members:
            pos = members[0]['GeoObject']['Point']['pos']
            # Яндекс возвращает "долгота широта" — нужно развернуть
            lng, lat = [float(x) for x in pos.split(' ')]
            return (lat, lng)
        
        logger.warning(f'Геокодер не нашёл адрес: {query}')
        return None

    except Exception as e:
        logger.error(f'Ошибка геокодирования для "{query}": {e}')
        return None


def get_city_center(city):
    """
    Возвращает координаты центра города, если город известен.
    Иначе возвращает координаты Татарстана по умолчанию.
    """
    if not city:
        return (54.9, 52.3)

    for city_name, coords in CITY_CENTERS.items():
        if city_name.lower() in city.lower() or city.lower() in city_name.lower():
            return coords

    return (54.9, 52.3)