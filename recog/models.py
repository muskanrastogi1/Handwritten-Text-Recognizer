from django.db import models
from uuid import uuid4
import uuid, os
# Create your models here.

def upload(instance, filename):
    upload_to = 'handwriting'
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}.{}'.format(instance.pk, ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)


class Handwriting(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    image = models.ImageField(upload_to=upload, null=True)
    text = models.TextField(null=True)