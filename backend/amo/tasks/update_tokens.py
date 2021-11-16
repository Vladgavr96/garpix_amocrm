from app.celery import app
from ..models import Amo


@app.task
def update_tokens_task():
    print('updating amo tokens...')
    amo = Amo.get_solo()
    amo.save()


app.add_periodic_task(43200, update_tokens_task, name='update_tokens')
