from django.db import migrations


def create_default_auth_config(apps, schema_editor):
    AuthConfig = apps.get_model('common', 'AuthConfig')
    AuthConfig.objects.create(is_google_login=False, created_by=None)


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0013_merge_20240812_1623'),
    ]

    operations = [
        migrations.RunPython(create_default_auth_config),
    ]
