import re

from bs4 import BeautifulSoup

from scripts.db_scraping import DBScraping
from scripts.utils import get_html, find, find_class, find_all, extract_html_str, extract_html_date
from scripts.workers.workerScrap import WorkerScrap


class ProyectoWorker(WorkerScrap):

    tipo_proyecto_re = re.compile('([A-Za-z ]+).*')
    origen_re = re.compile('(.*)\s*-\s*(.*)')
    promulga_PE_re = re.compile('.*Poder Ejecutivo promulga.*')

    def __init__(self, legislatura, date_from, date_to, id_proyecto):
        super().__init__(legislatura, date_from, date_to)
        self.id_proyecto = id_proyecto

    def execute(self):
        if DBScraping().exists('proyectos', self.id_proyecto):
            print('\tProyecto %s ya importado' % self.id_proyecto)
        else:
            print('\tImportando proyecto %s' % self.id_proyecto)

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

            proyecto['origen'] = find_class(h, 'div', 'views-field-Orgn-Nombre').contents[2].strip()
            if proyecto['origen']:
                match = self.origen_re.match(proyecto['origen'])
                if match:
                    proyecto['origen'] = match.group(1).strip()
                    proyecto['presentado_por'] = match.group(2).strip()
            proyecto['entrada_CSS'] = None
            proyecto['entrada_CRR'] = None
            proyecto['entrada_A.G.'] = None
            proyecto['sanciona_CSS'] = None
            proyecto['sanciona_CRR'] = None
            proyecto['sanciona_A.G.'] = None
            proyecto['sanciona_PE'] = None

            tabla_entradas = find_class(h, 'div', 'views-field-Entradas')
            if tabla_entradas:
                for row_html in find_all(find(tabla_entradas, 'tbody'), 'tr'):
                    fecha = extract_html_date(row_html.contents[0])
                    cuerpo = extract_html_str(row_html.contents[1])
                    if (cuerpo is None or len(cuerpo) == 0) and 'origen' in proyecto and proyecto['origen'] and proyecto[
                        'origen'] == 'Asamblea General':
                        cuerpo = 'A.G.'
                    elif (cuerpo is None or len(cuerpo) == 0) and 'origen' in proyecto and proyecto['origen'] and proyecto[
                        'origen'] == 'Cámara Representantes':
                        cuerpo = 'CRR'
                    elif (cuerpo is None or len(cuerpo) == 0) and 'origen' in proyecto and proyecto['origen'] and proyecto[
                        'origen'] == 'Cámara Senadores':
                        cuerpo = 'CSS'
                    proyecto['entrada_%s' % cuerpo] = fecha
                    if proyecto['titulo'] is None:
                        proyecto['titulo'] = extract_html_str(row_html.contents[3])

            tabla_sanciones = find_class(h, 'div', 'views-field-Sanciones')
            if tabla_sanciones:
                for row_html in find_all(find(tabla_sanciones, 'tbody'), 'tr'):
                    fecha = extract_html_date(row_html.contents[0])
                    cuerpo = extract_html_str(row_html.contents[1])
                    desc = extract_html_str(row_html.contents[3])
                    if (cuerpo is None or len(cuerpo) == 0) and self.promulga_PE_re.match(desc):
                        cuerpo = 'PE'
                    elif (cuerpo is None or len(cuerpo) == 0) and 'origen' in proyecto and proyecto['origen'] and proyecto['origen'] == 'Asamblea General':
                        cuerpo = 'A.G.'
                    elif (cuerpo is None or len(cuerpo) == 0) and 'origen' in proyecto and proyecto['origen'] and proyecto['origen'] == 'Cámara Representantes':
                        cuerpo = 'CRR'
                    elif (cuerpo is None or len(cuerpo) == 0) and 'origen' in proyecto and proyecto['origen'] and proyecto['origen'] == 'Cámara Senadores':
                        cuerpo = 'CSS'

                    proyecto['sanciona_%s' % cuerpo] = fecha

            tabla_comisiones = find_class(h, 'div', 'views-field-Cms')
            list_comisiones = []
            if tabla_comisiones:
                list_comisiones = find_all(find(tabla_comisiones, 'tbody'), 'tr')
            proyecto['num_comisiones'] = len(list_comisiones) if list_comisiones else 0

            tabla_sesiones = find_class(h, 'div', 'views-field-Sesiones')
            list_sesiones = []
            if tabla_sesiones:
                list_sesiones = find_all(find(tabla_sesiones, 'tbody'), 'tr')
            proyecto['num_sesiones'] = len(list_sesiones) if list_sesiones else 0
            DBScraping().insert('proyectos', self.id_proyecto, proyecto)
