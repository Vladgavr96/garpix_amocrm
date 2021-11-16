from django.contrib import admin
from solo.admin import SingletonModelAdmin

from ..models import Amo


@admin.register(Amo)
class AmoAdmin(SingletonModelAdmin):
    pass
