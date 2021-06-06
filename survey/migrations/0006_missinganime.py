# Generated by Django 3.1 on 2021-06-06 00:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('survey', '0005_auto_20210412_1920'),
    ]

    operations = [
        migrations.CreateModel(
            name='MissingAnime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.URLField()),
                ('description', models.TextField(blank=True)),
                ('is_read', models.BooleanField(default=False)),
                ('anime', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='survey.anime')),
                ('survey', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='survey.survey')),
                ('user', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
