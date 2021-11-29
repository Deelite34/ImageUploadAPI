import os
from django.core.validators import MaxValueValidator
from django.db import models
from django.contrib.auth.models import User
from .utils import user_directory_path, set_generated_image_model_slug_and_expire_date
from .custom_validators import MinValueValidatorIgnoreNull, MaxValueValidatorIgnoreNull, \
                               validate_image_type


class CustomThumbnailSize(models.Model):
    """
    Contains custom sizes of thumbnail available to choose,
    when selecting account type.
    """

    # We don't want to have our server generate too big images
    size = models.PositiveSmallIntegerField(validators=[MaxValueValidator(4096)])

    def __str__(self):
        return f'{self.size}x{self.size}'


class AccountTypePermissions(models.Model):
    """
    Contains information about account type and its permissions.
    Custom thumbnail sizes can be added, by linking to CustomThumbnailSize
    trough custom_size foreign key.
    """

    name = models.CharField(max_length=50)
    create_200px_thumbnail_perm = models.BooleanField(default=False)
    create_400px_thumbnail_perm = models.BooleanField(default=False)
    create_original_img_link_perm = models.BooleanField(default=False)
    create_custom_sized_thumbnail_perm = models.BooleanField(default=False)
    create_time_limited_link_perm = models.BooleanField(default=False)
    custom_size = models.ManyToManyField(CustomThumbnailSize, blank=True,
                                         default=None)

    def __str__(self):
        return f'{self.name}'


class APIUserProfile(models.Model):
    """
    Specifies profile type,
    which contains information on allowed for that type thumbnail sizes, for specific user
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_type = models.ForeignKey(AccountTypePermissions, null=True, blank=True,
                                     on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.user.username}'


class StoredImage(models.Model):
    """
    Data on image uploaded by user
    """
    owner = models.ForeignKey(APIUserProfile, on_delete=models.CASCADE)
    img_height = models.PositiveIntegerField(blank=True)
    img_width = models.PositiveIntegerField(blank=True)
    file = models.ImageField(height_field='img_height',
                             width_field='img_width',
                             upload_to=user_directory_path,
                             validators=[validate_image_type])

    def __str__(self):
        return f'{os.path.basename(self.file.name)}'


class GeneratedImage(models.Model):
    """
    Data on images generated using source image and thumbnail sizes permissions
    """
    source_image = models.ForeignKey(StoredImage, related_name='thumbnails', on_delete=models.PROTECT)
    modified_image = models.ImageField(blank=True)
    slug = models.SlugField(max_length=15, blank=True)
    expire_time = models.IntegerField(default=None, blank=True, null=True, validators=[
        MinValueValidatorIgnoreNull(300),
        MaxValueValidatorIgnoreNull(30000)
    ])
    expire_date = models.DateTimeField(blank=True, null=True)  # checked when img is accessed
    type = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.id}'

    def save(self, *args, **kwargs):
        """
        In addition to standard save procedure, generate unique slug
        used for URL and set expire_date if expire_time is set
        """
        set_generated_image_model_slug_and_expire_date(self)
        super().save(*args, **kwargs)
