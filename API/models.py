import os
from django.core.validators import MaxValueValidator
from django.db import models
from django.contrib.auth.models import User
from .custom_validators import MinValueValidatorIgnoreNull, MaxValueValidatorIgnoreNull, \
                               validate_image_type


def user_directory_path(instance, filename):
    """Used for specifying unique for each user file path of
    stored files, using his ID number"""
    return 'user_{0}/{1}'.format(instance.owner.user.id, filename)


class CustomThumbnailSize(models.Model):
    """Contains custom sizes of thumbnail available to choose,
    when selecting account type"""

    # We don't want to have our server create, store and display too big images
    size = models.PositiveSmallIntegerField(validators=[MaxValueValidator(4096)])

    def __str__(self):
        return f'{self.size}x{self.size} px'


class AccountTypePermissions(models.Model):
    """Contains information about account type and its permissions.
    Custom thumbnail sizes can be added, by linking to CustomThumbnailSize
    trough custom_size foreign key."""

    name = models.CharField(max_length=50)
    create_200px_thumbnail_perm = models.BooleanField(default=False)
    create_400px_thumbnail_perm = models.BooleanField(default=False)
    get_original_img_link_perm = models.BooleanField(default=False)
    create_time_limited_link_perm = models.BooleanField(default=False)

    custom_size = models.ManyToManyField(CustomThumbnailSize, blank=True,
                                         default=None)

    def __str__(self):
        return f'{self.name}'


class APIUserProfile(models.Model):
    """Specifies information how can specific user
    use the api trough account_type field"""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_type = models.ForeignKey(AccountTypePermissions, null=True, blank=True,
                                     on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.user.username}'


class StoredImage(models.Model):
    owner = models.ForeignKey(APIUserProfile, on_delete=models.CASCADE)
    file = models.ImageField(upload_to=user_directory_path, validators=[
                             validate_image_type])

    def __str__(self):
        return f'{os.path.basename(self.file.name)}'


class GeneratedImage(models.Model):
    """
    Information on created, based
    """
    original_image = models.ForeignKey(APIUserProfile, on_delete=models.CASCADE)
    url = models.URLField()
    filename = models.CharField(max_length=100)
    expire_time = models.IntegerField(default=None, blank=True, null=True, validators=[
        MinValueValidatorIgnoreNull(300),
        MaxValueValidatorIgnoreNull(30000)
    ])
    size = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.id}'
