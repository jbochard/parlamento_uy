from bs4 import BeautifulSoup

from db_scraping import DBScraping
from utils import get_html, find, extract_id, find_class, find_all, extract_html_str
from workers.workerScrap import WorkerScrap
from workers.asistenciaPlenarioSenadoWork import AsistenciaPlenarioSenadoWork
from workers.asistenciaPlenarioRepresentantesWork import AsistenciaPlenarioRepresentantesWork


class LegislaturaWork(WorkerScrap):

    def __init__(self, legislatura, date_from, date_to, nombre, base_dir):
        super().__init__(legislatura, date_from, date_to)
        self.base_dir = base_dir
        self.nombre = nombre

    def execute(self):
        print('Importando legislatura desde %s a %s' % (self.date_from, self.date_to))

        self.tasks.put(AsistenciaPlenarioSenadoWork(self.legislatura, self.date_from, self.date_to))
        self.tasks.put(AsistenciaPlenarioRepresentantesWork(self.legislatura, self.date_from, self.date_to))