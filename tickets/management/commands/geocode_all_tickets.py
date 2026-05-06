from django.core.management.base import BaseCommand
from tickets.models import Ticket
from tickets.geocode import geocode_address, get_city_center


class Command(BaseCommand):
    help = 'Геокодирует адреса всех заявок без координат'

    def handle(self, *args, **options):
        tickets = Ticket.objects.filter(latitude__isnull=True) | Ticket.objects.filter(latitude=54.9, longitude=52.3)
        count = tickets.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('Все заявки уже имеют координаты!'))
            return
        
        self.stdout.write(f'Найдено заявок для геокодирования: {count}')
        
        updated = 0
        not_found = 0
        errors = 0
        
        for i, ticket in enumerate(tickets, 1):
            self.stdout.write(f'  [{i}/{count}] #{ticket.ticket_number}: {ticket.city}, {ticket.address[:40]}...', ending='')
            
            try:
                coords = geocode_address(ticket.city, ticket.address)
                if coords:
                    ticket.latitude = coords[0]
                    ticket.longitude = coords[1]
                    ticket.save(update_fields=['latitude', 'longitude'])
                    self.stdout.write(self.style.SUCCESS(f' -> {coords[0]:.4f}, {coords[1]:.4f}'))
                    updated += 1
                else:
                    fallback = get_city_center(ticket.city)
                    ticket.latitude = fallback[0]
                    ticket.longitude = fallback[1]
                    ticket.save(update_fields=['latitude', 'longitude'])
                    self.stdout.write(self.style.WARNING(f' -> fallback: {fallback[0]}, {fallback[1]}'))
                    not_found += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f' -> ОШИБКА: {e}'))
                errors += 1
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Готово! Обновлено: {updated}, Fallback: {not_found}, Ошибки: {errors}'))