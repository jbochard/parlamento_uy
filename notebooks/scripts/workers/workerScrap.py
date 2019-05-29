from db_scraping import DBScraping
from exceptions import WebConnectionError


class WorkerScrap:
    tasks = None

    def __init__(self, legislatura, date_from, date_to):
        self.legislatura = legislatura
        self.date_from = date_from
        self.date_to = date_to
        self.debug = False
        self.__log('Create instance')

    def __call__(self, *args, **kwargs):
        try:
            self.execute()
        except WebConnectionError as e:
            self.tasks.put(self)

    def execute(self):
        pass

    def __log(self, msg):
        if self.debug:
            print('%s - %s' % (self, msg))