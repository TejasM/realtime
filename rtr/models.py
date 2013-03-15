import datetime
from django.db import models
from django import forms
from django.core import exceptions
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _


class Series(models.Model):
    live = models.BooleanField(default=False)
    series_id = models.CharField(max_length=200)


class Session(models.Model):
    series = models.ForeignKey(Series)
    create_time = models.DateTimeField('date published')

    def __unicode__(self):
        return self.series.seriesId


class DictionaryField(models.Field):
    description = _("Dictionary object")

    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return "TextField"

    def to_python(self, value):
        if value is None:
            return None
        elif value == "":
            return {}
        elif isinstance(value, basestring):
            try:
                return dict(simplejson.loads(value))
            except (ValueError, TypeError):
                raise exceptions.ValidationError(self.error_messages['invalid'])

        if isinstance(value, dict):
            return value
        else:
            return {}

    def get_prep_value(self, value):
        if not value:
            return ""
        elif isinstance(value, basestring):
            return value
        else:
            return simplejson.dumps(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def clean(self, value, model_instance):
        value = super(DictionaryField, self).clean(value, model_instance)
        return self.get_prep_value(value)

    def formfield(self, **kwargs):
        defaults = {'widget': forms.Textarea}
        defaults.update(kwargs)
        return super(DictionaryField, self).formfield(**defaults)


class Stats(models.Model):
    session = models.ForeignKey(Session)
    user_id = models.CharField(max_length=200)
    stats = DictionaryField()