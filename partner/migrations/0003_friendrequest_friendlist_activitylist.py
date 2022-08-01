# Generated by Django 4.0.3 on 2022-05-02 08:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0002_activitiestest'),
    ]

    operations = [
        migrations.CreateModel(
            name='FriendRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(blank=True, default=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to='partner.user')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to='partner.user')),
            ],
        ),
        migrations.CreateModel(
            name='FriendList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('friends', models.ManyToManyField(blank=True, related_name='friends', to='partner.user')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user', to='partner.user')),
            ],
        ),
        migrations.CreateModel(
            name='ActivityList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activities', models.ManyToManyField(blank=True, related_name='activities', to='partner.activitiestest')),
                ('initiator', models.OneToOneField(default='', on_delete=django.db.models.deletion.CASCADE, related_name='initiator', to='partner.user')),
            ],
        ),
    ]