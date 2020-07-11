import os
from django.db import models
from datetime import date
from django.utils.translation import gettext_lazy as _
from .storage import this_storage


# Create your models here.
# noinspection SpellCheckingInspection
class HookNotification(models.Model):
    name = models.CharField(_("name"), max_length=100, blank=True, null=True)
    exchange = models.CharField(_("exchange"), max_length=100, blank=True, null=True)
    ticker = models.CharField(_("ticker"), max_length=100, blank=True, null=True)
    volume = models.FloatField(_("volume"), blank=True, null=True)
    hopen = models.FloatField(_("open"), blank=True, null=True)
    close = models.FloatField(_("close"), blank=True, null=True)
    high = models.FloatField(_("high"), blank=True, null=True)
    low = models.FloatField(_("low"), blank=True, null=True)
    time = models.DateTimeField(_("time"), blank=True, null=True)
    signal = models.IntegerField(_("signal"))
    timenow = models.DateTimeField(_("timenow"))

    class Meta:
        ordering = ['-id']

    @property
    def me_csv(self):
        ff = '%(name)s,%(exchange)s,%(ticker)s,%(volume)s,%(hopen)s,%(close)s,%(high)s,%(low)s,%(time)s,%(timenow)s\n'
        return ff % self.__dict__

    def save(self, **kwargs):
        notification_csv = os.path.join(this_storage.location, 'notification_csv')
        try:
            os.makedirs(notification_csv)
        except FileExistsError:
            pass

        file_name = os.path.join(notification_csv, '%s.csv' % date.today().strftime('%Y%m%d'))
        file_already_exists = os.path.exists(file_name)
        with open(file_name, 'a') as f:
            if not file_already_exists:
                f.write('timestamp,signal\n')
            f.write('%(timenow)s,%(signal)s\n' % self.__dict__)
