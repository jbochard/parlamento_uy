from bs4 import BeautifulSoup

from scripts.db_scraping import DBScraping
from scripts.utils import get_html, find_all, extract_html_date, extract_html_int, find_class
from scripts.workers.workerScrap import WorkerScrap


class LegisladorAsistenciaComisionesWorker(WorkerScrap):

    def __init__(self, legislatura, date_from, date_to, id_legislador, id_comision):
        super().__init__(legislatura, date_from, date_to)
        self.id_legislador = id_legislador
        self.id_comision = id_comision

    def execute(self):
        print('\tImportando detalle de asistencia a comisiones (%s, %s)' % (self.id_legislador, self.id_comision))
        file = get_html('https://parlamento.gub.uy/camarasycomisiones/legisladores/%s/asistencia-a-comisiones/%s?Fecha[min][date]=%s&Fecha[max][date]=%s' % (self.id_legislador, self.id_comision, self.date_from, self.date_to))
        h = BeautifulSoup(file, 'lxml')
        asist_tablas = find_all(find_class(h, 'div', 'views-field views-field-Comsiones'), 'tbody')
        if len(asist_tablas) > 1:
            for row_asist in find_all(asist_tablas[1], 'tr'):
                fecha = extract_html_date(row_asist.contents[0])
                citaciones = extract_html_int(row_asist.contents[1])
                asistencias = extract_html_int(row_asist.contents[2])
                faltas_con_aviso = extract_html_int(row_asist.contents[3])
                faltas_sin_aviso = extract_html_int(row_asist.contents[4])
                licencia = extract_html_int(row_asist.contents[5])
                otras_comisiones = extract_html_int(row_asist.contents[6])
                DBScraping().insert('asistencia_comisiones', '%s_%s_%s' % (self.id_comision, self.id_legislador, fecha), {'id_comision': self.id_comision, 'id_legislador': self.id_legislador, 'fecha': fecha, 'citaciones': citaciones, 'asistencias': asistencias, 'faltas_con_aviso': faltas_con_aviso, 'faltas_sin_aviso': faltas_sin_aviso, 'licencia': licencia, 'otras_comisiones': otras_comisiones})
        else:
            print('\t\tTabla de asistencia a comisiones no existe para comision %s, %s' % (self.id_comision, self.id_legislador))
