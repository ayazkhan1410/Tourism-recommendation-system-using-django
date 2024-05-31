import datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import (HotelRating,Booking, Place, City,Contact,Hotel, CustomUser as User, PlaceFeatureImages, HotelFeatureImages, PlaceRating)
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
import random
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
import stripe
from django.conf import settings
from django.views.decorators.http import require_POST
from datetime import datetime

# Create your views here.

def index(request):
    popular_destinations = City.objects.filter(is_popular_place=True)
    is_top_tour_packages = Place.objects.filter(is_top_tour_package=True)
    hotel_obj = Hotel.objects.filter(is_popular_hotel=True)
    
    # Calculate average rating and total ratings for each place
    for place in is_top_tour_packages:
        ratings = PlaceRating.objects.filter(place=place)
        place.average_rating = ratings.aggregate(Avg('rating'))['rating__avg']
        place.total_ratings = ratings.count()
        
        # Round the average rating to the nearest integer
        place.average_rating = round(place.average_rating) if place.average_rating is not None else None

    for item in hotel_obj:
        ratings = HotelRating.objects.filter(hotel=item)
        item.average_rating = ratings.aggregate(Avg('rating'))['rating__avg']
        item.total_ratings = ratings.count()
        
        # Round the average rating to the nearest integer
        item.average_rating = round(item.average_rating) if item.average_rating is not None else None
    
    if request.method == "POST":
        places = request.POST.get('places')
        
        if places:
            # Filter places based on the city name entered by the user
            places_queryset = Place.objects.filter(
                Q(city__city__icontains=places) |
                Q(place_name__icontains=places) |
                Q(place_desc__icontains=places) 
            )

            context = {
                'places': places_queryset,
            }
        
        for item in places_queryset:
            ratings = PlaceRating.objects.filter(place=item)
            item.average_rating = ratings.aggregate(Avg('rating'))['rating__avg']
            item.total_ratings = ratings.count()
            
            # Round the average rating to the nearest integer
            item.average_rating = round(item.average_rating) if item.average_rating is not None else None
        
            return render(request, 'search-results.html', context)
    
    context = {
        'popular_destinations': popular_destinations,
        'is_top_tour_packages': is_top_tour_packages,
        'hotel_obj': hotel_obj,
    }
    return render(request, 'index.html', context)


def places_by_city(request, place_name):
    place_by_city = Place.objects.filter(city__city=place_name)   
    
    paginator = Paginator(place_by_city, 6)
    page_number = request.GET.get('page')
    
    try:
        paginated_products = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_products = paginator.page(1)
    except EmptyPage:
        paginated_products = paginator.page(paginator.num_pages)
        
    context = {
        'paginated_products': paginated_products,
        "place_name": place_name,
    }
    
    return render(request, 'tour.html', context)

def tour(request):
    places_obj = Place.objects.all().order_by('-id')

    paginator = Paginator(places_obj, 6)
    page_number = request.GET.get('page')

    try:   
        paginated_products = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_products = paginator.page(1)
    except EmptyPage:
        paginated_products = paginator.page(paginator.num_pages)
        
    if request.method == "POST":
        place_name = request.POST.get('place_name')
        city = request.POST.get('city')
        price_from = request.POST.get('price_from')
        price_to = request.POST.get('price_to')
       
       
        # Filter places based on place name or city name
        if place_name:
            places_obj = places_obj.filter(place_name__icontains=place_name)
            paginator = Paginator(places_obj, 6)
            paginated_products = paginator.page(1)
        if city:
            places_obj = places_obj.filter(city__city__icontains=city)
            paginator = Paginator(places_obj, 6)
            paginated_products = paginator.page(1)
        
        # Additional filtering based on price if provided
        if price_from:
            places_obj = places_obj.filter(place_price__gte=price_from)
            paginator = Paginator(places_obj, 6)
            paginated_products = paginator.page(1)
        if price_to:
            places_obj = places_obj.filter(place_price__lte=price_to)
            paginator = Paginator(places_obj, 6)
            paginated_products = paginator.page(1)
    
    for place in paginated_products:
        ratings = PlaceRating.objects.filter(place=place)
        place.average_rating = ratings.aggregate(Avg('rating'))['rating__avg']
        place.total_ratings = ratings.count()
        
        # Round the average rating to the nearest integer
        place.average_rating = round(place.average_rating) if place.average_rating is not None else None
        
    context = {
        'paginated_products': paginated_products
    }
    
    return render(request, 'tour.html', context)

