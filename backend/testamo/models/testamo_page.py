
from garpix_page.models import BasePage
from garpix_amocrm.models import Lead



class TestamoPage(BasePage):
    template = "pages/testamo.html"



    def get_context(self, request=None, *args, **kwargs):
        context = super(TestamoPage, self).get_context(request, *args, **kwargs)

        data = {
            #!!!
        }
        Lead.create_lead(data=data)
        return context

    class Meta:
        verbose_name = "Testamo"
        verbose_name_plural = "Testamos"
        ordering = ("-created_at",)
