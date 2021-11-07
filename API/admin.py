from django.contrib import admin
from .models import APIUserProfile, CustomThumbnailSize,\
                    AccountTypePermissions, GeneratedImage, StoredImage


class AccountTypePermissionsAdmin(admin.ModelAdmin):
    list_display = ('name', 'create_200px_thumbnail_perm', 'create_400px_thumbnail_perm',
                    'get_original_img_link_perm', 'create_time_limited_link_perm')


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_type')


admin.site.register(APIUserProfile, UserProfileAdmin)
admin.site.register(CustomThumbnailSize)
admin.site.register(AccountTypePermissions, AccountTypePermissionsAdmin)
admin.site.register(GeneratedImage)
admin.site.register(StoredImage)
