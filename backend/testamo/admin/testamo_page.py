from ..models.testamo_page import TestamoPage
from django.contrib import admin
from garpix_page.admin import BasePageAdmin


@admin.register(TestamoPage)
class TestamoPageAdmin(BasePageAdmin):
    list_display = ('__all__')