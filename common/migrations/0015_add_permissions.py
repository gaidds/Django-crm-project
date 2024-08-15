from django.contrib.auth.models import Group, Permission
from django.db import migrations

def add_permissions(apps, schema_editor):
    admin_group = Group.objects.get(name='Admin')
    sales_manager_group = Group.objects.get(name='Sales Manager')
    sales_rep_group = Group.objects.get(name='Sales Representative')
    employee_group = Group.objects.get(name='Generic Employee')

    # Add permissions to Grneric Employee group
    employee_group_permissions = []

    for perm in employee_group_permissions:
        permission = Permission.objects.get(codename=perm)
        employee_group.permissions.add(permission)



    # Add permissions to Sales Representative group
    sales_rep_group_permissions = []

    for perm in sales_rep_group_permissions:
        permission = Permission.objects.get(codename=perm)
        sales_rep_group.permissions.add(permission)



    # Add permissions to Sales Manager group
    sales_manager_group_permissions = []

    for perm in sales_manager_group_permissions:
        permission = Permission.objects.get(codename=perm)
        sales_manager_group.permissions.add(permission)



    # Add permissions to Admin group
    all_permissions = Permission.objects.all()
    admin_group.permissions.set(all_permissions)

class Migration(migrations.Migration):

    dependencies = [
        ('common', '0014_create_groups'),
    ]

    operations = [
        migrations.RunPython(add_permissions),
    ]
