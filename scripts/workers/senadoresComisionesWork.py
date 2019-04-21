from bs4 import BeautifulSoup

from scripts.db_scraping import DBScraping
from scripts.utils import get_html, find, extract_id, find_class, find_all, extract_html_str
from scripts.workers.senadoresAsistenciaComisionesWork import SenadoresAsistenciaComisionesWorker
from scripts.workers.workerScrap import WorkerScrap


class SenadoresComisionesWorker(WorkerScrap):

    def __init__(self, legislatura, date_from, date_to, id_legislador):
        super().__init__(legislatura, date_from, date_to)
        self.id_legislador = id_legislador

    def execute(self):
        print('\tImportando comisiones desde %s' % self.id_legislador)
        file = get_html('https://parlamento.gub.uy/camarasycomisiones/legisladores/%s/asistencia-a-comisiones?Fecha[min][date]=%s&Fecha[max][date]=%s' % (
            self.id_legislador, self.date_from, self.date_to))
        h = BeautifulSoup(file, 'lxml')
        for row_html in find_all(find(find_class(h, 'div', 'attachment'), 'tbody'), 'tr'):
            link = find(row_html, 'a')
            id_comision = extract_id(link)
            nombre_comision = extract_html_str(row_html.contents[0])
            DBScraping().insert('comisiones', id_comision, {'id_comision': id_comision, 'nombre': nombre_comision})
            self.tasks.put(SenadoresAsistenciaComisionesWorker(self.legislatura, self.date_from, self.date_to, self.id_legislador, id_comision))

