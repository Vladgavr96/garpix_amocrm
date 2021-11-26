from django.db import models
from garpix_page.models import BasePage
from garpix_amocrm.models import Lead



class TestamoPage(BasePage):
    template = "pages/testamo.html"
    data = {

    }
    Lead.create_lead(data = data)

    class Meta:
        verbose_name = "Testamo"
        verbose_name_plural = "Testamos"
        ordering = ("-created_at",)