@login_required(login_url='login')
def tour_detail(request, slug):
    # Fetch the specific place corresponding to the slug
    place = get_object_or_404(Place, slug=slug)
    feature_images = PlaceFeatureImages.objects.filter(place=place)
    you_may_also_like = Place.objects.filter(city=place.city).exclude(id=place.id).order_by('?')[:3]
    
    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        review_text = request.POST.get('review')
        if rating_value and review_text:
            user = request.user
            
            # Check if the user has already submitted a review for this place
            if not PlaceRating.objects.filter(user=user, place=place).exists():
                rating = PlaceRating.objects.create(user=user, place=place, rating=rating_value, review=review_text)
                rating.save()
                messages.success(request, 'Review submitted successfully')
                return redirect('tour-detail', slug=slug)  # Redirect to prevent form resubmission on page refresh
            else:
                messages.error(request, 'You have already submitted a review for this place')
                return redirect('tour-detail', slug=slug)  # Redirect to prevent form resubmission on page refresh
    
    # Calculate average rating for the specific place
    ratings = PlaceRating.objects.filter(place=place)
    average_rating = ratings.aggregate(Avg('rating'))['rating__avg']
    total_ratings = ratings.count()

    # Round the average rating to the nearest integer
    average_rating = round(average_rating) if average_rating is not None else None

    context = {
        'place': place,
        'feature_images': feature_images,
        'average_rating': average_rating,
        'total_ratings': total_ratings,
        'you_may_also_like':you_may_also_like
    }
    return render(request, 'tour-detail.html', context)

stripe.api_key = settings.STRIPE_SECRET_KEY
@login_required(login_url='login')
def create_checkout_session(request):
    try:
        name = request.POST.get('name')
        email = request.POST.get('email')
        place_id = request.POST.get('place_id')
        place = get_object_or_404(Place, id=place_id)
        date_from_str = request.POST.get('date_from')
        date_to_str = request.POST.get('date_to')
        total_persons = int(request.POST.get('total_persons'))
        
        # Check if dates are not empty
        if not (date_from_str and date_to_str):
            return HttpResponse('Error: Please select valid check-in and check-out dates')
        
        if date_from_str > date_to_str:
            return HttpResponse('Error: Check-in date cannot be greater than check-out date')
        
        if date_from_str < datetime.now().strftime('%Y-%m-%d'):
            return HttpResponse('Error: Check-in date cannot be a past date')
        
        if not total_persons:
            return HttpResponse('Error: Please select number of adults')
        
        if not email:
            return HttpResponse('Error: Please enter a valid email address')
        
        if not name:
            return HttpResponse('Error: Please enter your name')
        
        # Convert date strings to datetime objects
        date_from = datetime.strptime(date_from_str, '%Y-%m-%d')
        date_to = datetime.strptime(date_to_str, '%Y-%m-%d')

        # Calculate number of days
        num_days = (date_to - date_from).days + 1
        
        # Calculate total amount
        total_amount = place.place_price * total_persons * num_days * 100  # in cents

        # Create a Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Booking for {place.place_name}',
                    },
                    'unit_amount': total_amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://127.0.0.1:100/payment-success',
            cancel_url='http://127.0.0.1:100/payment-failed',
        )
        
        # Save booking details if session created successfully
        if session:
            book_obj = Booking.objects.create(
                user=request.user,
                place=place,
                guest_name=name,
                guest_email=email,
                num_adults=total_persons,
                total_price=total_amount/100,
                checkin_date=date_from,
                checkout_date=date_to,
                is_confirmed=True,
                is_completed=True,
                is_canceled=False
            )
            book_obj.save()
            
        # Redirect user to Stripe checkout page
        return redirect(session.url, code=303)
    except Exception as e:
        print(str(e))
        return redirect('/')
