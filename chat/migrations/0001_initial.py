# Generated by Django 5.1 on 2024-08-26 12:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='EmailMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255)),
                ('date_sent', models.DateTimeField()),
                ('date_received', models.DateTimeField()),
                ('body', models.TextField()),
                ('email_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.emailaccount')),
            ],
        ),
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=255)),
                ('file_data', models.BinaryField()),
                ('email_message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='chat.emailmessage')),
            ],
        ),
    ]
