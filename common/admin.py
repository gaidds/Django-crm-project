from django.contrib import admin

from common.models import Address, Comment, CommentFiles, User, AuthConfig

# Register your models here.

admin.site.register(User)
admin.site.register(Address)
admin.site.register(Comment)
admin.site.register(CommentFiles)
admin.site.register(AuthConfig)
