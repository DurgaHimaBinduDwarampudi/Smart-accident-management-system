from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='VehicleInsurance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicle_number', models.CharField(max_length=20, unique=True)),
                ('owner_name', models.CharField(max_length=100)),
                ('insurance_company', models.CharField(max_length=100)),
                ('policy_number', models.CharField(max_length=50)),
                ('coverage_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('expiry_date', models.DateField()),
                ('vehicle_type', models.CharField(choices=[('car', 'Car'), ('bike', 'Bike / Motorcycle'), ('truck', 'Truck'), ('bus', 'Bus'), ('auto', 'Auto Rickshaw')], default='car', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(blank=True, max_length=15)),
                ('address', models.TextField(blank=True)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profiles/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AccidentReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='accidents/')),
                ('vehicle_number', models.CharField(blank=True, max_length=20)),
                ('detected_vehicle_number', models.CharField(blank=True, max_length=20)),
                ('report_date', models.DateTimeField(auto_now_add=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('location_address', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('analyzed', 'Analyzed'), ('claimed', 'Claim Submitted')], default='pending', max_length=20)),
                ('emergency_alerts_sent', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accident_reports', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DamageAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('damaged_parts', models.JSONField(default=list)),
                ('total_repair_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('insurance_coverage', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('payable_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('analysis_summary', models.TextField(blank=True)),
                ('analyzed_at', models.DateTimeField(auto_now_add=True)),
                ('report', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='damage_analysis', to='accident_app.accidentreport')),
            ],
        ),
        migrations.CreateModel(
            name='EmergencyContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('relationship', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=15)),
                ('email', models.EmailField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='emergency_contacts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
