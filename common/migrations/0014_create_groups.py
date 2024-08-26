from django.contrib.auth.models import Group
from django.db import migrations

def create_groups(apps, schema_editor):
    Group.objects.get_or_create(name='Admin')
    Group.objects.get_or_create(name='Sales Manager')
    Group.objects.get_or_create(name='Sales Representative')
    Group.objects.get_or_create(name='Generic Employee')

class Migration(migrations.Migration):

    dependencies = [
        ('common', '0013_merge_20240812_1623'),
    ]

    operations = [
        migrations.RunPython(create_groups),
    ]
