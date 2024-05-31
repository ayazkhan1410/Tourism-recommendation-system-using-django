from django.contrib import admin
from .models import (CustomUser, City, Place, Contact, Hotel, HotelFeatureImages, Booking, PlaceFeatureImages, PlaceRating, HotelRating)
# Register your models here.

@admin.register(CustomUser)
class AdminCustomUser(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone', 'address', 'user_profile')
    search_fields = ('email', 'first_name', 'last_name', 'phone', 'address')
    readonly_fields = ('date_joined', 'last_login')
    
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    
    ordering = ('email',)
    filter_horizontal = ()
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone', 'address', 'user_profile', 'password1', 'password2'),
        }),
    )

@admin.register(City)
class AdminCity(admin.ModelAdmin):
    list_display = ['city', 'city_image', 'city_desc', 'is_popular_place','city_slug']
    list_per_page = 10
    search_fields = ['city']
    
@admin.register(Place)
class AdminPlace(admin.ModelAdmin):
    list_display = ['city', 'place_name', 'place_address', 'place_image', 'place_desc', 'place_price', 'is_top_tour_package', 'slug']
    list_per_page = 10
    search_fields = ['place_name']

@admin.register(Hotel)
class AdminHotel(admin.ModelAdmin):
    list_display = ['city', 'hotel_name', 'hotel_address', 'hotel_desc', 'hotel_image', 'hotel_price', 'hotel_rooms', 'slug', 'is_popular_hotel']
    list_per_page = 10
    search_fields = ['hotel_name']
    
@admin.register(HotelFeatureImages)
class AdminHotelFeatureImages(admin.ModelAdmin):
    list_display = ['hotel', 'image']
    list_per_page = 10
    search_fields = ['hotel']

@admin.register(Booking)
class AdminBooking(admin.ModelAdmin):
    list_display = ('user', 'hotel', 'place', 'guest_name', 'guest_email', 'checkin_date', 'checkout_date', 'num_adults', 'num_children', 'no_of_rooms', 'total_price', 'is_confirmed', 'is_canceled', 'is_completed', )
    list_per_page = 10
    search_fields = ['user', 'place', 'hotel']

@admin.register(Contact)
class AdminContact(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'message']
    list_per_page = 10
    search_fields = ['name', 'email', 'subject']
    
@admin.register(PlaceFeatureImages)
class AdminPlaceFeatureImages(admin.ModelAdmin):
    list_display = ['place', 'images']
    list_per_page = 10
    search_fields = ['place']
    
@admin.register(PlaceRating)
class AdminPriceRating(admin.ModelAdmin):
    list_display = ['user', 'place', 'rating', 'review']
    list_per_page = 10
    search_fields = ['user', 'place']

@admin.register(HotelRating)
class AdminHotelRating(admin.ModelAdmin):
    list_display = ['user', 'hotel', 'rating', 'review']
    list_per_page = 10
    search_fields = ['user', 'hotel']