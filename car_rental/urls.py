from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('cars/', views.car_list, name='car_list'),
    path('cars/<int:car_id>/', views.car_detail, name='car_detail'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('bookings/create/<int:car_id>/', views.create_booking, name='create_booking'),
    path('bookings/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('support/', views.create_support_request, name='create_support_request'),
] 