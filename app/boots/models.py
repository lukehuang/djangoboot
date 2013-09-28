from django.db import models
from django.utils.translation import ugettext as _

from taggit.managers import TaggableManager

from core.models import TimeStampedMixin
from accounts.models import Group


class Boot(TimeStampedMixin, models.Model):
    TYPE_PROJECT = 'P'
    TYPE_APP = 'A'

    TYPES = (
        (TYPE_PROJECT, _('project')),
        (TYPE_APP, _('application')),
    )

    group = models.ForeignKey(Group, verbose_name=_('group'))
    slug = models.SlugField(_('slug'))
    type = models.CharField(_('type'), max_length=1, choices=TYPES)
    tags = TaggableManager(verbose_name=_('tags'))


class BootVersion(TimeStampedMixin, models.Model):
    boot = models.ForeignKey(Boot, verbose_name=_('boot'))
    source = models.URLField(_('source'))
    name = models.CharField(_('name'), max_length=50)
