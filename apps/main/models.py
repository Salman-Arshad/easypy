from django.db import models


# Create your models here.
class Execution(models.Model):
    running = 'running'
    killed = 'killed'
    missing = 'missing'
    status_choices = (
        (running, 'Running'),
        (killed, 'Killed'),
        (missing, 'Missing'),
    )
    pid = models.IntegerField()
    dt_start = models.DateTimeField(auto_now_add=True)
    dt_end = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=100, choices=status_choices, default=running)
    objects = models.Manager()

    def __str__(self):
        return '%(pid)s - %(status)s' % self.__dict__
