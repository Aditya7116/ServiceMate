
# Create your models here.
from django.db import models
from django.contrib.auth.models import User  # Add this line
from django.utils import timezone
from datetime import datetime, timedelta

class Appointment(models.Model):
    SERVICE_CHOICES = [
        ('cleaning', 'Cleaning'),
        ('plumbing', 'Plumbing'),
        ('technician', 'Technician'),
        ('carpentry', 'Carpentry'),
    ]

    TIME_SLOT_CHOICES = [
        ('8-10', '8:00 AM to 10:00 AM'),
        ('11-1', '11:00 AM to 1:00 PM'),
        ('2-4', '2:00 PM to 4:00 PM'),
        ('5-7', '5:00 PM to 7:00 PM'),
        ('8-10pm', '8:00 PM to 10:00 PM'),
    ]

    date = models.DateField()
    time_slot = models.CharField(max_length=10, choices=TIME_SLOT_CHOICES)
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    address = models.TextField()
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField(null=False, blank=False)
    customer_contact = models.CharField(max_length=10, default='0000000000')
    payment_status = models.BooleanField(default=True)  # Assume payment is always successful
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments', null=True, blank=True)
      # Add a new field for the receipt
    receipt = models.FileField(upload_to='receipts/', null=True, blank=True)
    
    def is_bookable(self):
        now = timezone.now()
        minimum_booking_time = now + timedelta(hours=3)
        # Combine date and time_slot to form a datetime object
        appointment_datetime = timezone.make_aware(datetime.combine(self.date, self.time_slot))
        return appointment_datetime >= minimum_booking_time
    


    def __str__(self):
        return f"{self.date} - {self.time_slot} - {self.service}"
    

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failure', 'Failure'),
    ]
    
    appointment = models.ForeignKey('Appointment', on_delete=models.CASCADE)
    order_id = models.CharField(max_length=255)  
    payment_id = models.CharField(max_length=255)  # For Razorpay payment ID
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # Add status field
    amount = models.DecimalField(max_digits=10, decimal_places=2)
