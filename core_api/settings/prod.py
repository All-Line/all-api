from .base import *  # noqa

AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")  # noqa: F405
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")  # noqa: F405

PROD_APPS = ["django_s3_storage"]

INSTALLED_APPS += PROD_APPS  # noqa

DEV_EMAIL = "squirre.lair.startnow@gmail.com"

WHITENOISE_STATIC_PREFIX = "/static/"

S3_BUCKET = "allline-zappa-static"
AWS_STORAGE_BUCKET_NAME = S3_BUCKET

STATICFILES_STORAGE = "django_s3_storage.storage.StaticS3Storage"
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_S3_BUCKET_NAME_STATIC = S3_BUCKET

AWS_S3_CUSTOM_DOMAIN = f"{S3_BUCKET}.s3.amazonaws.com"
STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"
MEDIA_URL = AWS_S3_CUSTOM_DOMAIN
