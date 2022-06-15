# Generated by Django 3.2.5 on 2021-09-16 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0013_alter_animeresponse_expectations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='animeresponse',
            name='expectations',
            field=models.CharField(blank=True, choices=[(None, 'Met expectations / no answer'), ('S', 'Surprise'), ('D', 'Disappointment')], max_length=1, null=True),
        ),
    ]