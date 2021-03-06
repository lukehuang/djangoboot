from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import ugettext as _
from django.db.models import Q

from core.models import TimeStampedMixin, SlugField


class Team(TimeStampedMixin, models.Model):
    slug = SlugField(_('slug'), unique=True)
    name = models.CharField(_('name'), max_length=100, help_text=_('Display name.'))
    email = models.EmailField(_('email'))
    url = models.URLField(_('URL'), null=True, blank=True, help_text=_('Website.'))

    @models.permalink
    def get_absolute_url(self):
        return 'boots:team', [self.slug]

    @models.permalink
    def get_delete_url(self):
        return 'accounts:team_delete', [self.slug]

    @models.permalink
    def get_update_url(self):
        if self.default_users.all():
            return 'accounts:user_details', [self.slug]
        else:
            return 'accounts:team_update', [self.slug]

    @models.permalink
    def get_add_user_url(self):
        return 'accounts:team_add_user', [self.slug]

    @models.permalink
    def get_leave_url(self):
        return 'accounts:team_leave', [self.slug]

    def is_user(self):
        try:
            return self.default_users.all()[0]
        except IndexError:
            pass

    def is_team(self):
        return not self.is_user()

    def has_user(self, user):
        return user.team == self or self.users.filter(id=user.id)

    def __unicode__(self):
        return self.name


class UserManager(BaseUserManager):

    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        email = UserManager.normalize_email(email)

        team = Team(slug=username, name=username, email=email)
        team.save(using=self._db)

        user = self.model(team=team, username=email, email=email)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username,  email, password):
        email = UserManager.normalize_email(email)
        u = self.create_user(username, email, password)
        u.is_superuser = True
        u.save(using=self._db)
        return u


class User(TimeStampedMixin, AbstractBaseUser, PermissionsMixin):

    username = models.CharField(_('username'), max_length=100, unique=True)
    email = models.EmailField(_('email'), unique=True)

    team = models.ForeignKey(Team, related_name='default_users', verbose_name=_('default team'))
    teams = models.ManyToManyField(Team, related_name='users', verbose_name=_('teams'))

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __unicode__(self):
        return self.username

    def get_teams(self):
        return Team.objects.filter(Q(default_users=self) | Q(users=self))

    @property
    def is_staff(self):
        return self.is_superuser

    def get_short_name(self):
        return self.username

    def get_absolute_url(self):
        return self.team.get_absolute_url()
