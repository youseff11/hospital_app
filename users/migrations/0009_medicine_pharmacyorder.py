from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_alter_prescription_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Medicine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Medicine Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Price')),
                ('stock', models.IntegerField(default=0, verbose_name='Stock Quantity')),
                ('category', models.CharField(blank=True, max_length=100, null=True, verbose_name='Category')),
                ('is_available', models.BooleanField(default=True, verbose_name='Available')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'verbose_name': 'Medicine', 'verbose_name_plural': 'Medicines'},
        ),
        migrations.CreateModel(
            name='PharmacyOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1, verbose_name='Quantity')),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed'), ('DELIVERED', 'Delivered'), ('CANCELLED', 'Cancelled')], default='PENDING', max_length=10)),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('medicine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.medicine', verbose_name='Medicine')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.patientprofile', verbose_name='Patient')),
            ],
            options={'verbose_name': 'Pharmacy Order', 'verbose_name_plural': 'Pharmacy Orders', 'ordering': ['-created_at']},
        ),
    ]