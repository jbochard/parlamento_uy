import datetime
from bs4 import BeautifulSoup

from db_scraping import DBScraping
from utils import get_html, find, extract_id, find_all, extract_html_date, find_class, extract_html_str
from workers.proyectoWork import ProyectoWork
from workers.workerScrap import WorkerScrap


class LegisladorPedidosInformeWork(WorkerScrap):

    def __init__(self, legislatura, date_from, date_to, id_legislador):
        super().__init__(legislatura, date_from, date_to)
        self.id_legislador = id_legislador
        self.date_from = date_from
        self.date_to = date_to
        DBScraping().create_table('proyectos_presentados', {'pk auto id': int, 'id_proyecto': int, 'id_legislador ref legisladores.id_legislador': int, 'id_legislatura': int, 'fecha': datetime, 'organismo': str})

    def execute(self):
        print('\tImportando pedidos de informe de %s' % self.id_legislador)

        file = get_html('https://parlamento.gub.uy/camarasycomisiones/legisladores/%s/pedidosInf-legislador?Fecha[min][date]=%s&Fecha[max][date]=%s' % (self.id_legislador, self.date_from, self.date_to))
        h = BeautifulSoup(file, 'lxml')
        for html_row in find_all(find(h, 'tbody'), 'tr'):
            id_legislador = self.id_legislador
            id_proyecto = extract_id(find(html_row, 'a'))
            fecha = extract_html_date(find_class(html_row, 'td', 'views-field-Ast-FechaDeEntradaAlCuerpo'))
            organismos_html = html_row.find_all('li')
            for organismo_html in organismos_html:
                organismo = extract_html_str(organismo_html)
                DBScraping().insert('proyectos_presentados', {'id_proyecto': id_proyecto, 'id_legislador': id_legislador, 'id_legislatura': self.legislatura, 'fecha': fecha, 'organismo': organismo})
                
                if not DBScraping().exists('proyectos', {'id_proyecto': id_proyecto}):
                    self.tasks.put(ProyectoWork(self.legislatura, self.date_from, self.date_to, id_proyecto))
