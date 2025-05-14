from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Car, Booking, Payment, SupportRequest
from .forms import UserRegisterForm, SupportRequestForm, BookingForm
from datetime import datetime
import uuid

def index(request):
    if request.user.is_authenticated:
        cars = Car.objects.filter(availability=True)[:6]  # Get the first 6 available cars
    else:
        cars = []  # Empty list for non-authenticated users
    return render(request, 'index.html', {'cars': cars})

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        form = SupportRequestForm(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            support_request = form.save(commit=False)
            support_request.user = request.user
            support_request.save()
            messages.success(request, 'Your message has been sent successfully.')
            return redirect('contact')
        elif not request.user.is_authenticated:
            messages.error(request, 'Please login to submit a support request.')
            return redirect('login')
    else:
        form = SupportRequestForm()
    
    return render(request, 'contact.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}. You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('index')

@login_required
def dashboard(request):
    bookings = Booking.objects.filter(user=request.user).exclude(status='CANCELLED').order_by('-start_date')
    support_requests = SupportRequest.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'bookings': bookings,
        'support_requests': support_requests,
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def car_list(request):
    cars = Car.objects.filter(availability=True)
    return render(request, 'cars.html', {'cars': cars})

@login_required
def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    return render(request, 'car_detail.html', {'car': car})

@login_required
def booking_list(request):
    bookings = Booking.objects.filter(user=request.user).exclude(status='CANCELLED').order_by('-start_date')
    return render(request, 'bookings.html', {'bookings': bookings})

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    # Calculate duration in days
    duration = (booking.end_date - booking.start_date).days + 1  # Include both start and end dates
    return render(request, 'booking_detail.html', {'booking': booking, 'duration': duration})

@login_required
def create_booking(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    
    if not car.availability:
        messages.error(request, 'This car is not available for booking.')
        return redirect('car_list')
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.car = car
            
            # Calculate number of days
            delta = booking.end_date - booking.start_date
            days = delta.days + 1  # Include both start and end date
            
            # Calculate total price
            booking.total_price = car.price_per_day * days
            
            booking.save()
            
            # Update car availability
            car.availability = False
            car.save()
            
            # Create payment record
            transaction_id = f"TX-{uuid.uuid4().hex[:12].upper()}"
            payment = Payment(
                booking=booking,
                amount=booking.total_price,
                payment_method='CREDIT_CARD',
                transaction_id=transaction_id,
                status='PENDING'  # Initial payment status
            )
            payment.save()
            
            messages.success(request, 'Booking created successfully. Payment has been recorded.')
            return redirect('booking_detail', booking_id=booking.id)
    else:
        form = BookingForm()
    
    context = {
        'form': form,
        'car': car,
    }
    
    return render(request, 'create_booking.html', context)

@login_required
def create_support_request(request):
    if request.method == 'POST':
        form = SupportRequestForm(request.POST)
        if form.is_valid():
            support_request = form.save(commit=False)
            support_request.user = request.user
            support_request.save()
            messages.success(request, 'Your support request has been submitted.')
            return redirect('index')
    else:
        form = SupportRequestForm()
    
    return render(request, 'create_support_request.html', {'form': form})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Only allow cancellation of pending or confirmed bookings
    if booking.status in ['PENDING', 'CONFIRMED']:
        # Update booking status
        booking.status = 'CANCELLED'
        booking.save()
        
        # Update associated payment status
        payments = Payment.objects.filter(booking=booking)
        for payment in payments:
            payment.status = 'REFUNDED'
            payment.save()
        
        # Make the car available again
        car = booking.car
        car.availability = True
        car.save()
        
        messages.success(request, 'Your booking has been cancelled successfully and payment has been refunded.')
        return redirect('booking_list')
    else:
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('booking_detail', booking_id=booking.id)
