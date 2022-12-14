# Generated by Django 4.0.3 on 2022-04-30 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivitiesTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('initiator', models.CharField(max_length=32)),
                ('title', models.CharField(max_length=32)),
                ('nums', models.IntegerField(null=True)),
                ('startTime', models.DateTimeField(null=True)),
                ('endTime', models.DateTimeField(null=True)),
                ('location', models.CharField(max_length=100, null=True)),
                ('lat', models.CharField(max_length=20, null=True)),
                ('lng', models.CharField(max_length=20, null=True)),
                ('img', models.ImageField(blank=True, null=True, upload_to='images/')),
            ],
        ),
    ]
