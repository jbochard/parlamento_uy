from bs4 import BeautifulSoup

from scripts.db_scraping import DBScraping
from scripts.utils import get_html, find, extract_id, normalize_html_name
from scripts.workers.senadorWorker import SenadorWorker
from scripts.workers.workerScrap import WorkerScrap


class SenadoresAsistenciaCamaraWorker(WorkerScrap):

    def __init__(self, legislatura, date_from, date_to):
        super().__init__(legislatura, date_from, date_to)

    def execute(self):
        print('Importando senadores desde asistencias...')

        file = get_html('https://parlamento.gub.uy/camarasycomisiones/senadores/plenario/asistencia-a-sesiones?Fecha[min][date]=%s&Fecha[max][date]=%s' % (self.date_from, self.date_to))
        h = BeautifulSoup(file, 'lxml')
        for td_html in h.find_all('td', class_='views-field-Psn-NombresDeFirma'):
            link_html = find(td_html, 'a')
            if link_html:
                id = extract_id(link_html)
                nombre = normalize_html_name(link_html)
                DBScraping().insert('senadores', id, {'id_senador': id, 'nombre': nombre})
                self.tasks.put(SenadorWorker(self.legislatura, self.date_from, self.date_to, id))

