import datetime
from bs4 import BeautifulSoup

from db_scraping import DBScraping
from utils import get_html, find, find_all, extract_html_date, extract_html_int, find_class
from workers.workerScrap import WorkerScrap


class LegisladorAsistenciaPlenarioRepresentantesWork(WorkerScrap):

    def __init__(self, legislatura, date_from, date_to, id_legislador):
        super().__init__(legislatura, date_from, date_to)
        self.id_legislador = id_legislador
        DBScraping().create_table('asistencia_plenario', {'pk auto id': int, 'id_legislador ref legisladores.id_legislador': int, 'id_legislatura': int, 'camara': str, 'fecha': datetime, 'citaciones': int, 'asistencias': int, 'faltas_con_aviso': int, 'faltas_sin_aviso': int, 'licencia': int, 'pasaje_presidencia': int})

    def execute(self):
        print('\tImportando detalle de asistencia a plenario (%s) representantes.' % (self.id_legislador))
        file = get_html('https://parlamento.gub.uy/camarasycomisiones/legisladores/%s/asistenciaplenario/representantes?Fecha[min][date]=%s&Fecha[max][date]=%s' % (self.id_legislador, self.date_from, self.date_to))
        h = BeautifulSoup(file, 'lxml')
        asist_tabla = find(find_class(h, 'div', 'views-field-DetalleAsistencia'), 'tbody')
        if asist_tabla:
            for row_asist in find_all(asist_tabla, 'tr'):
                camara='CRR'
                fecha = extract_html_date(row_asist.contents[0])
                citaciones = extract_html_int(row_asist.contents[1])
                asistencias = extract_html_int(row_asist.contents[2])
                faltas_con_aviso = extract_html_int(row_asist.contents[3])
                faltas_sin_aviso = extract_html_int(row_asist.contents[4])
                licencia = extract_html_int(row_asist.contents[5])
                pasaje_presidencia = extract_html_int(row_asist.contents[6])
                DBScraping().insert('asistencia_plenario', {'id_legislador': self.id_legislador, 'id_legislatura': self.legislatura, 'camara': camara, 'fecha': fecha, 'citaciones': citaciones, 'asistencias': asistencias, 'faltas_con_aviso': faltas_con_aviso, 'faltas_sin_aviso': faltas_sin_aviso, 'licencia': licencia, 'pasaje_presidencia': pasaje_presidencia})
        else:
            print('\t\tTabla de asistencia a plenario no existe para %s' % self.id_legislador)
