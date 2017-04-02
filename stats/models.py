import uuid
from django.contrib.postgres.fields import JSONField
from django.utils import timezone
from django.db import models
from django.template import Context, Template
from ordered_model.models import OrderedModel


class Team(models.Model):
    name = models.CharField(max_length=100)
    identifier = models.PositiveIntegerField()

    unique_together = (("name", "identifier"),)

    def __str__(self):
        return self.name

class Game(models.Model):
    img = models.ImageField(upload_to='game_avatars')
    basedir = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    teams = models.ManyToManyField(Team)

    def __str__(self):
        return self.name

class GameServer(OrderedModel):
    ip = models.GenericIPAddressField(unpack_ipv4=True)
    port = models.PositiveIntegerField(default=27015)
    hostname = models.TextField(blank=True, null=True, max_length=200)
    secret_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    game = models.ForeignKey(Game, on_delete=models.PROTECT)
    connected = models.BooleanField(default=False)

    unique_together = (("ip", "port"),)

    class Meta(OrderedModel.Meta):
        pass

    def __str__(self):
        return "{0}:{1}".format(self.hostname if self.hostname else self.ip, self.port)

class LogTag(models.Model):
    name = models.CharField(unique=True,max_length=50)
    pretty = models.TextField(blank=True)

    def __str__(self):
        return self.name

class ServerLog(models.Model):
    kind = models.CharField(max_length=200)
    data = JSONField()
    server = models.ForeignKey(GameServer, related_name='logs', on_delete=models.PROTECT)
    time = models.DateTimeField(default=timezone.now)
    tags = models.ManyToManyField(LogTag)

    @property
    def pretty_print_log(self):
        pretty = self.tags.all()[0].pretty
        if pretty:
            template = Template(pretty)
            context = Context(self.data)
            return template.render(context)
        else:
            return "{0}".format(self.data)

    def __str__(self):
        return "{0} {1}".format(self.server, self.time)
