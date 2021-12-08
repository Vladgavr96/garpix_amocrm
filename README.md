# GarpixCMS Empty Template

Cookiecutter template for GarpixCMS == 1.0.0.

## Install

1. Install Docker and docker-compose.
   
For Debian, Ubuntu:

```
su
apt update; apt upgrade -y; apt install -y curl; curl -sSL https://get.docker.com/ | sh; curl -L https://github.com/docker/compose/releases/download/1.28.2/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose
```

Don't forget press CTRL+D to exit from super user account.

2. Apply environment variables:

```
cp example.env .env
```

3. Change a random string for `SECRET_KEY` and `POSTGRES_PASSWORD` in `.env`.

4. Install dependencies:

```
pipenv install
pipenv shell
```

5. Up docker-compose, migrate database and create super user:

```
docker-compose up -d
python3 backend/manage.py makemigrations
python3 backend/manage.py migrate
python3 backend/manage.py createsuperuser
```

6. Run the server:

```
python3 backend/manage.py runserver
```

7. Enjoy!

Начало работы.
Заполните раздел Амо в административной панели.
Токены генерируются автоматически. ИД воронки можно взять из URL в разделе сделки на сайте amocrm. Остальные данные получаются при создании интеграции в личном кабинете amocrm

Методы
```
create_unsorted_forms - создание несортированной формы
```
```
create_unsorted_sip - создание несортированного звонка
```
```
create_lead - создание нового лида. Обязательные поля :
name
price
Примечание: словарь с данными обязательно должен быть внутри списка
```
```
get_unsorted_list - запрашивает список несортированных объектов со всеми их полями
```
```
get_leads_list -запрашивает список лидов со всеми их полями
```
```
get_unsorted - запрашивает несортированный объект по id
```
```
get_lead -запрашивает лид по id
```
```
add_note_to_lead - Добавляет комментарий к лиду с указанным id
```
```
show_lead_field - Показывает все доступные поля для лидов, включая кастомные
```
```
create_lead_fields - добавление кастомных полей к лидам. Обязательные поля :
name
type - тип данных поля. 
	Примечание: словарь с данными обязательно должен быть внутри списка
```
Ссылка на документацию
https://www.amocrm.ru/developers/content/crm_platform/api-reference

Ссылка на несортированое в документации 
https://www.amocrm.ru/developers/content/crm_platform/unsorted-api#unsorted-add-form

Ссылка на Лиды в документации
https://www.amocrm.ru/developers/content/crm_platform/leads-api

Список доступных типов данных для кастомных полей 
https://www.amocrm.ru/developers/content/crm_platform/custom-fields#cf-types

Поля и группы полей
https://www.amocrm.ru/developers/content/crm_platform/custom-fields

