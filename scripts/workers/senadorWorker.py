import re

from scripts.db_scraping import DBScraping
from scripts.utils import find_class, extract_html_str
from bs4 import BeautifulSoup
from scripts.utils import get_html
from scripts.workers.senadoresActuacionParlamentariaWork import SenadoresActuacionParlamentariaWorker
from scripts.workers.senadoresAsistenciaPlenarioWork import SenadoresAsistenciaPlenarioWorker
from scripts.workers.senadoresComisionesWork import SenadoresComisionesWorker
from scripts.workers.senadoresPedidosInformeWork import SenadoresPedidosInformeWorker
from scripts.workers.senadoresProyectosPresentadosWork import SenadoresProyectosPresentadosWorker
from scripts.workers.workerScrap import WorkerScrap

lema_re = re.compile('.*Lema\s+([A-Z a-z]+).*')


class SenadorWorker(WorkerScrap):

    def __init__(self, legislatura, date_from, date_to, id_senador):
        super().__init__(legislatura, date_from, date_to)
        self.id_senador = id_senador

    def execute(self):
        print('\tImportando perfil de %s' % self.id_senador)

        senador = DBScraping().find_by_id('senadores', self.id_senador)

        file = get_html('https://parlamento.gub.uy/camarasycomisiones/legisladores/%s' % self.id_senador)
        h = BeautifulSoup(file, 'lxml')

        # Valida que actúe en la legislatura seleccionada
        actuo_en_legislatura = False
        leg_list_html = find_class(h, 'div', 'view-legislaturas-actuo')
        if leg_list_html is not None:
            for leg_html in leg_list_html.find_all('span', class_='field-content'):
                if self.legislatura in extract_html_str(leg_html):
                    actuo_en_legislatura = True
        if not actuo_en_legislatura:
            print('Senador %s(%s) no actuó en la legislatura seleccionada.' % (senador['nombre'], senador['id_senador']))
            DBScraping().delete_by_id('senadores', self.id_senador)
            return

        # Lee email
        email = ''
        if find_class(h, 'div', 'field-name-field-persona-mail'):
            email = extract_html_str(find_class(h, 'div', 'field-name-field-persona-mail').find('a'))
        senador['email'] = email

        # Lee el lema del senador
        if find_class(h, 'div', 'field-name-field-persona-desc'):
            desc = extract_html_str(
                find_class(find_class(h, 'div', 'field-name-field-persona-desc'), 'div', 'field-item'))
            if desc and len(desc.strip()) > 0:
                if lema_re.match(desc):
                    senador['lema'] = lema_re.match(desc).group(1).strip()

        DBScraping().update_by_id('senadores', self.id_senador, senador)

        self.tasks.put(SenadoresAsistenciaPlenarioWorker(self.legislatura, self.date_from, self.date_to, self.id_senador))
        self.tasks.put(SenadoresProyectosPresentadosWorker(self.legislatura, self.date_from, self.date_to, self.id_senador))
        self.tasks.put(SenadoresPedidosInformeWorker(self.legislatura, self.date_from, self.date_to, self.id_senador))
        self.tasks.put(SenadoresComisionesWorker(self.legislatura, self.date_from, self.date_to, self.id_senador))
        self.tasks.put(SenadoresActuacionParlamentariaWorker(self.legislatura, self.date_from, self.date_to, self.id_senador, 0))

