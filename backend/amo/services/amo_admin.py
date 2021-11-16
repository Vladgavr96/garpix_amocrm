import json

from django.contrib import messages
from django.utils.safestring import mark_safe

from .amo_service import AmoConnect


class AmoServiceAdmin:

    actions = [
        'get_amo_leads_pipelines',
        'get_amo_leads',
        'get_amo_contacts',
        'post_lead'
    ]

    def __init__(self, *args, **kwargs):
        super(AmoServiceAdmin, self).__init__(*args, **kwargs)
        self.connect = AmoConnect()

    def get_amo_contacts(self, request, queryset):
        result = self.connect.fetch_contacts().json()
        return AmoServiceAdmin.show_message(request, result)
    get_amo_contacts.short_description = 'Список Контактов (Амо)'

    def get_amo_leads_pipelines(self, request, queryset=None):
        connect = AmoConnect()
        leads_pipelines = connect.fetch_leads_pipelines().json()
        return AmoServiceAdmin.show_message(request, leads_pipelines)
    get_amo_leads_pipelines.short_description = 'Список воронок сделок (Амо)'

    def get_amo_leads(self, request, queryset=None):
        connect = AmoConnect()
        leads = connect.fetch_leads().json()
        return AmoServiceAdmin.show_message(request, leads)
    get_amo_leads.short_description = 'Список сделкок (Амо)'

    @staticmethod
    def show_message(request, json_data):
        html = mark_safe(
            f'<pre><small>'
            f'{json.dumps(json_data, indent=4, sort_keys=True, ensure_ascii=False)}'
            f'</small></pre>')
        return messages.success(request, html)
