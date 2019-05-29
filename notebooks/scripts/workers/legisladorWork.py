import re

from db_scraping import DBScraping
from utils import find_class, extract_html_str
from bs4 import BeautifulSoup
from utils import get_html
from workers.legisladorActuacionParlamentariaWork import LegisladorActuacionParlamentariaWork
from workers.legisladorAsistenciaPlenarioSenadoWork import LegisladorAsistenciaPlenarioSenadoWork
from workers.legisladorAsistenciaPlenarioRepresentantesWork import LegisladorAsistenciaPlenarioRepresentantesWork
from workers.legisladorComisionesWork import LegisladorComisionesWork
from workers.legisladorPedidosInformeWork import LegisladorPedidosInformeWork
from workers.legisladorProyectosPresentadosWork import LegisladorProyectosPresentadosWork
from workers.workerScrap import WorkerScrap

lema_re = re.compile('.*Lema\s+([A-Z a-z]+).*')
representante_re = re.compile('.*Representante\s+([A-Z a-z]+).*')
senador_re = re.compile('.*Senador\s+([A-Z a-z]+).*')

class LegisladorWork(WorkerScrap):

    def __init__(self, legislatura, date_from, date_to, id_legislador):
        super().__init__(legislatura, date_from, date_to)
        self.id_legislador = id_legislador

    def execute(self):
        print('\tImportando perfil de %s' % self.id_legislador)

        legislador = DBScraping().find('legisladores', {'id_legislador': self.id_legislador})

        file = get_html('https://parlamento.gub.uy/camarasycomisiones/legisladores/%s' % self.id_legislador)
        h = BeautifulSoup(file, 'lxml')
        
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

        DBScraping().update('legisladores', legislador)

        self.tasks.put(LegisladorAsistenciaPlenarioSenadoWork(self.legislatura, self.date_from, self.date_to, self.id_legislador))
        self.tasks.put(LegisladorAsistenciaPlenarioRepresentantesWork(self.legislatura, self.date_from, self.date_to, self.id_legislador))
        self.tasks.put(LegisladorProyectosPresentadosWork(self.legislatura, self.date_from, self.date_to, self.id_legislador))
        self.tasks.put(LegisladorPedidosInformeWork(self.legislatura, self.date_from, self.date_to, self.id_legislador))
        self.tasks.put(LegisladorComisionesWork(self.legislatura, self.date_from, self.date_to, self.id_legislador))
        self.tasks.put(LegisladorActuacionParlamentariaWork(self.legislatura, self.date_from, self.date_to, self.id_legislador, 0))

