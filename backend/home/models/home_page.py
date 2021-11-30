from garpix_page.models import BasePage
from garpix_amocrm.models import Lead



class HomePage(BasePage):
    template = "pages/testamo.html"



    def get_context(self, request=None, *args, **kwargs):
        context = super(HomePage, self).get_context(request, *args, **kwargs)
        data = {
            'name': 'Сделка #7309363',
            'price': 0,
            'responsible_user_id': 7650907,
            'group_id': 0,
            'status_id': 44176471,
            'pipeline_id': 4869595,
            'loss_reason_id': None,
            'created_by': 7650907
        }
        res = Lead.create_lead(data)
        print(res)
        #context.update(res)

        return context


    class Meta:
        verbose_name = "Testamo"
        verbose_name_plural = "Testamos"
        ordering = ("-created_at",)
