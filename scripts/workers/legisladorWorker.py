import re

from scripts.db_scraping import DBScraping
from scripts.utils import find_class, extract_html_str
from bs4 import BeautifulSoup
from scripts.utils import get_html
from scripts.workers.legisladorActuacionParlamentariaWork import LegisladorActuacionParlamentariaWorker
from scripts.workers.representantesAsistenciaPlenarioWork import RepresentantesAsistenciaPlenarioWorker
from scripts.workers.senadoresAsistenciaPlenarioWork import SenadoresAsistenciaPlenarioWorker
from scripts.workers.legisladorComisionesWork import LegisladorComisionesWorker
from scripts.workers.legisladorPedidosInformeWork import LegisladorPedidosInformeWorker
from scripts.workers.legisladorProyectosPresentadosWork import LegisladorProyectosPresentadosWorker
from scripts.workers.workerScrap import WorkerScrap

lema_re = re.compile('.*Lema\s+([A-Z a-z]+).*')
representante_re = re.compile('.*Representante\s+([A-Z a-z]+).*')
senador_re = re.compile('.*Senador\s+([A-Z a-z]+).*')

class LegisladorWorker(WorkerScrap):

    def __init__(self, legislatura, date_from, date_to, id_legislador):
        super().__init__(legislatura, date_from, date_to)
        self.id_legislador = id_legislador

    def execute(self):
        print('\tImportando perfil de %s' % self.id_legislador)

        legislador = DBScraping().find_by_id('legisladores', self.id_legislador)

        file = get_html('https://parlamento.gub.uy/camarasycomisiones/legisladores/%s' % self.id_legislador)
        h = BeautifulSoup(file, 'lxml')

        # Valida que actúe en la legislatura seleccionada
        actuo_en_legislatura = False
        leg_list_html = find_class(h, 'div', 'view-legislaturas-actuo')
        if leg_list_html is not None:
            for leg_html in leg_list_html.find_all('span', class_='field-content'):
                if self.legislatura in extract_html_str(leg_html):
                    actuo_en_legislatura = True
        if not actuo_en_legislatura:
            print('Legislador %s(%s) no actuó en la legislatura seleccionada.' % (legislador['nombre'], legislador['id_legislador']))
            DBScraping().delete_by_id('legisladores', self.id_legislador)
            return

        # Lee email
        email = ''
        if find_class(h, 'div', 'field-name-field-persona-mail'):
            email = extract_html_str(find_class(h, 'div', 'field-name-field-persona-mail').find('a'))
        legislador['email'] = email

        # Lee el lema del senador
        if find_class(h, 'div', 'field-name-field-persona-desc'):
            desc = extract_html_str(
                find_class(find_class(h, 'div', 'field-name-field-persona-desc'), 'div', 'field-item'))
            if desc and len(desc.strip()) > 0:
                if lema_re.match(desc):
                    legislador['lema'] = lema_re.match(desc).group(1).strip()
                if senador_re.match(desc):
                    legislador['cuerpo'] = 'SENADO'
                if representante_re.match(desc):
                    legislador['cuerpo'] = 'REPRESENTANTE'

        DBScraping().update_by_id('legisladores', self.id_legislador, legislador)

        self.tasks.put(SenadoresAsistenciaPlenarioWorker(self.legislatura, self.date_from, self.date_to, self.id_legislador))
        self.tasks.put(RepresentantesAsistenciaPlenarioWorker(self.legislatura, self.date_from, self.date_to, self.id_legislador))
        self.tasks.put(LegisladorProyectosPresentadosWorker(self.legislatura, self.date_from, self.date_to, self.id_legislador))
        self.tasks.put(LegisladorPedidosInformeWorker(self.legislatura, self.date_from, self.date_to, self.id_legislador))
        self.tasks.put(LegisladorComisionesWorker(self.legislatura, self.date_from, self.date_to, self.id_legislador))
        self.tasks.put(LegisladorActuacionParlamentariaWorker(self.legislatura, self.date_from, self.date_to, self.id_legislador, 0))

