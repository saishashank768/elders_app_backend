from django.core.exceptions import ValidationError
from django.conf import settings
import imghdr


def validate_file_size(value):
    max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 5 * 1024 * 1024)
    if value.size > max_size:
        raise ValidationError(f'File too large. Size should not exceed {max_size} bytes.')


def validate_image_type(value):
    # basic type check
    try:
        file_type = imghdr.what(value)
    except Exception:
        file_type = None
    allowed = ('jpeg', 'png', 'gif', 'bmp')
    if file_type is None:
        # allow if extension-based or unknown; further checks may be desired
        return
    if file_type not in allowed:
        raise ValidationError('Unsupported image type.')
