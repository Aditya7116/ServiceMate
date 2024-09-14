from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from urllib import request
from django.shortcuts import get_object_or_404, render, redirect
from django.shortcuts import render  # Add this line
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
import os
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Appointment, Payment,Service
import razorpay
from razorpay import Client
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse,FileResponse,Http404
from django.urls import reverse
from django.core.mail import send_mail
import logging
from django.contrib.auth.decorators import login_required
import random
from django.utils import timezone
from datetime import datetime, timedelta
from io import BytesIO
from xhtml2pdf import pisa
from django.template.loader import render_to_string
import pdfkit
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.core.mail import EmailMultiAlternatives




# Initialize Razorpay client
razorpay_client = Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

logger = logging.getLogger(__name__)

def index(request):
    services = Service.objects.all()
    return render(request, 'index.html', {'services': services})

def registerUser(request):
    if request.method == "GET":
        return render(request, 'register.html')
    else:
        f = request.POST['first']
        l = request.POST['last']
        e = request.POST['email']
        u = request.POST['username']
        p = request.POST['password']
        cp = request.POST['confirmpassword']

        if u == '' or e == '' or p == '' or cp == '' or f == '' or l == '':
            context = {'error': 'All fields are mandatory'}
            return render(request, 'register.html', context)
        elif p != cp:
            context = {'error': 'Password and Confirm Password must be the same'}
            return render(request, 'register.html', context)
        else:
            ur = User.objects.create(first_name=f, last_name=l, email=e, username=u)
            ur.set_password(p)
            ur.save()
            messages.success(request, 'User Registered Successfully')
            return redirect('/login')

def login1(request):
    if request.method == "GET":
        return render(request, 'login.html')
    else:
        u = request.POST['username']
        p = request.POST['password']
        user = authenticate(username=u, password=p)
        if user is None:
            messages.error(request, 'Invalid Credentials')
            return render(request, 'login.html')
        else:
            login(request, user)
            messages.success(request, 'User Logged In Successfully!')
            return redirect('/')

def logout1(request):
    logout(request)
    messages.success(request, 'User Logged Out Successfully!')
    return redirect('/')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Send an email to the site admin
        try:
            send_mail(
                subject=f"Contact Form Submission: {subject}",
                message=f"Message from {name} ({email}, {phone}):\n\n{message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
            )
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
        except Exception as e:
            messages.error(request, 'There was an error sending your message. Please try again later.')
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')

def search_results(request):
    query = request.GET.get('query')
    if query:
        results = Service.objects.filter(name__icontains=query)  # Adjust the field as needed
    else:
        results = Service.objects.none()  # Return an empty queryset if no query

    return render(request, 'search_results.html', {'results': results, 'query': query})



@login_required
def book_appointment(request):
    services = Service.objects.all()  # Fetch all services

    if request.method == 'POST':
        # Retrieve form data
        customer_name = request.POST.get('customer_name')
        customer_email = request.POST.get('customer_email')  
        date_str = request.POST.get('date')
        time_slot_str = request.POST.get('time_slot')
        service = request.POST.get('service')
        address = request.POST.get('address')
        customer_contact = request.POST.get('customer_contact')

        # Debugging print statements
        print("Customer Email:", customer_email)

        # Ensure all fields are filled
        if not all([customer_name, customer_email, date_str, time_slot_str, service, address, customer_contact]):
            messages.error(request, 'All fields are required, including email.')
            return render(request, 'bookappoint.html', {'services': services})  # Render the form with services and error message

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()

            if Appointment.objects.filter(date=date, time_slot=time_slot_str, service=service, payment_status=True).exists():
                messages.error(request, 'This time slot for the selected service is already booked.')
                return render(request, 'bookappoint.html', {'services': services})  # Render the form with services and error message

            # Create and save the appointment
            appointment = Appointment.objects.create(
                customer_name=customer_name,
                customer_email=customer_email,  # Saving email correctly
                date=date,
                time_slot=time_slot_str,
                service=service,
                address=address,
                customer_contact=customer_contact,
                payment_status=False,
                user=request.user
            )

            # Redirect to the payment processing page
            return redirect('process_payment', appointment_id=appointment.id)

        except ValueError as e:
            # Handle parsing errors (e.g., invalid date format)
            messages.error(request, f'Invalid input: {str(e)}')
            return render(request, 'bookappoint.html', {'services': services})  # Render the form with services and error message

    # For GET requests, show the form and booked slots
    booked_appointments = Appointment.objects.filter(payment_status=True)
    booked_slots = [(appointment.date.strftime('%Y-%m-%d'), appointment.time_slot) for appointment in booked_appointments]
    
    # Extract the selected service from the query parameters or set default to 'cleaning'
    selected_service = request.GET.get('service', 'cleaning')

    context = {
        'booked_slots': booked_slots,
        'services': services,
        'selected_service': selected_service  # Pass selected_service to the template
    }
    return render(request, 'bookappoint.html', context)






# Set up logging
logger = logging.getLogger(__name__)

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def generate_unique_order_id():
    while True:
      
        order_id = random.randint(100000, 999999)
        
        if not Payment.objects.filter(order_id=order_id).exists():
            return order_id
        
        
        
        
