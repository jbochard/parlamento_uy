import datetime
import re

from bs4 import BeautifulSoup

from db_scraping import DBScraping
from utils import get_html, find, find_class, find_all, extract_html_str, extract_html_date, extract_id, find_link_in
from workers.workerScrap import WorkerScrap


class ProyectoWorker(WorkerScrap):

    tipo_proyecto_re = re.compile('([A-Za-z ]+).*')
    origen_re = re.compile('(.*)\s*-\s*(.*)')

    def __init__(self, legislatura, date_from, date_to, id_proyecto):
        super().__init__(legislatura, date_from, date_to)
        self.id_proyecto = id_proyecto
        DBScraping().create_table('proyectos', {'pk id_proyecto': int, 'origen': str, 'tipo': str, 'titulo': str, 'presentado_por': str, 'evolucion': str})
        DBScraping().create_table('evolucion_proyectos', {'pk auto id': int, 'id_proyecto': int, 'tipo': str, 'fecha': datetime, 'cuerpo': str, 'detalle': str, 'id_comision': int})

    def execute(self):
        if DBScraping().exists('proyectos', {'id_proyecto': self.id_proyecto}):
            print('\tProyecto %s ya importado' % self.id_proyecto)
        else:
            print('\tImportando proyecto %s' % self.id_proyecto)
            DBScraping().insert('proyectos', {'id_proyecto': self.id_proyecto})

            file = get_html(
                'https://parlamento.gub.uy/documentosyleyes/ficha-asunto/%s/ficha_completa' % self.id_proyecto)
            h = BeautifulSoup(file, 'lxml')
            proyecto = {}
            proyecto['id_proyecto'] = self.id_proyecto
            proyecto['titulo'] = extract_html_str(find(find_class(h, 'div', 'views-field-Ast-Titulo'), 'span'))
            proyecto['tipo'] = extract_html_str(find_class(h, 'div', 'tipo-acto'))
            if proyecto['tipo']:
                tipo = self.tipo_proyecto_re.match(proyecto['tipo'])
                if tipo:
                    proyecto['tipo'] = tipo.group(1).strip()

            origen = find_class(h, 'div', 'views-field-Orgn-Nombre').contents[2].strip()
            match = self.origen_re.match(origen)
            if match:
                origen = match.group(1).strip()
                proyecto['presentado_por'] = match.group(2).strip()
            
            if origen == 'Asamblea General':
                origen = 'AG'
            elif origen == 'Cámara Representantes':
                origen = 'CRR'
            elif origen == 'Cámara Senadores':
                origen = 'CSS'
            elif origen == 'Poder Ejecutivo':
                origen = 'PE'
            proyecto['origen'] = origen

            evolucion = ''
            for row_html in find_all(find(find_class(find_class(h, 'div', 'views-field-Tmt'), 'table', 'tablaAsunto'), 'tbody'), 'tr'):
                fecha = extract_html_date(row_html.contents[0])
                cuerpo = extract_html_str(row_html.contents[1])
                desc = extract_html_str(row_html.contents[3])
                tipo = self.build_type(tipo, desc)
                id_comision = extract_id(find_link_in(row_html.contents[3], 'comisiones'))
                if tipo is not None:
                    evolucion = '%s:%s' % (evolucion, tipo)
                DBScraping().insert('evolucion_proyectos', {'id_proyecto': self.id_proyecto, 'tipo': tipo, 'fecha': fecha, 'cuerpo': cuerpo, 'detalle': desc, 'id_comision': id_comision})

            proyecto['evolucion'] = evolucion
            DBScraping().insert('proyectos', proyecto)

    def build_type(self, tipo, desc):
        matcher = {
            re.compile('.*Se da curso.*'): 'PEDIDO_INFORME_ENVIO',
            re.compile('.*Respuesta.*'): 'PEDIDO_INFORME_RESPUESTA',
            re.compile('.*Ampliación de plazo según Ley 17673.*'): 'PEDIDO_INFORME_AMPLIACION_17673',

            re.compile('.*pasa a comisión.*'): 'PASE_COMISION',

            re.compile('.*(Se da cuenta en comisión|envía a la Comisión).*'): 'COMISION_ENTRADA',
            re.compile('.*Tratamiento en comisión.*'): 'COMISION_TRATAMIENTO',
            re.compile('.*Comisión posterga su tratamiento.*'): 'COMISION_POSTERGA',
            re.compile('.*Comisión aprueba.*'): 'COMISION_APRUEBA',
            re.compile('.*Comisión vota negativamente.*'): 'COMISION_RECHAZA',
            re.compile('.*Se da cuenta en sala informe.*'): 'COMISION_INFORMA',

            re.compile('.*Recepción por parte de Archivo.*'): 'PASE_ARCHIVO',

            re.compile('.*Entrada a Cámara.*'): 'CAMARA_ENTRADA',
            re.compile('.*(C\.RR\.|C\.SS\.) rechaza.*'): 'CAMARA_RECHAZA',
            re.compile('.*(C\.RR\.|C\.SS\.) modifica.*'): 'CAMARA_MODIFICA',
            re.compile('.*Moción de urgencia.*'): 'CAMARA_URGENCIA',
            re.compile('.*(C\.RR\.|C\.SS\.) sanciona.*'): 'CAMARA_APRUEBA',
            re.compile('.*Se aprueba Resolución.*'): 'CAMARA_APRUEBA',
            re.compile('.*(Discusión general|Discusión particular).*'): 'CAMARA_DISCUCION',

            re.compile('.*Poder Ejecutivo promulga.*'): 'PROMULGA_PE'
        }
        for k, v in matcher.items():
            if k.match(desc):
                return v
        return None