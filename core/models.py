from pyexpat import model
from django.db import models
from django.contrib.auth.models import User
import json
import pathlib
import uuid
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

FLOW_SCHEMA =pathlib.Path(__file__).parent /'schema' /'flow_schema.json'
with open(FLOW_SCHEMA, "r") as f:
    FLOW_SCHEMA = json.load(f)

INPUT_SCHEMA = pathlib.Path(__file__).parent / 'schema' / 'inputs_schema.json'
with open(INPUT_SCHEMA, "r") as f:
    INPUT_SCHEMA = json.load(f)


class FlowConstraintGroup(models.Model):
    name = models.CharField(max_length=200, blank=True)
    
    class Meta:
        unique_together = ('name',)

    def __str__(self):
        return self.name or f"Group {self.id}"
        
class OptionalFlow(models.Model):
    name = models.CharField(max_length=200)
    flows = models.JSONField()
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    # this is used to group flows
    group = models.ForeignKey(
        FlowConstraintGroup,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    users = models.ManyToManyField(
        User,
        related_name="optional_flows",
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name
    
class Service(models.Model):
    users = models.ManyToManyField(User, related_name="services")
    optional_flows = models.ManyToManyField(
        OptionalFlow,
        related_name="services",
        blank=True
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    inputs = models.JSONField()
    flows = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(
        FlowConstraintGroup,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
class FixedFlow(models.Model):
    name = models.CharField(max_length=200)
    flows = models.JSONField()
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField(User, related_name="fixed_flows", blank=True)
    notify_condition= models.JSONField(null=True, blank=True)
    success_value = models.JSONField(null=True, blank=True)
    notify_variables = models.JSONField(null=True, blank=True)
    group = models.ForeignKey(
        FlowConstraintGroup,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    class Meta:
        ordering = ["order"]
    
    def __str__(self):
        return self.name
    

class UserLogs(models.Model):

    user = models.CharField(max_length=100, blank=True, null=True)
    service_name = models.CharField(max_length=100, blank=True, null=True)
    logtype = models.CharField(max_length=10)
    info = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.logtype}] {self.service_name or 'Unknown'} - {self.info[:50]}"


class Notifications(models.Model):
    user = models.CharField()
    variables = models.JSONField(null=True, blank=True)
    sucess = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.variables}"
    
class UserInactiveMessage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    inactive_message = models.TextField(
        blank=True,
        default="Your account is inactive. Please contact support."
    )
    
    def __str__(self):
        return self.user.username

class UserProxy(models.Model):
    ip = models.CharField(max_length=100, blank=True, null=True)
    port = models.CharField(max_length=100, blank=True, null=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)

    users = models.ManyToManyField(User, related_name="user_proxu", blank=True)

class TelegramAuthSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="telegram_sessions", null=True, blank=True)
    token = models.CharField(max_length=600, unique=True)
    telegram_id = models.CharField(max_length=50, blank=True, null=True)
    is_authenticated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user} - {self.telegram_id or 'Not linked'}"

class AllowedTelgramUsers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="allowed_telegram_users", null=True, blank=True)
    telegram_id = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.telegram_id or 'Not linked'}"