from bs4 import BeautifulSoup

from scripts.db_scraping import DBScraping
from scripts.utils import get_html, find, extract_id, find_all, extract_html_date, find_class
from scripts.workers.senadoresProyectoWork import SenadoresProyectoWorker
from scripts.workers.workerScrap import WorkerScrap


class SenadoresProyectosPresentadosWorker(WorkerScrap):

    def __init__(self, legislatura, date_from, date_to, id_senador):
        super().__init__(legislatura, date_from, date_to)
        self.id_senador = id_senador
        self.date_from = date_from
        self.date_to = date_to

    def execute(self):
        print('\tImportando proyectos presentados por %s' % self.id_senador)

        file = get_html('https://parlamento.gub.uy/camarasycomisiones/legisladores/%s/iniciativas-legislador?Fecha[min][date]=%s&Fecha[max][date]=%s' % (self.id_senador, self.date_from, self.date_to))
        h = BeautifulSoup(file, 'lxml')
        tabla = find(h, 'tbody')
        for html_row in find_all(tabla, 'tr'):
            id_proyecto = extract_id(find(html_row, 'a'))
            fecha = extract_html_date(find_class(html_row, 'td', 'views-field-Ast-FechaDeEntradaAlCuerpo'))
            DBScraping().insert('proyectos_presentados', id_proyecto, {'id_proyecto': id_proyecto, 'id_senador': self.id_senador, 'fecha': fecha})
            if not DBScraping().exists('proyectos', id_proyecto):
                self.tasks.put(SenadoresProyectoWorker(self.legislatura, self.date_from, self.date_to, id_proyecto))


