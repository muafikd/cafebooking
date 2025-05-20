from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid

def generate_organization_id():
    raw = str(uuid.uuid4())
    return f"{raw[:8]}-{raw[9:13]}-{raw[14:17]}"
# Create your models here.


class User(AbstractUser):
    ROLE_CHOICES = [
        ('client', 'Клиент'),
        ('assistant', 'Ассистент'),
        ('admin', 'Администратор'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)

    cafe = models.ForeignKey('Cafe', on_delete=models.SET_NULL, null=True, blank=True, related_name='staff')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Cafe(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активно'),
        ('inactive', 'Неактивно'),
    ]
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    organization_id = models.CharField(
    max_length=20,
    unique=True,
    default=generate_organization_id
    )
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

class BanquetBooking(models.Model):
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE, related_name='bookings')
    assistant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')

    client_name = models.CharField(max_length=255)
    client_phone = models.CharField(max_length=20)
    client_email = models.EmailField(null=True, blank=True)

    date = models.DateField()
    time = models.TimeField()
    duration_hours = models.PositiveIntegerField()
    number_of_people = models.PositiveIntegerField()

    price_per_visitor = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    prepayment = models.DecimalField(max_digits=12, decimal_places=2)
    remaining_payment = models.DecimalField(max_digits=12, decimal_places=2)

    confirmation_code = models.CharField(max_length=4, null=True, blank=True)

    event_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Название мероприятия")
    EVENT_STATUS_CHOICES = [
        ('confirmed', 'Подтверждено'),
        ('not_confirmed', 'Не подтверждено'),
    ]
    event_status = models.CharField(max_length=20, choices=EVENT_STATUS_CHOICES, default='not_confirmed', verbose_name="Статус мероприятия")

    client_comment = models.TextField(null=True, blank=True, verbose_name="Комментарий клиента")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client_name} — {self.date} {self.time} ({self.cafe.name})"


# class PaymentConfirmationCode(models.Model):
#     banquet_booking = models.OneToOneField(BanquetBooking, on_delete=models.CASCADE, related_name='confirmation_code')
#     code = models.CharField(max_length=6)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Code for {self.banquet_booking.client_name}: {self.code}"