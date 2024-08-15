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
    sales_rep_group_permissions = [
        'change_userprofile', 'view_userprofile', 'view_document', 'add_uploadeddocument', 'change_uploadeddocument', 'delete_uploadeddocument', 'view_uploadeddocument', 'view_image', 'add_uploadedimage', 'change_uploadedimage', 'delete_uploadedimage', 'view_uploadedimage', 'view_page', 'add_site', 'change_site', 'delete_site', 'view_site', 'add_taskstate', 'change_taskstate', 'delete_taskstate', 'view_taskstate', 'add_comment', 'change_comment', 'delete_comment', 'view_comment', 'add_commentreply', 'change_commentreply', 'delete_commentreply', 'view_commentreply', 'view_homepage', 'view_menu', 'view_menuitem', 'change_user', 'view_user', 'add_address', 'change_address', 'delete_address', 'view_address', 'add_attachments', 'change_attachments', 'delete_attachments', 'view_attachments', 'add_comment', 'change_comment', 'delete_comment', 'view_comment', 'add_commentfiles', 'change_commentfiles', 'delete_commentfiles', 'view_commentfiles', 'view_org', 'view_profile', 'add_document', 'change_document', 'delete_document', 'view_document', 'add_account', 'change_account', 'delete_account', 'view_account', 'add_accountemail', 'change_accountemail', 'delete_accountemail', 'view_accountemail', 'add_contact', 'change_contact', 'delete_contact', 'view_contact', 'add_email', 'change_email', 'delete_email', 'view_email', 'add_company', 'change_company', 'delete_company', 'view_company', 'add_lead', 'change_lead', 'delete_lead', 'view_lead', 'add_opportunity', 'change_opportunity', 'delete_opportunity', 'view_opportunity', 'add_invoice', 'change_invoice', 'delete_invoice', 'view_invoice', 'view_invoicehistory', 'add_image', 'change_image', 'delete_image', 'add_task', 'change_task', 'delete_task', 'view_task'
    ]

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
        ('common', '0016_delete_duplicate_permissions'),
    ]

    operations = [
        migrations.RunPython(add_permissions),
    ]
