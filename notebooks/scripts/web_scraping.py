import re, os
from queue import Queue, Empty
from threading import Thread
from time import sleep

from db_scraping import DBScraping
from workers.representantesAsistenciaCamaraWork import RepresentantesAsistenciaCamaraWorker
from workers.senadoresAsistenciaCamaraWork import SenadoresAsistenciaCamaraWorker

tipo_proyecto_re            = re.compile('([A-Za-z ]+).*')
lema_re                     = re.compile('.*Lema\s+([A-Z a-z]+).*')
origen_re                   = re.compile('(.*)\s*-\s*(.*)')
informante_re               = [re.compile('.*Informante:\s*([^,]+,\s*\w+\s+\w+\s+\w+)\s+.*'), re.compile('.*Informante:\s*([^,]+,\s*\w+\s+\w+)\s+.*'), re.compile('.*Informante:\s*([^,]+,\s*\w+)\s+.*')]
promulga_PE_re              = re.compile('.*Poder Ejecutivo promulga.*')

legislaturas = {
    'Legislatura XLVIII': {'from': '15-02-2015', 'to': '14-02-2020'},
    'Legislatura XLVII': {'from': '15-02-2010', 'to': '14-02-2015'},
    'Legislatura XLVI': {'from': '15-02-2005', 'to': '14-02-2010'},
    'Legislatura XLV': {'from': '15-02-2000', 'to': '14-02-2005'},
    'Legislatura XLIV': {'from': '15-02-1995', 'to': '14-02-2000'},
    'Legislatura XLIII': {'from': '15-02-1990', 'to': '14-02-1995'},
    'Legislatura XLII': {'from': '15-02-1985', 'to': '14-02-1990'}
}


def create_directory(legislatura):
    try:
        os.mkdir('../data/%s' % legislatura)
    except OSError:
        pass


def worker(idx, task_queue):
    while True:
        try:
            next_task = task_queue.get(timeout=10)
            next_task.tasks = task_queue
            next_task()
        except Empty :
            break
    print("Worker %s terminado." % idx)


if __name__ == '__main__':
    legislatura = 'Legislatura XLVIII'
    create_directory(legislatura)

    date_from = legislaturas[legislatura]['from']
    date_to = legislaturas[legislatura]['to']

    dbScraping = DBScraping()

    tasks = Queue()
    num_consumers = 6
    print('Creando %s consumidores' % num_consumers)
    consumers = [Thread(target=worker, args=(i, tasks,)) for i in range(num_consumers)]
    for w in consumers:
        w.start()

    tasks.put(SenadoresAsistenciaCamaraWorker(legislatura, date_from, date_to))
    tasks.put(RepresentantesAsistenciaCamaraWorker(legislatura, date_from, date_to))
    for w in consumers:
        w.join()

    dbScraping.export_to_csv(legislatura)