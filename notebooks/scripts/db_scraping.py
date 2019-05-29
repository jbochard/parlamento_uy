import os
import datetime
import hashlib
import threading
import re
from pandas import DataFrame
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

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
    db_index_data = dict()
    db_index_meta = dict()
    debug = False

    def create_table(self, table, reg):
        with self.lock:
            if table not in self.db_meta:
                self.db_meta[table] = dict()
                self.db_meta[table] = self.__build_meta(reg)
                self.db_scraping[table] = dict()

    def create_index(self, table, name, key):
        with self.lock:
            if table not in self.db_index_meta:
                self.db_index_meta[table] = dict()
            if name not in self.db_index_meta[table]:
                self.db_index_meta[table][name] = key
                self.db_index_data['%s_%s' % (table, name)] = dict()
            
    def insert(self, table, reg):
        with self.lock:
            self.__log('insert', table, 'start')
            if table in self.db_meta:
                reg = self.__gen_auto(self.db_meta[table], reg)
                key = self.__build_key(self.db_meta[table], reg)
                self.db_scraping[table][key] = reg
                # Inserta en índices
                if table in self.db_index_meta:
                    for name ,keys in self.db_index_meta[table].items():
                        self.__index_insert(table, name, keys, reg)
            self.__log('insert', table, 'end')
            return None

    def exists(self, table, reg):
        with self.lock:
            self.__log('exists', table, 'ini')
            if table in self.db_meta and table in self.db_scraping:
                key = self.__build_key(self.db_meta[table], reg)
                return key in self.db_scraping[table]
            self.__log('exists', table, 'ini')
            return False

    def exists_idx(self, table, idx, reg):
        return self.find_idx(table, idx, reg) is not None

    def find_idx(self, table, name, reg):
        with self.lock:
            self.__log('find_idx', table, 'ini')
            if table in self.db_index_meta and name in self.db_index_meta[table]:
                keys = self.db_index_meta[table][name]
                index_keys = { k : {'primary_key': True} for k in  keys }
                idx = self.__build_key(index_keys, reg)
                if idx in self.db_index_data['%s_%s' % (table, name)]:
                    pk = self.db_index_data['%s_%s' % (table, name)][idx]
                    return self.__find(table, {**pk, **reg})
            self.__log('find_idx', table, 'ini')
            return None


    def find(self, table, reg):
        with self.lock:
            return self.__find(table, reg)

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

    def to_dataframe(self, table):
        if table in self.db_scraping:
            df = DataFrame(self.db_scraping[table].values()).reset_index(drop=True)
            return df
        return None

    def from_dataframe(self, table, df_orig, meta={}):
        if table not in self.db_scraping:
            meta = self._DBScraping__build_meta(meta)
            self.db_meta[table] = dict()
            df = df_orig.reset_index(drop=True)
            for c, t in df.dtypes.to_dict().items():
                if c not in ['index']:
                    self.db_meta[table][c] = {'type': self.__map_panda_type(t), 'primary_key': False}
            self.db_meta[table] = {**self.db_meta[table], **meta}
            self.db_scraping[table] = df.transpose().to_dict()
        return None

    def export_to_csv(self, base_dir):
        for table in self.db_scraping.keys():
            print('Exportando %s a csv' % table)
            self.__export_to_csv_table(table, base_dir)

    def db_export_to_sqlite(self, test=False, drop=False):
        engine = None
        if test:
            engine = create_engine('sqlite://',
                    connect_args={'check_same_thread':False},
                    poolclass=StaticPool)
        else:
            engine = create_engine('sqlite:///db.sqlite3')

        conn = engine.connect()
        if drop:
            conn.execute("PRAGMA foreign_keys = OFF")
            self.__db_drop_structure(conn)

        conn.execute("PRAGMA foreign_keys = ON")
        self.__db_create_structure(conn)
        for table in self.db_scraping.keys():
            print('Exportando %s a sql' % table)
            self.__db_export_to_sql_table(conn, table)
        conn.close()

    def __db_create_structure(self, conn):
        for table in self.db_meta.keys():
            self.__db_create_table(conn, table)

    def __db_drop_structure(self, conn):
        for table in self.db_meta.keys():
            self.__db_drop_table(conn, table)

    def __gen_auto(self, meta, reg):
        for k, v in meta.items():
            if 'auto_gen' in v:
                reg[k] = v['auto_gen']
                v['auto_gen'] = v['auto_gen'] + 1
        return reg

    def __find(self, table, reg):
        if table in self.db_meta and table in self.db_scraping:
            key = self.__build_key(self.db_meta[table], reg)
            if key in self.db_scraping[table]:
                return self.db_scraping[table][key]
        return None

    def __build_key(self, meta, reg):
        key = list()
        for k, v in sorted(meta.items()):
            if v['primary_key']:
                key.append('%s_%s' % (k, str(reg[k])))
        return ':'.join(key)

    def __build_meta(self, reg):
        meta = dict()
        for (k, t) in reg.items():
            tmp = {'type': t, 'primary_key': False}
            if re.search('\s*pk\s+', k):
                k = re.sub('(\s*pk\s+)', '', k)
                tmp['primary_key'] = True
            if re.search('\s*auto\s+', k):
                k = re.sub('(\s*auto\s+)', '', k)
                tmp['auto_gen'] = 0
            ref = re.search('\s+ref\s+(\w+)\.(\w+)\s*', k)
            if ref:
                k = re.sub('(\s+ref\s+(\w+)\.(\w+)\s*)', '', k)
                tmp['ref'] = [ref.group(1), ref.group(2)]
            meta[k] = tmp
        return meta

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

    def __index_insert(self, table, index_name, index_keys, reg):
        index_reg = { k : {'primary_key': True} for k in  index_keys }
        idx = self.__build_key(index_reg, reg)
        self.db_index_data['%s_%s' % (table, index_name)][idx] = self.__extract_PK(self.db_meta[table], reg)

    def __extract_PK(self, meta, reg):
        out = dict()
        for k, v in sorted(meta.items()):
            if v['primary_key']:
                out[k] = reg[k]
        return out

    def __build_key(self, meta, reg):
        key = list()
        for k, v in sorted(meta.items()):
            if v['primary_key']:
                key.append('%s_%s' % (k, str(reg[k])))
        return ':'.join(key)

    def __export_to_csv_table(self, table, base_dir):
        if table in self.db_scraping:
            df = DataFrame(self.db_scraping[table].values())
            df.to_csv('%s/%s.csv' % (base_dir, table), index=False)

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
            tp = self.__map_db_type(elem['type'])
            isPk = elem['primary_key']
            ref = elem.get('ref')
            field = '%s %s' % (name, tp)
            if isPk:
                field = '%s PRIMARY KEY' % field
            if ref:
                field = '%s REFERENCES %s(%s)' % (field, ref[0], ref[1])
            fields.append(field)
        conn.execute('create table if not exists %s(%s);' % (table, ','.join(fields)))

    def __map_db_type(self, tp):
        if tp == int:
            return 'integer'
        return 'text'

    def __map_panda_type(self, tp):
        if 'int' in tp.name:
            return int
        return str

    def __map_values(self, table, reg):
        keys = list()
        vals = list()
        for k, v in reg.items():
            keys.append(k)
            if v is None or v != v:
                vals.append("null")
            elif self.db_meta[table][k]['type'] == str:
                vals.append("'%s'" % v.replace("'", "''"))
            elif self.db_meta[table][k]['type'] == datetime:
                vals.append("'%s'" % v)
            else:
                vals.append('%s' % str(v))
        return keys, vals

    def __log(self, oper, table, msg):
        if self.debug:
            print('DBScraping: [%s][%s] - %s' % (table, oper, msg))