@login_required(login_url='login')
def hotel_create_checkout_session(request):
    try:
        guest_name = request.POST.get('name')
        guest_email = request.POST.get('email')
        checkin_date = request.POST.get('date_from')
        checkout_date = request.POST.get('date_to')
        num_adults = request.POST.get('total_persons')
        no_of_rooms = request.POST.get('total_rooms')
        hotel_id = request.POST.get('hotel_id')
        hotel = get_object_or_404(Hotel, id=hotel_id)

        if not checkin_date or not checkout_date:
            return HttpResponse('Error: Please select valid check-in and check-out dates')

        if checkin_date > checkout_date:
            return HttpResponse('Error: Check-in date cannot be greater than check-out date')

        if checkin_date < datetime.now().strftime('%Y-%m-%d'):
            return HttpResponse('Error: Check-in date cannot be a past date')

        if not num_adults:
            return HttpResponse('Error: Please select number of adults')

        if not no_of_rooms:
            return HttpResponse('Error: Please select number of rooms')

        if not guest_email:
            return HttpResponse('Error: Please enter a valid email address')

        if not guest_name:
            return HttpResponse('Error: Please enter your name')

        # Convert date strings to datetime objects
        date_from = datetime.strptime(checkin_date, '%Y-%m-%d')
        date_to = datetime.strptime(checkout_date, '%Y-%m-%d')

        # Convert to integers
        num_adults = int(num_adults)
        no_of_rooms = int(no_of_rooms)
        hotel_price = float(hotel.hotel_price)

        # Calculate number of days
        num_days = (date_to - date_from).days

        if num_days <= 0:
            return HttpResponse('Error: Check-out date must be after check-in date')

        # Calculate total amount
        total_amount = num_days * num_adults * no_of_rooms * hotel_price * 100  # Convert to cents

        # Create Stripe session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Booking for {hotel.hotel_name}',
                    },
                    'unit_amount': int(total_amount),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://127.0.0.1:100/payment-success-hotel',
            cancel_url='http://127.0.0.1:100/payment-failed',
            metadata={
                'user_email': request.user.email,
                'hotel_address': hotel.hotel_address,
                'hotel_city': hotel.city,
                'guest_name': guest_name,
                'guest_email': guest_email,
                'checkin_date': checkin_date,
                'checkout_date': checkout_date,
                'num_adults': num_adults,
                'no_of_rooms': no_of_rooms,
            }
        )

        if session:
            booking_obj = Booking.objects.create(
                user=request.user,
                hotel = hotel,
                guest_name=guest_name,
                guest_email=guest_email,
                checkin_date=checkin_date,
                checkout_date=checkout_date,
                num_adults=num_adults,
                no_of_rooms=no_of_rooms,
                total_price = total_amount /100,
                is_confirmed=True,
                is_completed=True,
                is_canceled=False
            )
            booking_obj.save()
            return redirect(session.url, code=303)

    except Exception as e:
        print(e)
        return redirect('payment-failed')

def hotels(request):
    hotels_obj = Hotel.objects.all().order_by('-id')

    paginator = Paginator(hotels_obj, 6)
    page_number = request.GET.get('page')

    try:
        paginated_products = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_products = paginator.page(1)
    except EmptyPage:
        paginated_products = paginator.page(paginator.num_pages)
        
    if request.method == "POST":
        hotel_name = request.POST.get('hotel_name')
        city = request.POST.get('city')
        price_from = request.POST.get('price_from')
        price_to = request.POST.get('price_to')
       
       
        # Filter places based on place name or city name
        if hotel_name:
            hotels_obj = hotels_obj.filter(hotel_name__icontains=hotel_name)
            paginator = Paginator(hotels_obj, 6)
            paginated_products = paginator.page(1)
        if city:
            hotels_obj = hotels_obj.filter(city__city__icontains=city)
            paginator = Paginator(hotels_obj, 6)
            paginated_products = paginator.page(1)
        
        # Additional filtering based on price if provided
        if price_from:
            hotels_obj = hotels_obj.filter(hotel_price__gte=price_from)
            paginator = Paginator(hotels_obj, 6)
            paginated_products = paginator.page(1)
        if price_to:
            hotels_obj = hotels_obj.filter(hotel_price__lte=price_to)
            paginator = Paginator(hotels_obj, 6)
            paginated_products = paginator.page(1)
      
    for hotel in paginated_products:
        ratings = HotelRating.objects.filter(hotel=hotel)
        hotel.average_rating = ratings.aggregate(Avg('rating'))['rating__avg']
        hotel.total_ratings = ratings.count()
        
    #     # Round the average rating to the nearest integer
        hotel.average_rating = round(hotel.average_rating) if hotel.average_rating is not None else None
    
    context = {
        'paginated_products': paginated_products
    }

    return render(request, 'hotels.html', context)\
        
