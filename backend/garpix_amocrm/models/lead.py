import requests
from django.db import models

from .amo import Amo

amo = Amo.get_solo()


class Lead(models.Model):
    uid = models.CharField(max_length=128, verbose_name='uid', blank=True, null=True)
    lead_data = models.JSONField(verbose_name='Данные заявки', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Лид'
        verbose_name_plural = 'Лиды'

    def __str__(self):
        return f'{self.uid} - {self.created_at}'

    @classmethod
    def create_unsorted_form(cls, data):
        url = f'{amo.cabinet_url}/api/v4/leads/unsorted/forms'
        session = requests.Session()
        session.headers = {"Authorization": f'Bearer {amo.access_token}'}
        session.headers.update({'Content-Type': 'application/json'})
        response = session.post(url=url, json=data)
        if response.status_code == 200:
            lead_data = response.json()
            entity_id = lead_data['_embedded']['unsorted'][0]['_embedded']['leads'][0]['id']
            return entity_id
        else:
            return response.status_code, response.text

    @classmethod
    def create_unsorted_sip(cls, data):
        url = f'{amo.cabinet_url}/api/v4/leads/unsorted/sip'
        session = requests.Session()
        session.headers = {"Authorization": f'Bearer {amo.access_token}'}
        session.headers.update({'Content-Type': 'application/json'})
        response = session.post(url=url, json=data)
        if response.status_code == 200:
            lead_data = response.json()
            entity_id = lead_data['_embedded']['unsorted'][0]['_embedded']['leads'][0]['id']
            return entity_id
        else:
            return response.status_code, response.text

    @classmethod
    def create_lead(cls, data):
        url = f'{amo.cabinet_url}/api/v4/leads'

        session = requests.Session()
        session.headers = {"Authorization": f'Bearer {amo.access_token}'}
        session.headers.update({'Content-Type': 'application/json'})
        response = session.post(url=url, json=data)
        if response.status_code == 200:
            lead_data = response.json()
            entity_id = lead_data['_embedded']['leads'][0]['id']
            return entity_id
        else:
            return response.status_code, response.text

    @classmethod
    def get_unsorted_list(cls):
        url = f'{amo.cabinet_url}/api/v4/leads/unsorted'
        session = requests.Session()
        session.headers = {"Authorization": f'Bearer {amo.access_token}'}
        response = session.get(url=url)
        if response.status_code == 200:
            unsorted_list = response.json()
            return unsorted_list
        else:
            return response.status_code, response.text

    @classmethod
    def get_unsorted(cls, uid):
        url = f'{amo.cabinet_url}/api/v4/leads/unsorted/{uid}'
        session = requests.Session()
        session.headers = {"Authorization": f'Bearer {amo.access_token}'}
        response = session.get(url=url)
        if response.status_code == 200:
            unsorted_element = response.json()
            return unsorted_element
        else:
            return response.status_code, response.text

    @classmethod
    def get_leads_list(cls):
        url = f'{amo.cabinet_url}/api/v4/leads'
        session = requests.Session()
        session.headers = {"Authorization": f'Bearer {amo.access_token}'}
        response = session.get(url=url)
        if response.status_code == 200:
            leads_list = response.json()
            return leads_list
        else:
            return response.status_code, response.text

    @classmethod
    def get_lead(cls, lead_id):
        url = f'{amo.cabinet_url}/api/v4/leads/{lead_id}'
        session = requests.Session()
        session.headers = {"Authorization": f'Bearer {amo.access_token}'}
        response = session.get(url=url)
        if response.status_code == 200:
            lead = response.json()
            return lead
        else:
            return response.status_code, response.text

    @classmethod
    def add_note_to_lead(cls, data, lead_id):
        url = f'{amo.cabinet_url}/api/v4/leads'
        session = requests.Session()
        session.headers = {"Authorization": f'Bearer {amo.access_token}'}
        session.headers.update({'Content-Type': 'application/json'})
        response = session.get(url=url)

        if response.status_code == 200:
            note_url = f'{amo.cabinet_url}/api/v4/leads/{lead_id}/notes'
            note_data = [
                {
                    "note_type": "common",
                    "params": {
                        "text": data
                    }
                }
            ]
            response = session.post(url=note_url, json=note_data)
            return response.status_code, response.text
        else:
            return response.status_code, response.text

    @classmethod
    def show_lead_fields(cls):
        url = f'{amo.cabinet_url}/api/v4/leads/custom_fields'
        session = requests.Session()
        session.headers = {"Authorization": f'Bearer {amo.access_token}'}
        response = session.get(url=url)
        if response.status_code == 200:
            lead_feields = response.json()
            return lead_feields
        else:
            return response.status_code, response.text

    @classmethod
    def create_lead_fields(cls, new_fields):
        url = f'{amo.cabinet_url}/api/v4/leads/custom_fields'
        session = requests.Session()
        session.headers = {"Authorization": f'Bearer {amo.access_token}'}
        session.headers.update({'Content-Type': 'application/json'})
        response = session.post(url=url, json=new_fields)
        if response.status_code == 200:
            return response
        else:
            return response.status_code, response.text
