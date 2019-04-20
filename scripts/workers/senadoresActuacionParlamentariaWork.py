import hashlib
import re

from bs4 import BeautifulSoup

from scripts.db_scraping import DBScraping
from scripts.utils import get_html, find, find_all, extract_html_date, find_class, \
    extract_html_str
from scripts.workers.workerScrap import WorkerScrap


class SenadoresActuacionParlamentariaWorker(WorkerScrap):

    informa_re = re.compile('Informante.*')
    interviene_re = re.compile('Interviene.*')
    expone_re = re.compile('.*((Presenta la exposicion)|(Presenta la exposición)|(Presenta la nota)).*')
    pedido_informe_re = re.compile('Solicita pedido de informes.*')

    def __init__(self, legislatura, date_from, date_to, id_senador, pagina):
        super().__init__(legislatura, date_from, date_to)
        self.id_senador = id_senador
        self.pagina = pagina

    def execute(self):
        print('\tImportando detalle actuacion parlamentaria (%s), página: %s' % (self.id_senador, self.pagina))
        file = get_html('https://parlamento.gub.uy/camarasycomisiones/legisladores/%s/actuacion-legislador?Fecha[min][date]=%s&Fecha[max][date]=%s&Tipo=All&page=0,0,%s' % (self.id_senador, self.date_from, self.date_to, self.pagina))
        h = BeautifulSoup(file, 'lxml')
        tabla = find(find_class(h, 'table', 'views-table'), 'tbody')
        if tabla:
            for row_asist in find_all(tabla, 'tr'):
                fecha = extract_html_date(row_asist.contents[1])
                detalle = extract_html_str(row_asist.contents[3])
                tipo = self.build_type(detalle)
                DBScraping().insert('actuacion_parlamentaria', '%s_%s_%s' % (self.id_senador, fecha, self.build_id(detalle)), {'id_senador': self.id_senador, 'tipo': tipo, 'fecha': fecha, 'detalle': detalle})
            self.tasks.put(SenadoresActuacionParlamentariaWorker(self.legislatura, self.date_from, self.date_to, self.id_senador, (self.pagina + 1)))
        else:
            print('\t\tTabla de actuación parlamentaria (página %s) no existe para %s' % (self.pagina, self.id_senador))

    def build_id(self, detalle):
        digester = hashlib.md5()
        digester.update(detalle.encode('utf-8'))
        return digester.hexdigest()

    def build_type(self, detalle):
        if self.informa_re.match(detalle):
            return 'INFORMA'
        if self.interviene_re.match(detalle):
            return 'INTERVIENE'
        if self.expone_re.match(detalle):
            return 'EXPONE'
        if self.pedido_informe_re.match(detalle):
            return 'PEDIDO_DE_INFORME'
        return ''