@login_required(login_url='login')
def hotel_detail(request, slug):
    
    hotel = get_object_or_404(Hotel, slug=slug)
    feature_images = HotelFeatureImages.objects.filter(hotel = hotel)
    you_may_also_like = Hotel.objects.filter(city=hotel.city).exclude(id=hotel.id).order_by('?')[:3]
    
    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        print(rating_value)
        review_text = request.POST.get('review')
        if rating_value and review_text:
            user = request.user
            
            # Check if the user has already submitted a review for this place
            if not HotelRating.objects.filter(user=user, hotel=hotel).exists():
                rating = HotelRating.objects.create(user=user, hotel=hotel, rating=rating_value, review=review_text)
                rating.save()
                messages.success(request, 'Review submitted successfully')
                return redirect('hotel-detail', slug=slug)  # Redirect to prevent form resubmission on page refresh
            else:
                messages.error(request, 'You have already submitted a review for this place')
                return redirect('hotel-detail', slug=slug)  # Redirect to prevent form resubmission on page refresh
    
    # Calculate average rating for the specific place
    ratings = HotelRating.objects.filter(hotel=hotel)
    average_rating = ratings.aggregate(Avg('rating'))['rating__avg']
    total_ratings = ratings.count()

    # Round the average rating to the nearest integer
    average_rating = round(average_rating) if average_rating is not None else None

    
    context = {
        'hotel': hotel,
        'feature_images' : feature_images,
        'average_rating': average_rating,
        'total_ratings': total_ratings,
        'you_may_also_like':you_may_also_like
        
    }
    
    return render(request, 'hotel-detail.html', context)

def signup(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email =  request.POST.get('email')
        password = request.POST.get('password')
        speical_char = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '=']
        
        if len(password) < 8 and not any(char in speical_char for char in password):
            messages.error(request, "Password must be atleast 8 characters and must contain special characters")
            return redirect('signup')
        
        if User.objects.filter(email = email).exists():
            messages.error(request, "Account already exists")
            return redirect('signup')
        
        user = authenticate(email = email, password = password, first_name = name)
        if user is None:
            messages.info(request, "invalid Email and Password")
            
        user_obj = User.objects.create(
            first_name = name,
            email = email
        )
        user_obj.set_password(password)
        user_obj.save()
        messages.info(request, 'Accounted Created successfully please login')
        return redirect('login')
        
    return render(request, 'signup.html')

@login_required(login_url='login')
def payment_success(request):
    booking = Booking.objects.filter(user=request.user).last()
    context = {
        'booking': booking
    }
    return render(request, 'payment-success.html', context)
@login_required(login_url='login')
def payment_success_hotel(request):
    booking = Booking.objects.filter(user=request.user).order_by('-id')
    context = {
        'booking': booking
    }
    return render(request, 'payment-success-hotel.html', context)
@login_required(login_url='login')
def payment_failed(request):
    return render(request, 'payment-failed.html')

@login_required(login_url='login')
def order_history(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-id')
    context = {
        'bookings': bookings
    }
    return render(request, 'order-history.html', context)

def login_page(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
       
        user = authenticate(email = email, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'invalid Email and Password')
            return redirect('login')
       
    return render(request, 'login.html')

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if not message:
            messages.error(request, 'Message field cannot be empty')
            return redirect('contact')

        contact_obj = Contact.objects.create(name=name,
                                             email=email, 
                                             subject=subject,
                                             message=message)
        
        contact_obj.save()
        messages.success(request, 'Your message has been sent successfully')
        return redirect('contact')

    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')

def logout_user(request):
    logout(request)
    return redirect('/')