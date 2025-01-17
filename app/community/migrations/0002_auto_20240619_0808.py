# Generated by Django 3.2.6 on 2024-06-19 08:08

from django.conf import settings
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('community', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='communitydetail',
            options={'verbose_name_plural': 'Community Details'},
        ),
        migrations.AlterModelOptions(
            name='communityjoinrequest',
            options={'verbose_name_plural': 'Community Join Requests'},
        ),
        migrations.AlterModelOptions(
            name='communitymembership',
            options={'verbose_name_plural': 'Community Memberships'},
        ),
        migrations.AlterModelOptions(
            name='eventcollaboration',
            options={'verbose_name_plural': 'Event Collaborations'},
        ),
        migrations.AlterModelOptions(
            name='eventregistration',
            options={'verbose_name_plural': 'Event Registrations'},
        ),
        migrations.RemoveField(
            model_name='communityjoinrequest',
            name='approved',
        ),
        migrations.AddField(
            model_name='communityjoinrequest',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'APPROVED'), ('declined', 'DECLINED')], default='pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='community',
            name='slug',
            field=models.CharField(max_length=20, unique=True, validators=[django.core.validators.MinLengthValidator(5)]),
        ),
        migrations.AlterUniqueTogether(
            name='communitymembership',
            unique_together={('user', 'community')},
        ),
        migrations.AlterUniqueTogether(
            name='eventcollaboration',
            unique_together={('event', 'collaborating_community')},
        ),
    ]
