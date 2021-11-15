from django.contrib import admin
from .models import APIUserProfile, CustomThumbnailSize,\
                    AccountTypePermissions, GeneratedImage, StoredImage


class AccountTypePermissionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'create_200px_thumbnail_perm', 'create_400px_thumbnail_perm',
                    'create_original_img_link_perm', 'create_time_limited_link_perm',
                    'create_custom_sized_thumbnail_perm')


class CustomThumbnailSizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'size')


class APIUserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'account_type')


class StoredImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'file')


class GeneratedImagesAdmin(admin.ModelAdmin):
    list_display = ('id', 'source_image', 'modified_image', 'type', 'slug', 'created', 'expire_date')


admin.site.register(AccountTypePermissions, AccountTypePermissionsAdmin)
admin.site.register(CustomThumbnailSize, CustomThumbnailSizeAdmin)
admin.site.register(APIUserProfile, APIUserProfileAdmin)
admin.site.register(StoredImage, StoredImageAdmin)
admin.site.register(GeneratedImage, GeneratedImagesAdmin)
