from time import time
import requests
from django.contrib.sites.models import Site
from django.db import models
from .amo import Amo


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
    def create_lead_order(cls, order):
        '''
        pipenv run python backend/manage.py shell -c "from order.models import Order; from garpix_amocrm.models import Lead; order = Order.objects.filter(id=11).first(); Lead.create_lead_order(order)"
        '''
        amo = Amo.get_solo()
        if order.user:
            return cls.create_lead_order_for_reg(order, amo)
        return cls.create_lead_order_for_unreg(order, amo)

    @classmethod
    def create_lead_order_for_reg(cls, order, amo):
        status = False
        if order.user.amo_contact_id not in [None, '']:
            contact_id = order.user.amo_contact_id
        else:
            url = f'{amo.cabinet_url}/api/v4/contacts'
            data = [{
                "first_name": order.user.first_name,
                "last_name": order.user.last_name,
                "custom_fields_values": [
                    {
                        "field_id": 794025,
                        "values": [{"value": order.user.position}, ]
                    },
                    {
                        "field_id": 794027,
                        "values": [{"value": order.user.phone}, ]
                    },
                    {
                        "field_id": 794029,
                        "values": [{"value": order.user.email}, ]
                    },
                    {
                        "field_id": 1195253,
                        "values": [{"value": order.get_customer_locality_display()}, ]
                    },
                    {
                        "field_id": 1213985,
                        "values": [{"value": order.user.company}, ]
                    },
                ]
            }, ]
            session = requests.Session()
            session.headers = {"Authorization": f'Bearer {amo.access_token}'}
            session.headers.update({'Content-Type': 'application/json'})
            response = session.post(url=url, json=data)
            if response.status_code == 200:
                contact_id = response.json()['_embedded']['contacts'][0]['id']
                order.user.amo_contact_id = contact_id
                order.user.save()
            else:
                contact_id = 0
        url = f'{amo.cabinet_url}/api/v4/leads'
        data = [
            {
                "source_name": order.customer_name,
                "source_uid": str(order.id),
                "pipeline_id": int(amo.pipeline_id),
                "_embedded": {
                    "leads": [
                        {
                            "name": "Заявка с сайта",
                            "custom_fields_values": [
                                {
                                    "field_code": "DELIVERY",
                                    "values": [{"value": 'Доставка' if order.delivery else 'Самовывоз'}]
                                },
                                {
                                    "field_code": "COMMENT",
                                    "values": [{"value": order.comment}]
                                }
                            ]
                        }
                    ],
                    "contacts": [{"id": int(contact_id)}, ],
                },
                "metadata": {
                    "form_id": "1",
                    "form_sent_at": int(time()),
                    "form_name": "Форма заявки с сайта",
                    "form_page": amo.redirect_url,
                }
            }
        ]
        session = requests.Session()
        session.headers = {"Authorization": f'Bearer {amo.access_token}'}
        session.headers.update({'Content-Type': 'application/json'})
        response = session.post(url=url, json=data)
        if response.status_code == 200:
            lead_data = response.json()
            uid = lead_data['_embedded']['leads'][0]['id']
            cls.objects.create(uid=uid, lead_data=lead_data)
            status = True
            entity_id = uid
            note_url = f'{amo.cabinet_url}/api/v4/leads/{entity_id}/notes'
            note = ''
            for order_item in order.order_items.all():
                note += f'{order_item.product_name}, {order_item.package_quantity} упаковок,' \
                        f' {order_item.item_quantity} штук, цена ед. {order_item.total_price}р\n'
            note += f'Сумма заказа: {order.total_cost}\n'
            if order.customer_company_name:
                note += f'Компания: {order.customer_company_name}\n'
            if order.customer_company_requisites:
                site_domain = Site.objects.first().domain
                note += f'Реквизиты: {site_domain + order.customer_company_requisites.url}\n'
            note += f'Населенный пункт: {order.get_customer_locality_display()}\n'
            note_data = [
                {
                    "note_type": "common",
                    "params": {
                        "text": note
                    }
                }
            ]
            response = session.post(url=note_url, json=note_data)
        return status

    @classmethod
    def create_lead_order_for_unreg(cls, order, amo):
        status = False
        url = f'{amo.cabinet_url}/api/v4/leads/unsorted/forms'
        site_domain = Site.objects.first().domain
        data = [
            {
                "source_name": order.customer_name,
                "source_uid": str(order.id),
                "pipeline_id": int(amo.pipeline_id),
                "_embedded": {
                    "leads": [
                        {
                            "name": "Заявка с сайта",
                            "custom_fields_values": [
                                {
                                    "field_code": "DELIVERY",
                                    "values": [{"value": 'Доставка' if order.delivery else 'Самовывоз'}]
                                },
                                {
                                    "field_code": "COMMENT",
                                    "values": [{"value": order.comment}]
                                }
                            ]
                        }
                    ],
                    "contacts": [
                        {
                            "name": order.customer_name,
                            "custom_fields_values": [
                                {
                                    "field_code": "PHONE",
                                    "values": [{"value": order.customer_phone}]
                                },
                                {
                                    "field_code": "EMAIL",
                                    "values": [{"value": order.customer_email}]
                                },
                                {
                                    "field_code": "COMPANY",
                                    "values": [{"value": order.customer_company_name}]
                                },
                                {
                                    "field_code": "REQUISITES",
                                    "values": [
                                        {"value": site_domain + order.customer_company_requisites.url
                                            if order.customer_company_requisites else ''}]
                                },
                                {
                                    "field_code": "LOCALITY",
                                    "values": [{"value": order.get_customer_locality_display()}]
                                }
                            ]
                        }
                    ],
                    "companies": [
                        {
                            "name": order.customer_company_name if order.customer_company_name else ''
                        }
                    ]
                },
                "metadata": {
                    "form_id": "1",
                    "form_sent_at": int(time()),
                    "form_name": "Форма заявки с сайта",
                    "form_page": amo.redirect_url,
                }
            }
        ]
        session = requests.Session()
        session.headers = {"Authorization": f'Bearer {amo.access_token}'}
        session.headers.update({'Content-Type': 'application/json'})
        response = session.post(url=url, json=data)
        if response.status_code == 200:
            lead_data = response.json()
            uid = lead_data['_embedded']['unsorted'][0]['uid']
            cls.objects.create(uid=uid, lead_data=lead_data)
            status = True
            entity_id = lead_data['_embedded']['unsorted'][0]['_embedded']['leads'][0]['id']
            note_url = f'{amo.cabinet_url}/api/v4/leads/{entity_id}/notes'
            note = ''
            for order_item in order.order_items.all():
                note += f'{order_item.product_name}, {order_item.package_quantity} упаковок,' \
                        f' {order_item.item_quantity} штук, цена ед. {order_item.total_price}р\n'
            note += f'Сумма заказа: {order.total_cost}'
            note_data = [
                {
                    "note_type": "common",
                    "params": {
                        "text": note
                    }
                }
            ]
            response = session.post(url=note_url, json=note_data)
        return status

    @classmethod
    def create_lead_feedback(cls, feedback):
        amo = Amo.get_solo()
        status = False
        url = f'{amo.cabinet_url}/api/v4/leads/unsorted/forms'
        when_contact = ''
        if feedback.is_urgent:
            when_contact = 'КАК МОЖНО СКОРЕЕ'
        else:
            when_contact += str(feedback.day_of_call) + '\n' if feedback.day_of_call else ''
            when_contact += str(feedback.time_of_call) + '\n' if feedback.time_of_call else ''

        data = [
            {
                "source_name": feedback.full_name,
                "source_uid": str(feedback.id),
                "pipeline_id": int(amo.pipeline_id),
                "_embedded": {
                    "leads": [
                        {
                            "name": "Обратная связь с сайта",
                        }
                    ],
                    "contacts": [
                        {
                            "name": feedback.full_name,
                            "custom_fields_values": [
                                {
                                    "field_code": "PHONE",
                                    "values": [{"value": feedback.phone_number}]
                                },
                                {
                                    "field_code": "WHEN_CONTACT",
                                    "values": [{"value": when_contact}]
                                },
                            ]
                        }
                    ],
                },
                "metadata": {
                    "form_id": "1",
                    "form_sent_at": int(time()),
                    "form_name": "Форма обратной связи с сайта",
                    "form_page": amo.redirect_url,
                }
            }
        ]
        session = requests.Session()
        session.headers = {"Authorization": f'Bearer {amo.access_token}'}
        session.headers.update({'Content-Type': 'application/json'})
        response = session.post(url=url, json=data)
        if response.status_code == 200:
            lead_data = response.json()
            uid = lead_data['_embedded']['unsorted'][0]['uid']
            cls.objects.create(uid=uid, lead_data=lead_data)
        return status

    @classmethod
    def create_unsorted(cls, order, amo, data):
        url = f'{amo.cabinet_url}/api/v4/leads/unsorted/forms'
        site_domain = Site.objects.first().domain


        session = requests.Session()
        session.headers = {"Authorization": f'Bearer {amo.access_token}'}
        session.headers.update({'Content-Type': 'application/json'})
        response = session.post(url=url, json=data)
        if response.status_code == 200:
            lead_data = response.json()
            uid = lead_data['_embedded']['unsorted'][0]['uid']#???
            cls.objects.create(uid=uid, lead_data=lead_data)
            entity_id = lead_data['_embedded']['unsorted'][0]['_embedded']['leads'][0]['id']#???
            note_url = f'{amo.cabinet_url}/api/v4/leads/{entity_id}/notes'
            note = ''
            for order_item in order.order_items.all():
                note += f'{order_item.product_name}, {order_item.package_quantity} упаковок,' \
                        f' {order_item.item_quantity} штук, цена ед. {order_item.total_price}р\n'
            note += f'Сумма заказа: {order.total_cost}'
            note_data = [
                {
                    "note_type": "common",
                    "params": {
                        "text": note
                    }
                }
            ]
            response = session.post(url=note_url, json=note_data)
            return entity_id
        else:
            return response.status_code, response.text

    @classmethod
    def create_lead(cls, order, amo, data):
        url = f'{amo.cabinet_url}/api/v4/leads'

        session = requests.Session()
        session.headers = {"Authorization": f'Bearer {amo.access_token}'}
        session.headers.update({'Content-Type': 'application/json'})
        response = session.post(url=url, json=data)
        if response.status_code == 200:
            lead_data = response.json()
            uid = lead_data['_embedded']['leads'][0]['id']
            cls.objects.create(uid=uid, lead_data=lead_data)
            entity_id = uid
            note_url = f'{amo.cabinet_url}/api/v4/leads/{entity_id}/notes'
            note = ''
            for order_item in order.order_items.all():
                note += f'{order_item.product_name}, {order_item.package_quantity} упаковок,' \
                        f' {order_item.item_quantity} штук, цена ед. {order_item.total_price}р\n'
            note += f'Сумма заказа: {order.total_cost}\n'
            if order.customer_company_name:
                note += f'Компания: {order.customer_company_name}\n'
            if order.customer_company_requisites:
                site_domain = Site.objects.first().domain
                note += f'Реквизиты: {site_domain + order.customer_company_requisites.url}\n'
            note += f'Населенный пункт: {order.get_customer_locality_display()}\n'
            note_data = [
                {
                    "note_type": "common",
                    "params": {
                        "text": note
                    }
                }
            ]
            response = session.post(url=note_url, json=note_data)
            return entity_id
        else:
            return response.status_code, response.text

