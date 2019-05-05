from bs4 import BeautifulSoup

from db_scraping import DBScraping
from utils import get_html, find, extract_id, normalize_html_name
from workers.legisladorWorker import LegisladorWorker
from workers.workerScrap import WorkerScrap


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
                if not DBScraping().exists('legisladores', id):
                    DBScraping().insert('legisladores', id, {'id_legislador': id, 'nombre': nombre})
                    self.tasks.put(LegisladorWorker(self.legislatura, self.date_from, self.date_to, id))

