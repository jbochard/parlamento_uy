import re
import datetime
from bs4 import BeautifulSoup

from db_scraping import DBScraping
from utils import get_html, find, find_all, extract_html_date, find_class, \
    extract_html_str, parse_list, try_parsing_date
from workers.workerScrap import WorkerScrap


class LegisladorActuacionParlamentariaWork(WorkerScrap):

    informa_re = re.compile('Informante.*')
    interviene_re = re.compile('Interviene.*')
    expone_re = re.compile('.*((Presenta la exposicion)|(Presenta la exposición)|(Presenta la nota)).*')
    pedido_informe_re = re.compile('Solicita pedido de informes.*')

    def __init__(self, legislatura, date_from, date_to, id_legislador, pagina):
        super().__init__(legislatura, date_from, date_to)
        self.id_legislador = id_legislador
        self.pagina = pagina
        DBScraping().create_table('actuacion_parlamentaria', {'pk auto id': int, 'id_legislador ref legisladores.id_legislador': int, 'id_legislatura': int, 'tipo': str, 'fecha': datetime, 'detalle': str})
        DBScraping().create_table('convocatoria', {'pk auto id': int, 'id_legislador ref legisladores.id_legislador': int, 'id_legislatura': int, 'fecha_ini': datetime, 'camara': str, 'lema': str, 'departamento': str, 'sublema': str, 'fecha_fin': datetime, 'titular': str})
 
    def execute(self):
        print('\tImportando detalle actuacion parlamentaria (%s), página: %s' % (self.id_legislador, self.pagina))
        file = get_html('https://parlamento.gub.uy/camarasycomisiones/legisladores/%s/actuacion-legislador?Fecha[min][date]=%s&Fecha[max][date]=%s&Tipo=All&page=0,0,%s' % (self.id_legislador, self.date_from, self.date_to, self.pagina))
        h = BeautifulSoup(file, 'lxml')
        tabla = find(find_class(h, 'table', 'views-table'), 'tbody')
        if tabla:
            for row_asist in find_all(tabla, 'tr'):
                fecha = extract_html_date(row_asist.contents[1])
                detalle = extract_html_str(row_asist.contents[3])
                tipo = self.build_type(detalle)
                if tipo == 'CONVOCATORIA':
                    convocatoria = self.parse_convocatoria(self.legislatura, self.id_legislador, fecha, detalle)
                    DBScraping().insert('convocatoria', convocatoria)
                elif tipo is not None:
                    DBScraping().insert('actuacion_parlamentaria', {'id_legislador': self.id_legislador, 'id_legislatura': self.legislatura, 'tipo': tipo, 'fecha': fecha, 'detalle': detalle})

            self.tasks.put(LegisladorActuacionParlamentariaWork(self.legislatura, self.date_from, self.date_to, self.id_legislador, (self.pagina + 1)))
        else:
            print('\t\tTabla de actuación parlamentaria (página %s) no existe para %s' % (self.pagina, self.id_legislador))

    def build_type(self, detalle):
        if self.informa_re.match(detalle):
            return 'INFORMA'
        if self.interviene_re.match(detalle):
            return 'INTERVIENE'
        if self.expone_re.match(detalle):
            return 'EXPONE'
        if self.es_convocatoria(detalle):
            return 'CONVOCATORIA'
        return None

    def es_convocatoria(self, detalle):
        return parse_list(detalle, 'Convocad.\s+a\s+la\s+(\w+\s+\w+\s+\w+)\s+por\s+el.*') is not None

    def parse_convocatoria(self, id_legislatura, id_legislador, fecha_ini, detalle):
        response = {
            'id_legislador': id_legislador,
            'id_legislatura': id_legislatura,
            'fecha_ini': fecha_ini
        }
        camara = parse_list(detalle, 'Convocad.\s+a\s+la\s+(\w+\s+\w+\s+\w+)\s+por\s+el.*')
        if camara:
            response['camara'] = camara
            response['lema'] = parse_list(detalle, '.*\s+lema\s*([^,]*),.*')
            response['departamento'] = parse_list(detalle, '.*por\s+el\s+departamento\s+de\s+(.*)\s+por\s+el.*')
            response['sublema'] = parse_list(detalle, '.*sublema\s+(.*)\s+hasta\s+el.*')
            response['fecha_fin'] = try_parsing_date(parse_list(detalle, '.*hasta\s+el\s+(\d\d/\d\d/\d\d\d\d\s+\d\d:\d\d).*'))
            response['titular'] = parse_list(detalle, '.*Titular:\s+(.*)\s+tomo.*')
            return response
        return None


