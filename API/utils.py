from datetime import datetime, timedelta

import pytz
from django.utils.crypto import get_random_string
from API.models import GeneratedImage


def user_directory_path(instance, filename):
    """
    Used for specifying unique for each user file path of
    stored files, using his ID number.
    Usable in a imagefield model field, in upload_to parameter.
    """
    return 'user_{0}/{1}'.format(instance.owner.user.id, filename)


def set_generated_image_model_slug_and_expire_date(obj):
    """
    Sets parameters of GeneratedImage model.
    Generates and sets slug,
    sets expire_date using expire_time
    :param obj: object of GeneratedImage model
    """
    if not obj.slug:
        obj.slug = get_random_string(15)
    while GeneratedImage.objects.filter(slug=obj.slug).count() != 0:
        obj.slug = get_random_string(15)

    if obj.expire_time is not None and obj.expire_date is None:
        timezone = pytz.timezone('CET')
        now = datetime.now(timezone)
        obj.expire_date = now + timedelta(seconds=int(obj.expire_time))
