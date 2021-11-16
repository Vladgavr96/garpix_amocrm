from app.celery import app
from ..models import Amo


@app.task
def update_tokens_task():
    print('updating garpix_amocrm tokens...')
    amo = Amo.get_solo()
    amo.save()


app.add_periodic_task(43200, update_tokens_task, name='update_tokens')
