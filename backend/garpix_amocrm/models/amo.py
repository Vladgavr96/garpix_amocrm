import requests
from django.db import models
from solo.models import SingletonModel


class Amo(SingletonModel):
    client_id = models.CharField(max_length=128, verbose_name='ИД интеграции', blank=True, null=True)
    cabinet_url = models.CharField(max_length=128, verbose_name='Амо ЛК', blank=True, null=True)
    pipeline_id = models.CharField(max_length=128, verbose_name='ИД воронки', blank=True, null=True)
    client_secret = models.CharField(max_length=128, verbose_name='Секретный ключ', blank=True, null=True)
    authorization_code = models.CharField(max_length=1024, verbose_name='Код авторизации', blank=True, null=True)
    redirect_url = models.CharField(max_length=128, verbose_name='Ссылка для перенаправления', blank=True, null=True)
    access_token = models.CharField(max_length=1024, verbose_name='access token', blank=True, null=True)
    refresh_token = models.CharField(max_length=1024, verbose_name='refresh token', blank=True, null=True)

    class Meta:
        verbose_name = 'Амо'
        verbose_name_plural = 'Амо'

    def save(self, *args, **kwargs):
        if self.cabinet_url:
            self.access_token, self.refresh_token = self.get_tokens()
        super(Amo, self).save(*args, **kwargs)

    def get_tokens(self):
        url = f'{self.cabinet_url}/oauth2/access_token'
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': self.authorization_code,
            'redirect_uri': self.redirect_url,
        }

        response = requests.post(url=url, data=data)

        status = response.json().get('status', None)
        if status:
            data.pop('code')
            data.update({
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
            })
            response = requests.post(url=url, data=data)
            status = response.json().get('status', None)
            if status:
                return '', ''
        return response.json()['access_token'], response.json()['refresh_token']
