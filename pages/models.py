from django.db import models
import django.utils

# Latest deals
class Sale(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    publish_date = models.DateField()
    photo_main = models.ImageField(upload_to = 'photos/%Y/%m/%d/') 
    link = models.TextField(blank=True)

    def __str__(self):
        return self.title

class Free_Game(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    publish_date = models.DateField(default=django.utils.timezone.now)
    expiry_date = models.DateField(blank=True, null=True)
    photo_main = models.TextField(blank=True)
    link = models.TextField(blank=True)

    def __str__(self):
        return "Free-Game: " + self.title

class Coupon(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    publish_date = models.DateField(default=django.utils.timezone.now)
    expiry_date = models.DateField(blank=True, null=True)
    photo_main = models.TextField(blank=True)
    link = models.TextField(blank=True)
    code = models.TextField(blank=True)

    def __str__(self):
        return "Coupon: " + self.title

class Bundle(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    publish_date = models.DateField(default=django.utils.timezone.now)
    expiry_date = models.DateField(blank=True, null=True)
    photo_main = models.TextField(blank=True)
    link = models.TextField(blank=True)

    def __str__(self):
        return "Bundle: " + self.title

# Latest deals
class Carousel_Advertisement(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    publish_date = models.DateField()
    photo_main = models.TextField(blank=True)
    link = models.TextField(blank=True)

    def __str__(self):
        return self.title

# Latest deals
class Alert(models.Model):
    description = models.TextField(blank=True)
    publish_date = models.DateField(default=django.utils.timezone.now)

    def __str__(self):
        return str(self.publish_date)