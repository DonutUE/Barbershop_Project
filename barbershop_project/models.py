
from django.db import models
from django.contrib.auth.models import User

class Location(models.Model):
    city = models.CharField(max_length=100); address = models.CharField(max_length=200)
    def __str__(self): return f"{self.city}, {self.address}"

class Master(models.Model):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    photo_url = models.CharField(max_length=500, default="https://via.placeholder.com/300")
    rating = models.FloatField(default=5.0)
    reviews_count = models.IntegerField(default=0)
    bio = models.TextField(default="Професіонал своєї справи.")
    def __str__(self): return self.name

class Service(models.Model):
    name = models.CharField(max_length=100); price = models.IntegerField(); description = models.TextField(blank=True)
    def __str__(self): return f"{self.name} - {self.price}"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    master = models.ForeignKey(Master, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    wishes = models.TextField(blank=True, null=True)
    date_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
