from django.contrib import admin

from auditlog.filters import ResourceTypeFilter
from auditlog.mixins import LogEntryAdminMixin
from auditlog.models import LogEntry


class LogEntryAdmin(admin.ModelAdmin, LogEntryAdminMixin):
    list_select_related = ["content_type", "actor"]
    list_display = ["created", "resource_url", "action", "msg_short", "user_url"]
    search_fields = [
        "timestamp",
        "object_repr",
        "changes",
        "actor__first_name",
        "actor__last_name",
        "actor__username",
    ]
    list_filter = ["action", ResourceTypeFilter]
    readonly_fields = ["created", "resource_url", "action", "user_url", "msg"]
    fieldsets = [
        (None, {"fields": ["created", "user_url", "resource_url"]}),
        ("Changes", {"fields": ["action", "msg"]}),
    ]

    def has_add_permission(self, request):
        # As audit admin doesn't allow log creation from admin
        return False


admin.site.register(LogEntry, LogEntryAdmin)
