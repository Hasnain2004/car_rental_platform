from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from car_rental.models import Car, Booking, SupportRequest
from django.utils import timezone
import datetime

User = get_user_model()

class Command(BaseCommand):
    help = 'Sets up initial data for the car rental application'

    def handle(self, *args, **kwargs):
        self.stdout.write('Setting up initial data...')
        
        # Create users
        if not User.objects.filter(username='customer').exists():
            User.objects.create_user(
                username='customer',
                email='customer@example.com',
                password='customer123',
                is_admin=False
            )
            self.stdout.write(self.style.SUCCESS('Created customer user'))
        
        if not User.objects.filter(username='admin').exists():
            User.objects.create_user(
                username='admin',
                email='admin@example.com',
                password='admin123',
                is_admin=True,
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        
        # Create cars
        cars_data = [
            {
                'make': 'Toyota',
                'model': 'Camry',
                'year': 2022,
                'price_per_day': 50.00,
                'availability': True,
                'registration_number': 'ABC123'
            },
            {
                'make': 'Honda',
                'model': 'Civic',
                'year': 2021,
                'price_per_day': 45.00,
                'availability': True,
                'registration_number': 'DEF456'
            },
            {
                'make': 'Ford',
                'model': 'Mustang',
                'year': 2023,
                'price_per_day': 85.00,
                'availability': True,
                'registration_number': 'GHI789'
            },
            {
                'make': 'Chevrolet',
                'model': 'Malibu',
                'year': 2022,
                'price_per_day': 55.00,
                'availability': True,
                'registration_number': 'JKL012'
            },
            {
                'make': 'Nissan',
                'model': 'Altima',
                'year': 2021,
                'price_per_day': 48.00,
                'availability': True,
                'registration_number': 'MNO345'
            },
            {
                'make': 'BMW',
                'model': '3 Series',
                'year': 2023,
                'price_per_day': 95.00,
                'availability': True,
                'registration_number': 'PQR678'
            },
        ]
        
        for car_data in cars_data:
            if not Car.objects.filter(registration_number=car_data['registration_number']).exists():
                Car.objects.create(**car_data)
                self.stdout.write(self.style.SUCCESS(f'Created car: {car_data["make"]} {car_data["model"]}'))
        
        # Create a booking if customer exists and there are cars
        customer = User.objects.filter(username='customer').first()
        car = Car.objects.filter(availability=True).first()
        
        if customer and car and not Booking.objects.filter(user=customer, car=car).exists():
            start_date = timezone.now().date()
            end_date = start_date + datetime.timedelta(days=5)
            
            Booking.objects.create(
                user=customer,
                car=car,
                start_date=start_date,
                end_date=end_date,
                total_price=car.price_per_day * 5,
                status='CONFIRMED'
            )
            
            car.availability = False
            car.save()
            
            self.stdout.write(self.style.SUCCESS(f'Created booking for {customer.username}'))
        
        # Create a support request
        if customer and not SupportRequest.objects.filter(user=customer).exists():
            SupportRequest.objects.create(
                user=customer,
                message='I have a question about my booking. Can you please provide more information?',
                status='OPEN'
            )
            self.stdout.write(self.style.SUCCESS(f'Created support request for {customer.username}'))
        
        self.stdout.write(self.style.SUCCESS('Initial data setup completed successfully')) 