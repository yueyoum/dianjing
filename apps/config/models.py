import os

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.core.exceptions import ValidationError

def upload_to(instance, filename):
    name = "config-{0}.zip".format(instance.version)
    return os.path.join(settings.UPLOAD_DIR, name)


class Config(models.Model):
    version = models.CharField(max_length=255, primary_key=True)
    config = models.FileField(upload_to=upload_to)
    des = models.TextField(blank=True)
    in_use = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = 'config'

    def __unicode__(self):
        return self.version


    def clean(self):
        condition = (~Q(version=self.version)) & Q(in_use=True)
        if not self.in_use:
            if Config.objects.filter(condition).count() == 0:
                raise ValidationError("No Config in use")

    def save(self, **kwargs):
        if self.in_use:
            Config.objects.filter(~Q(version=self.version)).update(in_use=False)

        super(Config, self).save(**kwargs)

    @classmethod
    def get_config(cls):
        try:
            return cls.objects.get(in_use=True)
        except Config.DoesNotExist:
            return None
