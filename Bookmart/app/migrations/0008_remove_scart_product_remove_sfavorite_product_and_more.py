# Generated by Django 5.1.5 on 2025-02-23 13:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_scart_sfavorite'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scart',
            name='product',
        ),
        migrations.RemoveField(
            model_name='sfavorite',
            name='product',
        ),
        migrations.RemoveField(
            model_name='scart',
            name='user',
        ),
        migrations.RemoveField(
            model_name='sfavorite',
            name='user',
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='Sbook',
        ),
        migrations.DeleteModel(
            name='Scart',
        ),
        migrations.DeleteModel(
            name='Sfavorite',
        ),
    ]
