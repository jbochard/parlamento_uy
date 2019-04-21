import hashlib
import threading

from pandas import DataFrame


def a(b):
    print(b)
    return b.get

class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


class DBScraping(Singleton):
    lock = threading.Lock()
    db_scraping = dict()

    def insert(self, table, key, reg):
        with self.lock:
            if table not in self.db_scraping:
                self.db_scraping[table] = dict()
            self.db_scraping[table][key] = reg
            return None

    def insert_autogen(self, table, reg):
        with self.lock:
            if table not in self.db_scraping:
                self.db_scraping[table] = dict()
            self.db_scraping[table][self.__build_id(reg)] = reg
            return None

    def __build_id(self, reg):
        text = ''.join([str(i[1]) for i in sorted(reg.items(), key=lambda x: x[0])])
        digester = hashlib.md5()
        digester.update(text.encode('utf-8'))
        return digester.hexdigest()

    def exists(self, table, key):
        with self.lock:
            return table in self.db_scraping and key in self.db_scraping[table]

    def find_by_id(self, table, key):
        with self.lock:
            if table in self.db_scraping and key in self.db_scraping[table]:
                return self.db_scraping[table][key]
            return None

    def update_by_id(self, table, key, reg):
        with self.lock:
            if table not in self.db_scraping:
                self.db_scraping[table] = dict()
            self.db_scraping[table][key] = reg
            return None

    def delete_by_id(self, table, key):
        with self.lock:
            if table in self.db_scraping and key in self.db_scraping[table]:
                del self.db_scraping[table][key]
            return None

    def __export_to_csv_table(self, legislatura, table):
        if table in self.db_scraping:
            df = DataFrame(self.db_scraping[table]).transpose()
            df.to_csv('../data/%s/%s.csv' % (legislatura, table), index=False)

    def export_to_csv(self, legislatura):
        for table in self.db_scraping.keys():
            print('Exportando %s a csv' % table)
            self.__export_to_csv_table(legislatura, table)
