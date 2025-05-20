from django.contrib import admin

# Register your models here.
from .models import User, Cafe, BanquetBooking
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role',)

@admin.register(Cafe)
class CafeAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'address')


@admin.register(BanquetBooking)
class BanquetBookingAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'cafe', 'date', 'time', 'assistant', 'total_price')
    list_filter = ('cafe', 'date')
    search_fields = ('client_name', 'client_phone')
