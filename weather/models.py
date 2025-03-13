from django.db import models

# Create your models here.
class WeatherSearch(models.Model):
    city = models.CharField(max_length=200)
    date = models.DateField(auto_now_add=True)

