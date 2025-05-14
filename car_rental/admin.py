from django.contrib import admin
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter
from .models import User, Car, Booking, Payment, SupportRequest

class BookingStatusFilter(SimpleListFilter):
    title = 'booking status'
    parameter_name = 'status'
    
    def lookups(self, request, model_admin):
        return (
            ('PENDING', 'Pending'),
            ('CONFIRMED', 'Confirmed'),
            ('COMPLETED', 'Completed'),
            ('CANCELLED', 'Cancelled'),
            ('ACTIVE', 'Active (Pending or Confirmed)'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'ACTIVE':
            return queryset.filter(status__in=['PENDING', 'CONFIRMED'])
        elif self.value():
            return queryset.filter(status=self.value())
        return queryset

class CarAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'year', 'price_per_day', 'availability_status', 'transmission_type', 'image_preview', 'rental_history')
    list_filter = ('availability', 'make', 'year', 'transmission_type')
    search_fields = ('make', 'model')
    
    def availability_status(self, obj):
        if obj.availability:
            # Check if this car has any completed bookings
            completed_bookings = Booking.objects.filter(car=obj, status='COMPLETED').count()
            if completed_bookings > 0:
                return format_html(
                    '<span style="color: green; font-weight: bold;">Available</span> '
                    '<span style="color: blue; font-size: 0.8em;">({} completed bookings)</span>', 
                    completed_bookings
                )
            return format_html('<span style="color: green; font-weight: bold;">Available</span>')
        else:
            # Find if there's a non-cancelled booking for this car
            active_booking = Booking.objects.filter(car=obj, status__in=['PENDING', 'CONFIRMED']).first()
            if active_booking:
                return format_html('<span style="color: red;">Booked until {}</span>', active_booking.end_date.strftime('%b %d, %Y'))
            return format_html('<span style="color: orange;">Not Available</span>')
    
    availability_status.short_description = 'Availability'
    
    def image_preview(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px;" />', obj.image_url)
        return "No Image"
    
    image_preview.short_description = 'Image Preview'
    
    readonly_fields = ('image_full_preview',)
    
    def image_full_preview(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="max-height: 300px; max-width: 100%;" />', obj.image_url)
        return "No Image"
    
    image_full_preview.short_description = 'Image Preview'
    
    def rental_history(self, obj):
        # Get counts of different booking statuses
        completed = Booking.objects.filter(car=obj, status='COMPLETED').count()
        cancelled = Booking.objects.filter(car=obj, status='CANCELLED').count()
        pending = Booking.objects.filter(car=obj, status='PENDING').count()
        confirmed = Booking.objects.filter(car=obj, status='CONFIRMED').count()
        
        if completed + cancelled + pending + confirmed == 0:
            return "No rentals"
        
        history = []
        if completed > 0:
            history.append(f'<span style="color: blue;">{completed} completed</span>')
        if cancelled > 0:
            history.append(f'<span style="color: red;">{cancelled} cancelled</span>')
        if pending + confirmed > 0:
            history.append(f'<span style="color: orange;">{pending + confirmed} active</span>')
            
        return format_html(', '.join(history))
    
    rental_history.short_description = 'Rental History'
    
    fieldsets = (
        (None, {
            'fields': ('make', 'model', 'year', 'price_per_day', 'availability', 'transmission_type')
        }),
        ('Image', {
            'fields': ('image_url', 'image_full_preview'),
            'description': 'Enter the URL of the car image. The image will be displayed on the website.'
        }),
    )

class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'car_info', 'start_date', 'end_date', 'total_price', 'status')
    list_filter = (BookingStatusFilter, 'start_date', 'end_date')
    search_fields = ('user__username', 'car__make', 'car__model')
    readonly_fields = ('total_price',)
    actions = ['cancel_bookings', 'complete_bookings']
    
    def car_info(self, obj):
        # Include availability info in the car description
        availability = "Available" if obj.car.availability else "Not Available"
        if obj.status == 'CANCELLED':
            availability = "Available (Cancelled Booking)"
        elif obj.status == 'COMPLETED':
            availability = "Available (Completed Booking)"
        
        return f"{obj.car.make} {obj.car.model} ({obj.car.year}) - {availability}"
    
    car_info.short_description = 'Car'
    
    def cancel_bookings(self, request, queryset):
        # Only cancel bookings that are pending or confirmed
        cancellable = queryset.filter(status__in=['PENDING', 'CONFIRMED'])
        count = 0
        payment_count = 0
        
        for booking in cancellable:
            booking.status = 'CANCELLED'
            booking.save()
            
            # Update associated payment status to refunded
            payments = Payment.objects.filter(booking=booking)
            for payment in payments:
                payment.status = 'REFUNDED'
                payment.save()
                payment_count += 1
            
            # Make the car available again
            car = booking.car
            car.availability = True
            car.save()
            
            count += 1
        
        self.message_user(
            request, 
            f"{count} booking(s) were cancelled, {payment_count} payment(s) were refunded, and cars made available."
        )
    
    cancel_bookings.short_description = "Cancel selected bookings and make cars available"
    
    def complete_bookings(self, request, queryset):
        # Only complete bookings that are confirmed or pending
        completable = queryset.filter(status__in=['CONFIRMED', 'PENDING'])
        count = 0
        payment_count = 0
        
        for booking in completable:
            booking.status = 'COMPLETED'
            booking.save()
            
            # Update associated payment status
            payments = Payment.objects.filter(booking=booking)
            for payment in payments:
                payment.status = 'COMPLETED'
                payment.save()
                payment_count += 1
            
            # Make the car available again
            car = booking.car
            car.availability = True
            car.save()
            
            count += 1
        
        self.message_user(
            request, 
            f"{count} booking(s) were marked as completed, {payment_count} payment(s) were updated, and cars made available again."
        )
    
    complete_bookings.short_description = "Mark selected bookings as completed"

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking_info', 'amount', 'payment_method', 'payment_date', 'transaction_id', 'status')
    list_filter = ('payment_method', 'payment_date', 'status')
    search_fields = ('booking__user__username', 'transaction_id')
    readonly_fields = ('payment_date',)
    
    def booking_info(self, obj):
        booking_status = obj.booking.get_status_display()
        status_color = 'blue'
        if obj.booking.status == 'CANCELLED':
            status_color = 'red'
        elif obj.booking.status == 'COMPLETED':
            status_color = 'green'
        
        return format_html(
            "Booking #{} - {} - {} {} - <span style='color: {};'>{}</span>",
            obj.booking.id, 
            obj.booking.user.username, 
            obj.booking.car.make, 
            obj.booking.car.model,
            status_color,
            booking_status
        )
    
    booking_info.short_description = 'Booking Details'

admin.site.register(User)
admin.site.register(Car, CarAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(SupportRequest)
