from django.contrib import admin

from core.admin_mixin import FlowIOAdminMixin
from .models import AllowedTelgramUsers, FlowConstraintGroup,Notifications, Service, FixedFlow, OptionalFlow, TelegramAuthSession, UserInactiveMessage, UserLogs
from .Forms.admin_forms import ServiceAdminForm
from .Forms.fixed_flow_forms import FixedFlowsForm
from .Forms.optional_flow_form import OptionalFlowForm

@admin.register(FixedFlow)
class FixedFlows(admin.ModelAdmin):
    form = FixedFlowsForm
    list_display = ("name", "users_list", "group")
    # change_list_template = "admin/core/fixedflow/change_list.html"
    def users_list(self, obj):
        return ", ".join(u.username for u in obj.users.all())
    
    users_list.short_description = "Users"
    
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    form = ServiceAdminForm
    list_display = ("name", "users_list", "created_at", "group")
    filter_horizontal = ("users","optional_flows")

    def users_list(self, obj):
        return ", ".join(u.username for u in obj.users.all())

    users_list.short_description = "Users"
    
    
@admin.register(OptionalFlow)
class OptionalFlowAdmin(admin.ModelAdmin):
    form = OptionalFlowForm
    list_display = ('name', 'is_active', 'order', 'created_at', "group") 
    ordering = ('order',)


# @admin.register(FlowConstraint)
# class FlowConstraintAdmin(admin.ModelAdmin):
#     form = FlowConstraintForm
#     list_display = ('left_flow', 'right_flow')


@admin.register(UserLogs)
class UserLogsAdmin(admin.ModelAdmin):
    list_display = ("date", "user", "service_name", "logtype", "info")
    list_filter = ("logtype", "user", "service_name", ("date", admin.DateFieldListFilter))
    search_fields = ("user__username", "service_name", "")
    ordering = ("-date",)
    readonly_fields = ("date", "user", "service_name", "logtype", "info")
    
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Notifications)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ("date", "user", "variables", "sucess")
    readonly_fields = ("date", "user", "variables", "sucess")
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

# admin.register(UserMessag@admin.register(FlowConstraint)


@admin.register(UserInactiveMessage)
class UserMessageAdmin(admin.ModelAdmin):
    list_display = ("user", "inactive_message")

# @admin.register(UserProxy)
# class UserProxyAdmin(admin.ModelAdmin):
#     list_display = ("ip", "port", "username", "password")

@admin.register(AllowedTelgramUsers)
class AllowedTelgramUsersAdmin(admin.ModelAdmin):
    list_display = ("user", "telegram_id")

@admin.register(TelegramAuthSession)
class TelegramAuthSessionAdmin(admin.ModelAdmin):
    readonly_fields = ("user", "telegram_id", "is_authenticated")
    list_display = ("user", "telegram_id", "is_authenticated")


@admin.register(FlowConstraintGroup)
class FlowConstraintGroup(admin.ModelAdmin):
    list_display = ('name', 'id')
    
