# Generated by Django 5.1.5 on 2025-02-25 10:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='buy',
            name='address',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.userdtl'),
            preserve_default=False,
        ),
    ]
