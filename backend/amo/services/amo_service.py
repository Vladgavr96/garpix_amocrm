import logging

import requests
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError

from ..models import Amo


class AmoConnect:

    def __init__(self):
        try:
            self.amo = Amo.get_solo()
            self.api_contacts = f'{self.amo.cabinet_url}/api/v4/contacts'
            self.api_companies = f'{self.amo.cabinet_url}/api/v4/companies'
            self.api_leads = f'{self.amo.cabinet_url}/api/v4/leads'

            self.api_leads_pipelines = f'{self.api_leads}/pipelines/{self.amo.pipeline_id}'

            self.session = self.set_session()
        except ObjectDoesNotExist as e:
            logging.warning(e)
        except:  # noqa
            logging.error("Amo settings don't find.")

    def set_session(self) -> requests.Session:
        session = requests.Session()
        session.headers = {"Authorization": f'Bearer {self.amo.access_token}'}
        session.headers.update({'Content-Type': 'application/json'})
        return session

    # GET requests

    def fetch_leads_pipelines(self):
        """Метод позволяет получить список воронок сделок в аккаунте."""
        response = self.session.get(url=self.api_leads_pipelines)
        return self._get_response(response)
        # if response.status_code == 200:
        #     return response
        # raise ValidationError({
        #     "status": response.status_code,
        #     "content": response.content
        # })

    def fetch_leads(self):
        response = self.session.get(url=self.api_leads)
        return self._get_response(response)
        # if response.status_code == 200:
        #     return response
        # raise ValidationError('fetch_leads() was fail')

    def fetch_contacts(self, query: str = ''):
        filter_by = self._prepare_filter(query)
        response = self.session.get(url=self.api_contacts, params=filter_by)
        return self._get_response(response)

    def fetch_companies(self, query: str = ''):
        filter_by = self._prepare_filter(query)
        response = self.session.get(url=self.api_companies, params=filter_by)
        return self._get_response(response)



    # POST requests

    def post_lead_to_first_contact(self, order):
        company_id = self.fetch_company_id(order)
        contact_id = self.fetch_contact_id(order)

        data = [
            {
                "name": f"Заказ:{order.pk} № {order.number}",
                # [note] Not needed "price": int(order.total_cost),
                "pipeline_id": int(self.amo.pipeline_id),
                "custom_fields_values": [
                    {
                        "field_code": "DELIVERY",
                        "values": [{"value": 'Доставка' if order.delivery else 'Самовывоз'}]
                    },
                    {
                        "field_code": "COMMENT",
                        "values": [{"value": order.comment}]
                    }
                ],
                "_embedded": {
                    "companies": [
                        {
                            "id": company_id,
                        }
                    ],
                    "contacts": [
                        {
                            "id": contact_id,
                        }
                    ]

                }
            }
        ]

        response = self.session.post(self.api_leads, json=data)

        if response.status_code == 200:
            lead_data = response.json()

            entity_id = lead_data['_embedded']['leads'][0]['id']
            note_url = f'{self.amo.cabinet_url}/api/v4/leads/{entity_id}/notes'

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

            self.session.post(url=note_url, json=note_data)

            return response
        else:
            logging.warning(response.__dict__)
            raise ValidationError('Произошла ошибка при добавлении "Сделки" в "Первичный контакт"')

    def _get_response(self, response):
        if response.status_code == 200:
            return response
        raise ValidationError({
            "status": response.status_code,
            "content": response.content
        })

    def _prepare_filter(self, query: str) -> dict:
        filter_by = dict()
        if query != '':
            filter_by.update({"filter[name]": query})
        return filter_by

    def _fetch_objects_by_name(self, response, key: str) -> int:
        _id = 0
        try:
            found = response.json()['_embedded'][key]

            if len(found) == 1:
                _id = found[0]['id']
            elif len(found) > 2:
                logging.warning(f'Найдено несколько объектов с таким наименованием: {found}. Взято первое!')
                _id = found[0]['id']
            elif _id == 0:
                logging.warning('Объект не определен!')
        except Exception as e:
            logging.warning('Объекты не найдены.', e)

        return _id
