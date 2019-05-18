import os
import datetime
import hashlib
import threading
import re
from pandas import DataFrame
from sqlalchemy import create_engine

class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


class DBScraping(Singleton):
    lock = threading.Lock()
    db_meta = dict()
    db_scraping = dict()

    def create_table(self, table, reg):
        with self.lock:
            if table not in self.db_meta:
                self.db_meta[table] = dict()
                for (k, t) in reg.items():
                    reg = {'type': t, 'primary_key': False}
                    if re.match('\s*pk\s+', k):
                        k = re.sub('(\s*pk\s+)', '', k)
                        reg['primary_key'] = True
                    if re.match('\s*auto\s+', k):
                        k = re.sub('(\s*auto\s+)', '', k)
                        reg['auto_gen'] = 0
                    self.db_meta[table][k] = reg
                self.db_scraping[table] = dict()

    def insert(self, table, reg):
        with self.lock:
            if table in self.db_meta:
                reg = self.__gen_auto(self.db_meta[table], reg)
                key = self.__build_key(self.db_meta[table], reg)
                self.db_scraping[table][key] = reg
            return None

    def exists(self, table, reg):
        with self.lock:
            if table in self.db_meta and table in self.db_scraping:
                key = self.__build_key(self.db_meta[table], reg)
                return key in self.db_scraping[table]
            return False

    def find(self, table, reg):
        with self.lock:
            if table in self.db_meta and table in self.db_scraping:
                key = self.__build_key(self.db_meta[table], reg)
                if key in self.db_scraping[table]:
                    return self.db_scraping[table][key]
            return None

    def update(self, table, reg):
        with self.lock:
            if table in self.db_meta and table in self.db_scraping:
                key = self.__build_key(self.db_meta[table], reg)
                self.db_scraping[table][key] = reg
            return None

    def delete(self, table, reg):
        with self.lock:
            if table in self.db_meta and table in self.db_scraping:
                key = self.__build_key(self.db_meta[table], reg)
                if key in self.db_scraping[table]:
                    del self.db_scraping[table][key]
            return None

    def export_to_csv(self, legislatura):
        for table in self.db_scraping.keys():
            print('Exportando %s a csv' % table)
            self.__export_to_csv_table(legislatura, table)

    def db_export_to_sqlite(self):
        engine = create_engine('sqlite:///db.sqlite3')
        conn = engine.connect()
        self.__db_create_structure()
        for table in self.db_scraping.keys():
            print('Exportando %s a sql' % table)
            self.__db_export_to_sql_table(conn, table)
        conn.close()

    def __db_create_structure(self):
        engine = create_engine('sqlite:///db.sqlite3')
        conn = engine.connect()
        for table in self.db_meta.keys():
            self.__db_drop_table(conn, table)
            self.__db_create_table(conn, table)
        conn.close()

    def __gen_auto(self, meta, reg):
        for k, v in meta.items():
            if 'auto_gen' in v:
                reg[k] = v['auto_gen']
                v['auto_gen'] = v['auto_gen'] + 1
        return reg

    def __build_key(self, meta, reg):
        key = list()
        for k, v in meta.items():
            if v['primary_key']:
                key.append('%s_%s' % (k, str(reg[k])))
        return ':'.join(key)

    def __escape(self, meta, reg): 
        for k, v in meta.items():
            if v['type'] == str and k in reg and reg[k] is not None:
                reg[k] = reg[k].replace("'", "''")
        return reg

    def __build_id(self, reg):
        text = ''.join([str(i[1]) for i in sorted(reg.items(), key=lambda x: x[0])])
        digester = hashlib.md5()
        digester.update(text.encode('utf-8'))
        return digester.hexdigest()

    def __export_to_csv_table(self, legislatura, table):
        if table in self.db_scraping:
            df = DataFrame(self.db_scraping[table].values())
            df.to_csv('%s/../data/%s/%s.csv' % (os.path.dirname(os.path.abspath(__file__)), legislatura, table), index=False)

    def __db_export_to_sql_table(self, conn, table):
        if table in self.db_scraping:
            for reg in self.db_scraping[table].values():
                names, values = self.__map_values(table, reg)
                conn.execute('insert into %s(%s) values (%s);' % (table, ','.join(names), ','.join(values)))

    def __db_drop_table(self, conn, table):
        print("Elmininando tabla %s" % table)
        conn.execute('drop table if exists %s;' % table)

    def __db_create_table(self, conn, table):
        print("Creando tabla %s" % table)
        fields = list()
        for name, elem in self.db_meta[table].items():
            tp = self.__map_type(elem['type'])
            isPk = elem['primary_key']
            fields.append('%s %s %s' % (name, tp, 'PRIMARY KEY' if isPk else ''))
        conn.execute('create table if not exists %s(%s);' % (table, ','.join(fields)))

    def __map_type(self, tp):
        if tp == int:
            return 'integer'
        return 'text'

    def __map_values(self, table, reg):
        keys = list()
        vals = list()
        for k, v in reg.items():
            keys.append(k)
            if v is None:
                vals.append("null")
            elif self.db_meta[table][k]['type'] == str:
                vals.append("'%s'" % v.replace("'", "''"))
            elif self.db_meta[table][k]['type'] == datetime:
                vals.append("'%s'" % v)
            else:
                vals.append('%s' % str(v))
        return keys, vals

    