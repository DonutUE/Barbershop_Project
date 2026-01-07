
from django.contrib import admin
from .models import Service, Booking, Location, Master, Review
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin): list_display = ('name', 'price')
@admin.register(Master)
class MasterAdmin(admin.ModelAdmin): list_display = ('name', 'rating')
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin): list_display = ('user', 'phone', 'master', 'date_time')
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin): list_display = ('master', 'user', 'rating')
