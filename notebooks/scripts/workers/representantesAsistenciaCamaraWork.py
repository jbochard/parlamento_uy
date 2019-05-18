from bs4 import BeautifulSoup

from db_scraping import DBScraping
from utils import get_html, find, extract_id, normalize_html_name
from workers.legisladorWorker import LegisladorWorker
from workers.workerScrap import WorkerScrap


class RepresentantesAsistenciaCamaraWorker(WorkerScrap):

    def __init__(self, legislatura, date_from, date_to):
        super().__init__(legislatura, date_from, date_to)
        DBScraping().create_table('legisladores', {'pk id_legislador': int, 'nombre': str, 'cuerpo': str, 'email': str, 'lema': str})

    def execute(self):
        print('Importando representantes desde asistencias...')

        file = get_html('https://parlamento.gub.uy/camarasycomisiones/representantes/plenario/asistencia-a-sesiones?Fecha[min][date]=%s&Fecha[max][date]=%s' % (self.date_from, self.date_to))
        h = BeautifulSoup(file, 'lxml')
        for td_html in h.find_all('td', class_='views-field-Psn-NombresDeFirma'):
            link_html = find(td_html, 'a')
            if link_html:
                id = extract_id(link_html)
                nombre = normalize_html_name(link_html)
                if not DBScraping().exists('legisladores', {'id_legislador': id}):
                    DBScraping().insert('legisladores', {'id_legislador': id, 'nombre': nombre})
                    self.tasks.put(LegisladorWorker(self.legislatura, self.date_from, self.date_to, id))

