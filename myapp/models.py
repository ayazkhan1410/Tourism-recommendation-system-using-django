from django.db import models
from .helpers import Manager
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify

# Create your models here.
class CustomUser(AbstractUser):
    username = None
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=100)
    address = models.TextField()
    user_profile = models.ImageField(upload_to='user_profile/', default='user_profile/default.webp')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = Manager()        
    
    def __str__(self) -> str:
        return self.email

class City(models.Model):
    city = models.CharField(max_length=100)
    city_image = models.ImageField(upload_to='city_images')
    city_desc = models.TextField()
    city_slug = models.SlugField(unique=True, max_length=150, blank=True, null=True)
    is_popular_place = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.city)
        super(City, self).save(*args, **kwargs)
        
    def __str__(self):
        return self.city

class Place(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='locations')
    place_name = models.CharField(max_length=100, null=True, blank=True)
    place_image = models.ImageField(upload_to='place_images')
    place_desc = models.TextField()
    place_address = models.CharField(max_length=100, null=True, blank=True)
    place_price = models.PositiveIntegerField(default=0)    
    is_top_tour_package = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, max_length=150, blank=True, null=True)
    
    
    def save(self, *args, **kwargs):
        if not self.slug:  # Generate slug only if it's not set
            base_slug = slugify(self.place_name)
            unique_slug = base_slug
            counter = 1
            while Place.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.place_name

class PlaceFeatureImages(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='place_images')
    images = models.ImageField(upload_to='place_images')
    
    def __str__(self) -> str:
        return self.place.place_name

class Hotel(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='hotels')
    hotel_name = models.CharField(max_length=100, null=True, blank=True)
    hotel_address = models.CharField(max_length=100, null=True, blank=True)
    hotel_desc = models.TextField()
    hotel_image = models.ImageField(upload_to='hotel_images')
    hotel_price = models.PositiveIntegerField(default=0)
    hotel_rooms = models.PositiveIntegerField(default=0)
    slug = models.SlugField(unique=True, max_length=150, blank=True, null=True)
    is_popular_hotel = models.BooleanField(default=False)
    
   
    def save(self, *args, **kwargs):
        self.slug = slugify(self.hotel_name)
        super(Hotel, self).save(*args, **kwargs)
        
    def __str__(self):
        return self.hotel_name

class HotelFeatureImages(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='hotel_images')
    image = models.ImageField(upload_to='hotel_images')

    def __str__(self):
        return self.hotel.hotel_name

    class Meta:
        verbose_name_plural = 'Hotel Feature Images'

class Booking(models.Model):
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    guest_name = models.CharField(max_length=100)
    guest_email = models.EmailField()
    no_of_rooms = models.PositiveIntegerField(default=0, null=True, blank=True)
    checkin_date = models.DateField()
    checkout_date = models.DateField()
    num_adults = models.PositiveIntegerField(default=1)
    num_children = models.PositiveIntegerField(default=0)
    total_price = models.PositiveIntegerField(default=0)
    is_confirmed = models.BooleanField(default=False)
    is_canceled = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        if self.hotel:
            return f"Booking for {self.hotel.hotel_name} - {self.checkin_date} to {self.checkout_date}"
        elif self.place:
            return f"Booking for {self.place.place_name} - {self.checkin_date} to {self.checkout_date}"
        else:
            return f"Booking - {self.checkin_date} to {self.checkout_date}"

class Contact(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    subject = models.CharField(max_length=100, null=True, blank=True)
    message = models.TextField()
    
    def __str__(self):
        return self.name

class PlaceRating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='place_ratings')
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='place_ratings')
    rating = models.PositiveIntegerField(default=0, null=True, blank=True)
    review = models.TextField()
    
    def __str__(self) -> str:
        return self.place.place_name
    

class HotelRating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='hotel_ratings')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='hotel_ratings')
    rating = models.PositiveIntegerField(default=0, null=True, blank=True)
    review = models.TextField(null=True, blank=True)
    
    def __str__(self) -> str:
        return self.hotel.hotel_name