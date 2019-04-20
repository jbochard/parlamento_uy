from scripts.db_scraping import DBScraping
from scripts.exceptions import WebConnectionError


class WorkerScrap:
    tasks = None

    def __init__(self, legislatura, date_from, date_to):
        self.legislatura = legislatura
        self.date_from = date_from
        self.date_to = date_to

    def __call__(self, *args, **kwargs):
        try:
            self.execute()
        except WebConnectionError as e:
            self.tasks.put(self)

    def execute(self):
        pass