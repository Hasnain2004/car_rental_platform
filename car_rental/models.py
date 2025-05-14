from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class Car(models.Model):
    TRANSMISSION_CHOICES = [
        ('MANUAL', 'Manual'),
        ('AUTOMATIC', 'Automatic'),
    ]
    
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    price_per_day = models.FloatField()
    availability = models.BooleanField(default=True)
    transmission_type = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, default='AUTOMATIC')
    image_url = models.URLField(max_length=500, blank=True, null=True, 
                               default="https://th.bing.com/th/id/R.c33768fe42791b045951429e0502701a?rik=Os5%2fNGBq8DeSgw&riu=http%3a%2f%2fwww.pixelstalk.net%2fwp-content%2fuploads%2f2016%2f06%2fCar-desktop-backgrounds-car-wallpapers-car-hd-photo.jpg&ehk=QhMJa%2bXR7ppHcBMx0gOMEXaZCCSYCneetAeXVsfTaPc%3d&risl=&pid=ImgRaw&r=0")
    
    def __str__(self):
        return f"{self.make} {self.model} ({self.year})"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    def __str__(self):
        return f"Booking {self.id} - {self.user.username} - {self.car}"

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('PAYPAL', 'PayPal'),
        ('BANK_TRANSFER', 'Bank Transfer'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('REFUNDED', 'Refunded'),
        ('FAILED', 'Failed'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.FloatField()
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    
    def __str__(self):
        return f"Payment {self.id} - {self.booking.id} - ${self.amount} - {self.get_status_display()}"

class SupportRequest(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    
    def __str__(self):
        return f"Support Request {self.id} - {self.user.username}"
