
from django.urls import path, include
from myapp import views

urlpatterns = [
    
    path('', views.index, name='home'),
    
    path('tour', views.tour, name='tour'),
    path('tour-detail/<str:slug>', views.tour_detail, name='tour-detail'),
    path('tours/<str:place_name>', views.places_by_city, name='places-by-city'),
    path('create-checkout-session/', views.create_checkout_session, name='create-checkout-session'),
    path('payment-success', views.payment_success, name='payment-success'),
    path('payment-failed', views.payment_failed, name='payment-failed'),
    path('order-history', views.order_history, name='order-history'),
    
    path('hotels', views.hotels, name='hotels'),
    path('hotel-detail/<str:slug>', views.hotel_detail, name='hotel-detail'),
    path('hotel-create-checkout-session', views.hotel_create_checkout_session, name='hotel-create-checkout-session'),
    path('payment-success-hotel', views.payment_success_hotel, name='payment-success-hotel'),

    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),
    path('signup', views.signup, name='signup'),
    path('login', views.login_page, name='login'),
    path('logout', views.logout_user, name='logout'),
    path('logout', views.logout_user, name='logout')
]
