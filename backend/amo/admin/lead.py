from django.contrib import admin

from ..models import Lead
from ..services.amo_admin import AmoServiceAdmin


@admin.register(Lead)
class LeadAdmin(AmoServiceAdmin, admin.ModelAdmin):
    pass
