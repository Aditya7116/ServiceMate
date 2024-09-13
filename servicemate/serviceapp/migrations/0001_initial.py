# Generated by Django 5.1.1 on 2024-09-12 12:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time_slot', models.CharField(choices=[('8-10', '8:00 AM to 10:00 AM'), ('11-1', '11:00 AM to 1:00 PM'), ('2-4', '2:00 PM to 4:00 PM'), ('5-7', '5:00 PM to 7:00 PM'), ('8-10pm', '8:00 PM to 10:00 PM')], max_length=10)),
                ('service', models.CharField(choices=[('cleaning', 'Cleaning'), ('plumbing', 'Plumbing'), ('technician', 'Technician'), ('carpentry', 'Carpentry')], max_length=20)),
                ('address', models.TextField()),
                ('customer_name', models.CharField(max_length=100)),
                ('customer_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('customer_contact', models.CharField(default='0000000000', max_length=10)),
                ('payment_status', models.BooleanField(default=True)),
                ('receipt', models.FileField(blank=True, null=True, upload_to='receipts/')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(max_length=255)),
                ('payment_id', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failure', 'Failure')], default='pending', max_length=10)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='serviceapp.appointment')),
            ],
        ),
    ]
