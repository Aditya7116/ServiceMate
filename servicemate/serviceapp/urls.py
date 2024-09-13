from django.conf import settings
from . import views
from django.urls import path
from django.conf.urls.static import static

urlpatterns =   [
    path('', views.home, name='home'),
    path('register',views.registerUser, name = 'register'),
    path('login',views.login1, name = 'login'),
    path('logout',views.logout1, name = 'logout'),
    path('contact',views.contact, name = 'contact'),
    path('about',views.about, name = 'about'),
    path('bookappointment', views.book_appointment, name='bookappointment'),
    path('process_payment/<int:appointment_id>', views.process_payment, name='process_payment'),
    path('payment-success', views.payment_success, name='payment_success'),
    path('appointment_history',views.appointment_history,name='appointment_history'),
    path('download-receipt/<int:appointment_id>/', views.download_receipt, name='download_receipt'),
]
 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)