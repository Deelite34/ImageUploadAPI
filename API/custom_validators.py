from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
import magic


class MinValueValidatorIgnoreNull(MinValueValidator):
    """
    In addition to original validator functionality, returns
    True if value is None
    """
    def compare(self, a, b):
        if a is None:
            return True
        return a < b


class MaxValueValidatorIgnoreNull(MaxValueValidator):
    """
    In addition to original validator functionality, returns
    True if value is None
    """
    def compare(self, a, b):
        if a is None:
            return True
        return a > b


def validate_image_type(value):
    """
    Check if models.ImageField object is an allowed-type image
    :param value: models.ImageField object to identify
    """
    extensions = ['jpg', 'png']
    short = value.name[-3:]
    error_msg = f'Incorrect file type. Allowed types: {" ".join(extensions)}'

    if short not in extensions:
        raise ValidationError(error_msg)

    # Check if mimetype starts with any of allowed item from valid_data
    mimetype = magic.from_buffer(value.read())
    valid_data = ("PNG image data", "JPEG image data,")
    def check_correct_type(x): return True if mimetype.startswith(x) else False
    if not any(map(check_correct_type, valid_data)):
        raise ValidationError(error_msg)

    # There still are more ways to check if file is a secure to open image,
    # but there is no need to overthink validation for this project