@login_required
def process_payment(request, appointment_id):
    user = request.user
    try:
        # Fetch the appointment using the appointment_id from URL
        appointment = Appointment.objects.get(id=appointment_id)

        # Fixed order amount for the service
        order_amount = 20000  # Amount in paise (₹200)
        order_currency = 'INR'

        # Data for Razorpay order creation
        data = {
            'amount': order_amount,
            'currency': order_currency,
            'receipt': f'order_{appointment.id}',  # Receipt format
            'payment_capture': 1  # Automatic capture
        }

        # Create the Razorpay order
        razorpay_order = razorpay_client.order.create(data=data)
        order_id = razorpay_order.get('id')
        
        # Log order creation response
        logger.info(f'Razorpay order created successfully: {razorpay_order}')

        # Create payment entry with initial pending status
        payment = Payment.objects.create(
            appointment=appointment,
            order_id=order_id,
            amount=200,  # Fixed amount in rupees
            status='pending'  # Initial status is pending
        )

        # Context for rendering the payment page
        context = {
            'appointment': appointment,
            'payment': payment,
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'order_amount': order_amount / 100,  # Convert back to rupees for display
            'currency': order_currency,
            'razorpay_order_id': order_id,
        }
        return render(request, 'pay.html', context)
    
    except Appointment.DoesNotExist:
        logger.error(f'Appointment with ID {appointment_id} does not exist.')
        return HttpResponseBadRequest("Appointment not found.")
    
    except razorpay.errors.RazorpayError as e:
        logger.error(f'Razorpay error: {e}')
        return HttpResponseBadRequest(f"Razorpay error: {e}")
    
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        return HttpResponseBadRequest(f"Unexpected error: {e}")

def payment_success(request):
    order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')

    try:
        # Fetch the payment record
        payment = Payment.objects.get(order_id=order_id)
        
        # Update payment status to success
        payment.status = 'success'
        payment.payment_id = payment_id
        payment.save()

        # Fetch appointment to update status
        appointment = payment.appointment
        appointment.payment_status = True  # Set appointment payment status to True
        appointment.save()

        # Generate and save receipt
        pdf_path = generate_and_save_receipt(appointment)

        # Send receipt email
        return send_receipt(request, appointment, payment_id)

    except Payment.DoesNotExist:
        return HttpResponse("Payment record not found.", status=404)

    except Exception as e:
        # Handle any other unexpected errors
        return HttpResponse(f"An error occurred: {e}", status=500)




# path till wkhtmltopdf
config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe') # Adjust the path as per your installation




def generate_and_save_receipt(appointment):
    # Generate the receipt content using a Django template
    receipt_content = render_to_string('receipt.html', {'appointment': appointment})

    # Define paths and settings
    receipts_dir = os.path.join(settings.MEDIA_ROOT, 'receipts') 
    os.makedirs(receipts_dir, exist_ok=True)  
    pdf_filename = f'receipt_{appointment.id}.pdf'
    pdf_path = os.path.join(receipts_dir, pdf_filename)

    # Configure pdfkit to use the installed wkhtmltopdf
    pdfkit_options = {
        'enable-local-file-access': True,
    }
    pdfkit.from_string(receipt_content, pdf_path, options=pdfkit_options, configuration=pdfkit.configuration(wkhtmltopdf=settings.PDFKIT_CONFIG['wkhtmltopdf']))

    
    appointment.receipt = pdf_filename  
    appointment.save()

    return pdf_path


def send_receipt(request, appointment, payment_id,):
    
    subject = 'Payment Successful'
    recipient_email = appointment.customer_email

   
    email_body = render_to_string('email.html', {
        'company_logo_url': 'http://127.0.0.1:8000/static/images/logo.png',
        'recipient_name': appointment.customer_name,
        'appointment_id': appointment.id,
        'payment_id': payment_id,
       
    })

  
    try:
       
        email = EmailMultiAlternatives(
            subject=subject,
            body='',  
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email]
        )
        email.attach_alternative(email_body, 'text/html')

        # Attach the PDF file
        receipt_filename = f'receipt_{appointment.id}.pdf'
        receipt_path = os.path.join(settings.MEDIA_ROOT, 'receipts', receipt_filename)
        if os.path.exists(receipt_path):
            with open(receipt_path, 'rb') as pdf_file:
                email.attach(receipt_filename, pdf_file.read(), 'application/pdf')
        else:
            # Handle the case where the receipt file does not exist
            return HttpResponse(f'Receipt file not found: {receipt_filename}', status=404)

       
        email.send()

    except Exception as e:
        
        return HttpResponse(f'Error sending email: {e}', status=500)

    return render(request, 'payment_success.html', {'appointment': appointment, 'payment_id': payment_id,})


    

def appointment_history(request):
    if request.user.is_authenticated:
        user_email = request.user.email
        
        # Filter appointments with successful payments for the logged-in user
        appointments = Appointment.objects.filter(
            user__email=user_email,
            payment__status='success'  
        ).distinct()  
    
    else:
        appointments = []

    return render(request, 'appointment.html', {'appointments': appointments})

def download_receipt(request, appointment_id):
    # Construct the path to the PDF file
    file_path = os.path.join(settings.MEDIA_ROOT, 'receipts', f'receipt_{appointment_id}.pdf')
    
    # Check if the file exists
    if not os.path.exists(file_path):
        raise Http404("Receipt not found")
    
  
  
  
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=f'receipt_{appointment_id}.pdf')