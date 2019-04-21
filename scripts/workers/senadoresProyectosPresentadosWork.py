from bs4 import BeautifulSoup

from scripts.db_scraping import DBScraping
from scripts.utils import get_html, find, extract_id, find_all, extract_html_date, find_class
from scripts.workers.senadoresProyectoWork import SenadoresProyectoWorker
from scripts.workers.workerScrap import WorkerScrap


class SenadoresProyectosPresentadosWorker(WorkerScrap):

    def __init__(self, legislatura, date_from, date_to, id_legislador):
        super().__init__(legislatura, date_from, date_to)
        self.id_legislador = id_legislador
        self.date_from = date_from
        self.date_to = date_to

    def execute(self):
        print('\tImportando proyectos presentados por %s' % self.id_legislador)

        file = get_html('https://parlamento.gub.uy/camarasycomisiones/legisladores/%s/iniciativas-legislador?Fecha[min][date]=%s&Fecha[max][date]=%s' % (self.id_legislador, self.date_from, self.date_to))
        h = BeautifulSoup(file, 'lxml')
        tabla = find(h, 'tbody')
        for html_row in find_all(tabla, 'tr'):
            id_proyecto = extract_id(find(html_row, 'a'))
            fecha = extract_html_date(find_class(html_row, 'td', 'views-field-Ast-FechaDeEntradaAlCuerpo'))
            DBScraping().insert_autogen('proyectos_presentados', {'id_proyecto': id_proyecto, 'id_legislador': self.id_legislador, 'fecha': fecha})
            if not DBScraping().exists('proyectos', id_proyecto):
                self.tasks.put(SenadoresProyectoWorker(self.legislatura, self.date_from, self.date_to, id_proyecto))


